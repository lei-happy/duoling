"""
运单服务（租户库）
"""

import random
from typing import Optional
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import select, func, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.pinyin_utils import match_pinyin
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.models.vehicle_basic.biz_vehicle_brand import BizVehicleBrand
from app.modules.client.models.vehicle_basic.biz_vehicle_series import BizVehicleSeries
from app.modules.client.schemas.waybill.waybill import (
    WaybillCreate,
    WaybillUpdate,
    WaybillStatusUpdate,
    WaybillOut,
    WaybillCargoLineIn,
    waybill_brand_model_key,
)
from app.modules.client.services.system_config_service import SystemConfigService
from app.modules.client.services.billing.billing_engine_service import BillingEngineService
from app.modules.client.services.billing.standardize_service import StandardizeService
from app.modules.client.services.billing.freight_calc_task_service import (
    FreightCalcTaskService,
    TASK_MANUAL_RECALC,
    TASK_WAYBILL_CHANGED,
)


# 运单"计费敏感字段"（Schema 字段名）：变更时触发重算
WAYBILL_BILLING_SENSITIVE_FIELDS = {
    "customerId", "originCode", "originRegionId",
    "destinationCode", "destinationRegionId",
    "planIssueTime", "requiredLoadTime", "requiredDeliverTime",
}

# Schema 字段名 → ORM 字段名（供敏感字段比对使用）
_SCHEMA_TO_MODEL = {
    "customerId": "customer_id",
    "originCode": "origin_code",
    "originRegionId": "origin_region_id",
    "destinationCode": "destination_code",
    "destinationRegionId": "destination_region_id",
    "planIssueTime": "plan_issue_time",
    "requiredLoadTime": "required_load_time",
    "requiredDeliverTime": "required_deliver_time",
}


class WaybillService:

    @staticmethod
    def _raise_biz_if_duplicate_waybill_no(exc: IntegrityError) -> None:
        msg = str(getattr(exc, "orig", None) or exc).lower()
        if "waybill_no" in msg:
            raise BizException("运单编号已存在，请更换其他编号") from exc
        raise exc

    @staticmethod
    def _generate_waybill_no() -> str:
        now = datetime.now()
        return f"YD{now.strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"

    @staticmethod
    def _validate_cargo_lines(lines: list[WaybillCargoLineIn]) -> None:
        if not lines:
            raise BizException("请至少录入一行货物信息")
        for i, line in enumerate(lines):
            if not (line.vehicleBrand and str(line.vehicleBrand).strip()):
                raise BizException(f"货物第{i + 1}行：请填写商品车品牌")
            if not (line.vehicleModel and str(line.vehicleModel).strip()):
                raise BizException(f"货物第{i + 1}行：请填写车型")

    @staticmethod
    def _ordered_cargoes(lines: list[WaybillCargoLineIn]) -> list[WaybillCargoLineIn]:
        indexed = list(enumerate(lines))
        indexed.sort(key=lambda t: (t[1].sortOrder, t[0]))
        return [t[1] for t in indexed]

    @staticmethod
    def _mirror_main_vehicle_fields(lines: list[WaybillCargoLineIn]) -> tuple[str, str, int]:
        ordered = WaybillService._ordered_cargoes(lines)
        first = ordered[0]
        total_qty = sum(int(x.quantity) for x in ordered)
        return (
            (first.vehicleBrand or "").strip() or None,  # type: ignore
            (first.vehicleModel or "").strip() or None,  # type: ignore
            total_qty,
        )

    @staticmethod
    def _match_waybill_region_filters(
        w: Waybill,
        origin_keyword: Optional[str],
        destination_keyword: Optional[str],
        vehicle_keyword: Optional[str],
    ) -> bool:
        ow = (origin_keyword or "").strip()
        if ow and not match_pinyin(w.origin or "", ow):
            return False
        dk = (destination_keyword or "").strip()
        if dk and not match_pinyin(w.destination or "", dk):
            return False
        vk = (vehicle_keyword or "").strip()
        if vk:
            brand_ok = match_pinyin(w.vehicle_brand or "", vk)
            model_ok = match_pinyin(w.vehicle_model or "", vk)
            if not (brand_ok or model_ok):
                return False
        return True

    @staticmethod
    async def _fetch_cargoes_batch(
        db: AsyncSession, waybill_ids: list[int]
    ) -> dict[int, list[WaybillCargo]]:
        if not waybill_ids:
            return {}
        result = await db.execute(
            select(WaybillCargo).where(
                WaybillCargo.waybill_id.in_(waybill_ids),
                WaybillCargo.is_deleted == 0,
            )
        )
        rows = list(result.scalars().all())
        by_wb: dict[int, list[WaybillCargo]] = {}
        for r in rows:
            by_wb.setdefault(r.waybill_id, []).append(r)
        for wid in by_wb:
            by_wb[wid].sort(key=lambda x: (x.sort_order, x.id))
        return by_wb

    @staticmethod
    async def _series_image_lookup_map(db: AsyncSession) -> dict[str, Optional[str]]:
        """品牌中文名 + 车系名 → 车系图（与运单货物行匹配）。"""
        result = await db.execute(
            select(
                BizVehicleBrand.brand_name_cn,
                BizVehicleSeries.series_name,
                BizVehicleSeries.series_image,
            )
            .select_from(BizVehicleSeries)
            .join(
                BizVehicleBrand,
                BizVehicleBrand.brand_id == BizVehicleSeries.brand_id,
            )
        )
        out: dict[str, Optional[str]] = {}
        for brand_cn, series_name, series_image in result.all():
            if not (brand_cn and series_name):
                continue
            k = waybill_brand_model_key(brand_cn, series_name)
            out[k] = series_image
        return out

    @staticmethod
    async def _fetch_cargoes_for_waybill(
        db: AsyncSession, waybill_id: int
    ) -> list[WaybillCargo]:
        m = await WaybillService._fetch_cargoes_batch(db, [waybill_id])
        return m.get(waybill_id, [])

    @staticmethod
    async def _soft_delete_cargoes(db: AsyncSession, waybill_id: int) -> None:
        await db.execute(
            update(WaybillCargo)
            .where(
                WaybillCargo.waybill_id == waybill_id,
                WaybillCargo.is_deleted == 0,
            )
            .values(is_deleted=1)
        )

    @staticmethod
    async def _insert_cargoes(
        db: AsyncSession,
        waybill_id: int,
        lines: list[WaybillCargoLineIn],
    ) -> None:
        ordered = WaybillService._ordered_cargoes(lines)
        for idx, line in enumerate(ordered):
            db.add(
                WaybillCargo(
                    waybill_id=waybill_id,
                    sort_order=idx,
                    vehicle_brand=(line.vehicleBrand or "").strip() or None,
                    vehicle_model=(line.vehicleModel or "").strip() or None,
                    quantity=line.quantity,
                )
            )

    @staticmethod
    async def _replace_cargoes(
        db: AsyncSession, waybill_id: int, lines: list[WaybillCargoLineIn]
    ) -> None:
        WaybillService._validate_cargo_lines(lines)
        await WaybillService._soft_delete_cargoes(db, waybill_id)
        await WaybillService._insert_cargoes(db, waybill_id, lines)

    @staticmethod
    async def _hydrate_waybill_create_region_ids(
        db: AsyncSession, data: WaybillCreate,
    ) -> WaybillCreate:
        """创建运单时 origin/destination_region_id 为空则用编码或名称补全。"""
        update: dict = {}
        if data.originRegionId is None and (data.originCode or data.origin):
            oc = (data.originCode or "").strip() or None
            r = await StandardizeService.resolve_region(
                db, region_id=None, code=oc, raw_name=data.origin,
            )
            if r.region_id is not None:
                update["originRegionId"] = r.region_id
                if not oc and r.region_code:
                    update["originCode"] = r.region_code
        if data.destinationRegionId is None and (data.destinationCode or data.destination):
            dc = (data.destinationCode or "").strip() or None
            r = await StandardizeService.resolve_region(
                db, region_id=None, code=dc, raw_name=data.destination,
            )
            if r.region_id is not None:
                update["destinationRegionId"] = r.region_id
                if not dc and r.region_code:
                    update["destinationCode"] = r.region_code
        if not update:
            return data
        return data.model_copy(update=update)

    @staticmethod
    async def _hydrate_waybill_row_region_ids(db: AsyncSession, waybill: Waybill) -> None:
        """已落库运单若 region_id 为空，用当前编码/名称补全（编辑、导入、历史数据自愈）。"""
        if waybill.origin_region_id is None and (waybill.origin_code or waybill.origin):
            oc = (waybill.origin_code or "").strip() or None
            r = await StandardizeService.resolve_region(
                db, region_id=None, code=oc, raw_name=waybill.origin,
            )
            if r.region_id is not None:
                waybill.origin_region_id = r.region_id
                if not (waybill.origin_code or "").strip() and r.region_code:
                    waybill.origin_code = r.region_code
        if (
            waybill.destination_region_id is None
            and (waybill.destination_code or waybill.destination)
        ):
            dc = (waybill.destination_code or "").strip() or None
            r = await StandardizeService.resolve_region(
                db, region_id=None, code=dc, raw_name=waybill.destination,
            )
            if r.region_id is not None:
                waybill.destination_region_id = r.region_id
                if not (waybill.destination_code or "").strip() and r.region_code:
                    waybill.destination_code = r.region_code

    @staticmethod
    async def _resolve_auto_freight(
        db: AsyncSession,
        calc_mode: str,
        customer_id: Optional[int],
        origin_code: Optional[str],
        destination_code: Optional[str],
        lines: list[WaybillCargoLineIn],
    ) -> tuple[Optional[Decimal], Optional[int], Optional[int]]:
        """
        多行分别计价后汇总金额。
        contract_id / rate_id：仅记录首个成功匹配行（多行可能对应不同运价，勿用于强业务约束）。
        """
        if calc_mode not in ("auto_required", "auto_preferred"):
            return None, None, None
        if not (customer_id and origin_code and destination_code):
            return None, None, None

        ordered = WaybillService._ordered_cargoes(lines)
        total = Decimal("0")
        first_contract_id: Optional[int] = None
        first_rate_id: Optional[int] = None
        any_hit = False

        for line in ordered:
            hit = await BillingEngineService.calculate_freight(
                db,
                customer_id=customer_id,
                origin_code=origin_code,
                destination_code=destination_code,
                vehicle_brand=line.vehicleBrand,
                vehicle_model=line.vehicleModel,
                quantity=line.quantity,
            )
            if hit:
                total += hit.totalAmount
                any_hit = True
                if first_contract_id is None:
                    first_contract_id = hit.contractId
                    first_rate_id = hit.rateId
            elif calc_mode == "auto_required":
                raise BizException("存在货物行未匹配到运价，无法保存运单")

        if not any_hit:
            return None, None, None
        return total, first_contract_id, first_rate_id

    @staticmethod
    async def page_waybills(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        customer_id: Optional[int] = None,
        status: Optional[int] = None,
        origin_keyword: Optional[str] = None,
        destination_keyword: Optional[str] = None,
        vehicle_keyword: Optional[str] = None,
        created_at_start: Optional[date] = None,
        created_at_end: Optional[date] = None,
    ) -> dict:
        list_show_raw = await SystemConfigService.get_by_key(
            db, "waybill.list_show_freight_amount"
        )
        show_freight_in_list = (list_show_raw or "").strip().lower() == "true"
        redact_freight_amount = not show_freight_in_list

        use_pinyin_filters = any(
            [
                (origin_keyword or "").strip(),
                (destination_keyword or "").strip(),
                (vehicle_keyword or "").strip(),
            ]
        )

        base = select(Waybill).where(Waybill.is_deleted == 0)

        if keyword:
            base = base.where(Waybill.waybill_no.contains(keyword))
        if customer_id is not None:
            base = base.where(Waybill.customer_id == customer_id)
        if status is not None:
            base = base.where(Waybill.status == status)
        if created_at_start is not None:
            start_dt = datetime.combine(created_at_start, time.min)
            base = base.where(Waybill.created_at >= start_dt)
        if created_at_end is not None:
            end_dt = datetime.combine(created_at_end, time.max)
            base = base.where(Waybill.created_at <= end_dt)

        if use_pinyin_filters:
            stmt = base.order_by(Waybill.created_at.desc(), Waybill.id.desc())
            result = await db.execute(stmt)
            rows = list(result.scalars().all())
            filtered = [
                w
                for w in rows
                if WaybillService._match_waybill_region_filters(
                    w, origin_keyword, destination_keyword, vehicle_keyword
                )
            ]
            total = len(filtered)
            offset = (page - 1) * page_size
            page_items = filtered[offset : offset + page_size]
            wb_ids = [w.id for w in page_items]
            cargo_map = await WaybillService._fetch_cargoes_batch(db, wb_ids)
            series_lookup = await WaybillService._series_image_lookup_map(db)
            return {
                "list": [
                    WaybillOut.from_model(
                        item,
                        cargo_map.get(item.id, []),
                        series_image_lookup=series_lookup,
                        redact_freight_amount=redact_freight_amount,
                    ).model_dump()
                    for item in page_items
                ],
                "count": total,
                "total": total,
                "page": page,
                "page_size": page_size,
            }

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(Waybill.created_at.desc(), Waybill.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()
        wb_ids = [w.id for w in items]
        cargo_map = await WaybillService._fetch_cargoes_batch(db, wb_ids)
        series_lookup = await WaybillService._series_image_lookup_map(db)

        return {
            "list": [
                WaybillOut.from_model(
                    item,
                    cargo_map.get(item.id, []),
                    series_image_lookup=series_lookup,
                    redact_freight_amount=redact_freight_amount,
                ).model_dump()
                for item in items
            ],
            "count": total,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def waybill_to_out(db: AsyncSession, waybill: Waybill) -> WaybillOut:
        cargoes = await WaybillService._fetch_cargoes_for_waybill(db, waybill.id)
        series_lookup = await WaybillService._series_image_lookup_map(db)
        return WaybillOut.from_model(
            waybill, cargoes, series_image_lookup=series_lookup
        )

    @staticmethod
    async def waybill_no_exists(
        db: AsyncSession,
        waybill_no: str,
        exclude_waybill_id: Optional[int] = None,
    ) -> bool:
        """是否存在相同运单号（未删除）。排除指定 id 用于编辑场景。"""
        raw = (waybill_no or "").strip()
        if not raw:
            return False
        q = select(Waybill.id).where(
            Waybill.waybill_no == raw,
            Waybill.is_deleted == 0,
        )
        if exclude_waybill_id is not None:
            q = q.where(Waybill.id != exclude_waybill_id)
        result = await db.execute(q.limit(1))
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_waybill(db: AsyncSession, waybill_id: int) -> Waybill:
        result = await db.execute(
            select(Waybill).where(
                Waybill.id == waybill_id,
                Waybill.is_deleted == 0,
            )
        )
        waybill = result.scalar_one_or_none()
        if not waybill:
            raise BizException("运单不存在")
        return waybill

    @staticmethod
    async def create_waybill(
        db: AsyncSession, data: WaybillCreate, current_user_id: int
    ) -> tuple[Waybill, list[WaybillCargo]]:
        data = await WaybillService._hydrate_waybill_create_region_ids(db, data)
        waybill_no = data.waybillNo or WaybillService._generate_waybill_no()
        WaybillService._validate_cargo_lines(data.cargoes)

        brand_mirr, model_mirr, qty_sum = WaybillService._mirror_main_vehicle_fields(
            data.cargoes
        )

        freight_amount: Optional[Decimal] = None
        freight_source: Optional[int] = None
        contract_id: Optional[int] = None
        rate_id: Optional[int] = None

        calc_mode = await SystemConfigService.get_by_key(db, "waybill.freight_calc_mode")
        if not calc_mode:
            calc_mode = "manual_only"

        auto_total, auto_cid, auto_rid = await WaybillService._resolve_auto_freight(
            db,
            calc_mode,
            data.customerId,
            data.originCode,
            data.destinationCode,
            data.cargoes,
        )
        if auto_total is not None:
            freight_amount = auto_total
            freight_source = 0
            contract_id = auto_cid
            rate_id = auto_rid

        if freight_amount is None:
            if data.freightAmount is not None:
                freight_amount = Decimal(str(data.freightAmount))
                freight_source = 1
            elif calc_mode == "auto_required":
                raise BizException("未匹配到运价，无法创建运单")

        waybill = Waybill(
            waybill_no=waybill_no,
            customer_id=data.customerId,
            customer_name=data.customerName,
            origin=data.origin,
            origin_code=data.originCode,
            origin_region_id=getattr(data, "originRegionId", None),
            destination=data.destination,
            destination_code=data.destinationCode,
            destination_region_id=getattr(data, "destinationRegionId", None),
            vehicle_brand=brand_mirr,
            vehicle_model=model_mirr,
            quantity=qty_sum,
            plan_issue_time=data.planIssueTime,
            required_load_time=data.requiredLoadTime,
            required_deliver_time=data.requiredDeliverTime,
            dealer_name=data.dealerName,
            dealer_contact=data.dealerContact,
            dealer_phone=data.dealerPhone,
            dealer_address=data.dealerAddress,
            freight_amount=freight_amount,
            freight_source=freight_source,
            contract_id=contract_id,
            rate_id=rate_id,
            remark=data.remark,
            status=0,
            calc_status="pending",
            is_locked=0,
            waybill_version=1,
            created_by=current_user_id,
        )
        db.add(waybill)
        try:
            await db.flush()
        except IntegrityError as exc:
            await db.rollback()
            WaybillService._raise_biz_if_duplicate_waybill_no(exc)
        await WaybillService._insert_cargoes(db, waybill.id, data.cargoes)
        await db.flush()
        # 写一条计算任务，由 worker 异步落正式 result + match_trace 留痕
        try:
            await FreightCalcTaskService.enqueue_waybill_recalc(
                db, waybill.id,
                task_type=TASK_WAYBILL_CHANGED,
                priority=10,
                triggered_by_user_id=current_user_id,
            )
        except Exception:
            pass
        cargoes = await WaybillService._fetch_cargoes_for_waybill(db, waybill.id)
        await db.refresh(waybill)
        return waybill, cargoes

    @staticmethod
    async def update_waybill(
        db: AsyncSession, waybill_id: int, data: WaybillUpdate,
        *, current_user_id: Optional[int] = None,
    ) -> tuple[Waybill, list[WaybillCargo]]:
        result = await db.execute(
            select(Waybill).where(
                Waybill.id == waybill_id,
                Waybill.is_deleted == 0,
            )
        )
        waybill = result.scalar_one_or_none()
        if not waybill:
            raise BizException("运单不存在")

        if waybill.is_locked == 1:
            raise BizException("运单已锁定（已结算/已开票），不允许修改")

        # 计费敏感字段变更判定
        billing_field_changed = False

        def _sensitive_changed(schema_field: str, new_val) -> bool:
            if schema_field not in WAYBILL_BILLING_SENSITIVE_FIELDS:
                return False
            if new_val is None:
                return False
            old_val = getattr(waybill, _SCHEMA_TO_MODEL.get(schema_field, ""), None)
            return old_val != new_val

        field_map = {
            "customerId": "customer_id",
            "customerName": "customer_name",
            "origin": "origin",
            "originCode": "origin_code",
            "originRegionId": "origin_region_id",
            "destination": "destination",
            "destinationCode": "destination_code",
            "destinationRegionId": "destination_region_id",
            "vehicleBrand": "vehicle_brand",
            "vehicleModel": "vehicle_model",
            "quantity": "quantity",
            "planIssueTime": "plan_issue_time",
            "requiredLoadTime": "required_load_time",
            "requiredDeliverTime": "required_deliver_time",
            "dealerName": "dealer_name",
            "dealerContact": "dealer_contact",
            "dealerPhone": "dealer_phone",
            "dealerAddress": "dealer_address",
            "freightAmount": "freight_amount",
            "remark": "remark",
        }
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                if _sensitive_changed(schema_field, val):
                    billing_field_changed = True
                setattr(waybill, model_field, val)

        if data.cargoes is not None:
            WaybillService._validate_cargo_lines(data.cargoes)
            old_cargoes = await WaybillService._fetch_cargoes_for_waybill(db, waybill_id)
            if WaybillService._cargoes_changed(old_cargoes, data.cargoes):
                billing_field_changed = True
            await WaybillService._replace_cargoes(db, waybill_id, data.cargoes)
            b, m, q = WaybillService._mirror_main_vehicle_fields(data.cargoes)
            waybill.vehicle_brand = b
            waybill.vehicle_model = m
            waybill.quantity = q

        await WaybillService._hydrate_waybill_row_region_ids(db, waybill)

        if billing_field_changed:
            waybill.waybill_version = (waybill.waybill_version or 1) + 1
            waybill.calc_status = "pending"

        await db.flush()

        if billing_field_changed:
            try:
                await FreightCalcTaskService.enqueue_waybill_recalc(
                    db, waybill.id,
                    task_type=TASK_WAYBILL_CHANGED,
                    priority=10,
                    triggered_by_user_id=current_user_id,
                )
            except Exception:
                pass

        cargoes = await WaybillService._fetch_cargoes_for_waybill(db, waybill_id)
        await db.refresh(waybill)
        return waybill, cargoes

    @staticmethod
    def _cargoes_changed(
        old: list[WaybillCargo], new: list[WaybillCargoLineIn]
    ) -> bool:
        old_keys = sorted([
            (waybill_brand_model_key(c.vehicle_brand, c.vehicle_model),
             int(c.quantity or 0))
            for c in old
        ])
        new_keys = sorted([
            (waybill_brand_model_key(c.vehicleBrand, c.vehicleModel),
             int(c.quantity or 0))
            for c in new
        ])
        return old_keys != new_keys

    # ---- 手动重算入口 ----

    @staticmethod
    async def request_recalc(
        db: AsyncSession, waybill_id: int, *, current_user_id: Optional[int] = None,
    ) -> int:
        """手动触发重算：写一条高优先级 task。返回 task.id。"""
        waybill = await WaybillService.get_waybill(db, waybill_id)
        if waybill.is_locked == 1:
            raise BizException("运单已锁定，禁止自动重算；请先解锁")
        waybill.calc_status = "pending"
        await db.flush()
        task = await FreightCalcTaskService.enqueue_waybill_recalc(
            db, waybill_id,
            task_type=TASK_MANUAL_RECALC,
            priority=20,
            triggered_by_user_id=current_user_id,
        )
        return task.id

    @staticmethod
    async def update_status(
        db: AsyncSession, waybill_id: int, data: WaybillStatusUpdate
    ) -> Waybill:
        result = await db.execute(
            select(Waybill).where(
                Waybill.id == waybill_id,
                Waybill.is_deleted == 0,
            )
        )
        waybill = result.scalar_one_or_none()
        if not waybill:
            raise BizException("运单不存在")

        waybill.status = data.status
        await db.flush()
        await db.refresh(waybill)
        return waybill

    @staticmethod
    async def delete_waybill(db: AsyncSession, waybill_id: int) -> None:
        result = await db.execute(
            select(Waybill).where(
                Waybill.id == waybill_id,
                Waybill.is_deleted == 0,
            )
        )
        waybill = result.scalar_one_or_none()
        if not waybill:
            raise BizException("运单不存在")
        if waybill.status not in (0, 1, 6):
            raise BizException("仅待确认、已确认或已取消的运单可以删除")
        waybill.is_deleted = 1
        await WaybillService._soft_delete_cargoes(db, waybill_id)
        await db.flush()
