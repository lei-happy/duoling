"""
车辆资产 - 续期台账 / 资产卡片 / 成本汇总（二期）

资产成本独立汇总，不写入任务支出成本引擎。
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.maintenance.renewal import FleetRenewal
from app.modules.client.models.capacity.maintenance.work_order import FleetWorkOrder
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
from app.modules.client.models.capacity.self_capacity.vehicle_ext import VehicleExt
from app.modules.client.models.compliance.compliance_alert import BizComplianceAlert
from app.modules.client.schemas.capacity.maintenance import (
    AssetCardOut,
    AssetCardUpdate,
    RenewalCreate,
    RenewalOut,
    RenewalUpdate,
)

RENEWAL_TYPES = {"insurance", "inspection"}
RENEWAL_STATUSES = {"draft", "effective", "cancelled"}
_DOC_TYPE_MAP = {"insurance": "insurance", "inspection": "inspection"}
_ZERO = Decimal("0")
_CENT = Decimal("0.01")


def _d(v: Any) -> Optional[Decimal]:
    if v is None:
        return None
    return Decimal(str(v)).quantize(_CENT, rounding=ROUND_HALF_UP)


def _money(v: Optional[Decimal]) -> Decimal:
    return (v or _ZERO).quantize(_CENT, rounding=ROUND_HALF_UP)


def _month_start(d: date) -> date:
    return date(d.year, d.month, 1)


def _add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    last = monthrange(y, m)[1]
    return date(y, m, min(d.day, last))


def _months_inclusive(start: date, end: date) -> int:
    """从 start 所在月到 end 所在月的应计月数（含首尾月）。"""
    if end < start:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month) + 1


class FleetAssetCostService:

    # ---------- 序列化 ----------

    @staticmethod
    def _renewal_out(row: FleetRenewal) -> dict[str, Any]:
        return RenewalOut(
            id=row.id,
            vehicleId=row.vehicle_id,
            plateNumber=row.plate_number,
            renewalType=row.renewal_type,
            effectiveDate=row.effective_date,
            expireDate=row.expire_date,
            amount=row.amount,
            policyNo=row.policy_no,
            attachmentUrl=row.attachment_url,
            status=row.status,
            effectiveAt=row.effective_at,
            remark=row.remark,
            createdAt=row.created_at,
            updatedAt=row.updated_at,
        ).model_dump(mode="json")

    @staticmethod
    def _calc_depreciation(
        *,
        original: Optional[Decimal],
        residual: Optional[Decimal],
        months: Optional[int],
        start: Optional[date],
        as_of: Optional[date] = None,
        range_from: Optional[date] = None,
        range_to: Optional[date] = None,
    ) -> tuple[Optional[Decimal], Optional[Decimal], Optional[Decimal], Decimal]:
        """返回 (月折旧, 累计折旧, 净值, 区间折旧)。"""
        if not original or not months or months <= 0 or not start:
            return None, None, None, _ZERO
        resid = residual if residual is not None else _ZERO
        base = max(original - resid, _ZERO)
        monthly = (base / Decimal(months)).quantize(_CENT, rounding=ROUND_HALF_UP)
        as_of = as_of or date.today()
        elapsed = min(_months_inclusive(start, as_of), months)
        accumulated = min(monthly * elapsed, base).quantize(
            _CENT, rounding=ROUND_HALF_UP
        )
        net = (original - accumulated).quantize(_CENT, rounding=ROUND_HALF_UP)

        period = _ZERO
        if range_from and range_to and range_to >= range_from:
            # 区间内应计：与折旧起算月的交集月数
            win_start = max(_month_start(start), _month_start(range_from))
            win_end = _month_start(range_to)
            end_cap = _add_months(_month_start(start), months - 1)
            win_end = min(win_end, end_cap)
            if win_end >= win_start:
                n = _months_inclusive(win_start, win_end)
                # 累计不超过剩余可折旧额（以区间起点前已计提为准）
                before = min(
                    _months_inclusive(start, _add_months(win_start, -1)),
                    months,
                ) if win_start > _month_start(start) else 0
                remain = max(base - monthly * before, _ZERO)
                period = min(monthly * n, remain).quantize(
                    _CENT, rounding=ROUND_HALF_UP
                )
        return monthly, accumulated, net, period

    # ---------- 车辆 ----------

    @staticmethod
    async def _get_vehicle(db: AsyncSession, vehicle_id: int) -> Vehicle:
        result = await db.execute(
            select(Vehicle).where(
                Vehicle.id == vehicle_id,
                Vehicle.is_deleted == 0,
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            raise BizException("未找到该车辆，请确认后重试")
        return row

    @staticmethod
    async def _get_or_create_ext(
        db: AsyncSession, vehicle_id: int
    ) -> VehicleExt:
        result = await db.execute(
            select(VehicleExt).where(
                VehicleExt.vehicle_id == vehicle_id,
                VehicleExt.is_deleted == 0,
            )
        )
        ext = result.scalar_one_or_none()
        if ext:
            return ext
        ext = VehicleExt(vehicle_id=vehicle_id)
        db.add(ext)
        await db.flush()
        return ext

    # ---------- 续期台账 ----------

    @staticmethod
    async def page_renewals(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        renewal_type: Optional[str] = None,
        status: Optional[str] = None,
        vehicle_id: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        conditions = [FleetRenewal.is_deleted == 0]
        if renewal_type:
            conditions.append(FleetRenewal.renewal_type == renewal_type)
        if status:
            conditions.append(FleetRenewal.status == status)
        if vehicle_id:
            conditions.append(FleetRenewal.vehicle_id == vehicle_id)
        if keyword:
            like = f"%{keyword.strip()}%"
            conditions.append(
                or_(
                    FleetRenewal.plate_number.like(like),
                    FleetRenewal.policy_no.like(like),
                )
            )

        total = (
            await db.execute(
                select(func.count())
                .select_from(FleetRenewal)
                .where(*conditions)
            )
        ).scalar() or 0

        rows = (
            await db.execute(
                select(FleetRenewal)
                .where(*conditions)
                .order_by(FleetRenewal.effective_date.desc(), FleetRenewal.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()

        return {
            "list": [FleetAssetCostService._renewal_out(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def create_renewal(
        db: AsyncSession,
        body: RenewalCreate,
        operator_user_id: int,
    ) -> dict:
        if body.renewalType not in RENEWAL_TYPES:
            raise BizException("请选择保险或年检续期类型")
        if body.expireDate < body.effectiveDate:
            raise BizException("新到期日不能早于生效日")

        vehicle = await FleetAssetCostService._get_vehicle(db, body.vehicleId)
        row = FleetRenewal(
            vehicle_id=vehicle.id,
            plate_number=vehicle.plate_number,
            renewal_type=body.renewalType,
            effective_date=body.effectiveDate,
            expire_date=body.expireDate,
            amount=body.amount,
            policy_no=body.policyNo,
            attachment_url=body.attachmentUrl,
            remark=body.remark,
            status="draft",
            created_by=operator_user_id,
        )
        db.add(row)
        await db.flush()
        await db.refresh(row)

        if body.effectNow:
            return await FleetAssetCostService.effect_renewal(
                db, row.id, operator_user_id
            )
        return FleetAssetCostService._renewal_out(row)

    @staticmethod
    async def update_renewal(
        db: AsyncSession, renewal_id: int, body: RenewalUpdate
    ) -> dict:
        row = await FleetAssetCostService._get_renewal(db, renewal_id)
        if row.status != "draft":
            raise BizException("仅草稿状态的续期记录可编辑")
        data = body.model_dump(exclude_unset=True)
        mapping = {
            "effectiveDate": "effective_date",
            "expireDate": "expire_date",
            "amount": "amount",
            "policyNo": "policy_no",
            "attachmentUrl": "attachment_url",
            "remark": "remark",
        }
        for k, col in mapping.items():
            if k in data:
                setattr(row, col, data[k])
        if row.expire_date < row.effective_date:
            raise BizException("新到期日不能早于生效日")
        await db.flush()
        await db.refresh(row)
        return FleetAssetCostService._renewal_out(row)

    @staticmethod
    async def _get_renewal(db: AsyncSession, renewal_id: int) -> FleetRenewal:
        result = await db.execute(
            select(FleetRenewal).where(
                FleetRenewal.id == renewal_id,
                FleetRenewal.is_deleted == 0,
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            raise BizException("未找到该续期记录，请刷新后重试")
        return row

    @staticmethod
    async def effect_renewal(
        db: AsyncSession, renewal_id: int, operator_user_id: int
    ) -> dict:
        row = await FleetAssetCostService._get_renewal(db, renewal_id)
        if row.status == "effective":
            return FleetAssetCostService._renewal_out(row)
        if row.status == "cancelled":
            raise BizException("已取消的续期记录不能再生效")

        ext = await FleetAssetCostService._get_or_create_ext(db, row.vehicle_id)
        if row.renewal_type == "insurance":
            ext.insurance_expire = row.expire_date
        else:
            ext.inspection_expire = row.expire_date

        row.status = "effective"
        row.effective_at = datetime.now()
        await db.flush()

        doc_type = _DOC_TYPE_MAP[row.renewal_type]
        await db.execute(
            update(BizComplianceAlert)
            .where(
                BizComplianceAlert.is_deleted == 0,
                BizComplianceAlert.status == "open",
                BizComplianceAlert.subject_type == "vehicle",
                BizComplianceAlert.subject_id == row.vehicle_id,
                BizComplianceAlert.doc_type == doc_type,
            )
            .values(status="resolved")
        )
        await db.flush()
        await db.refresh(row)
        return FleetAssetCostService._renewal_out(row)

    @staticmethod
    async def cancel_renewal(
        db: AsyncSession, renewal_id: int, operator_user_id: int
    ) -> dict:
        row = await FleetAssetCostService._get_renewal(db, renewal_id)
        if row.status == "cancelled":
            return FleetAssetCostService._renewal_out(row)
        if row.status == "effective":
            raise BizException(
                "已生效的续期记录不能取消；如需更正请再登记一笔新续期"
            )
        row.status = "cancelled"
        await db.flush()
        await db.refresh(row)
        return FleetAssetCostService._renewal_out(row)

    # ---------- 资产卡片 ----------

    @staticmethod
    async def get_asset_card(db: AsyncSession, vehicle_id: int) -> dict:
        vehicle = await FleetAssetCostService._get_vehicle(db, vehicle_id)
        ext = await FleetAssetCostService._get_or_create_ext(db, vehicle_id)
        monthly, accumulated, net, _ = FleetAssetCostService._calc_depreciation(
            original=_d(ext.original_value),
            residual=_d(ext.residual_value),
            months=ext.depreciable_months,
            start=ext.depreciation_start_date or ext.purchase_date,
        )
        return AssetCardOut(
            vehicleId=vehicle.id,
            plateNumber=vehicle.plate_number,
            purchaseDate=ext.purchase_date,
            originalValue=_d(ext.original_value),
            residualValue=_d(ext.residual_value),
            depreciableMonths=ext.depreciable_months,
            depreciationMethod=ext.depreciation_method or "straight_line",
            depreciationStartDate=ext.depreciation_start_date,
            insuranceExpire=ext.insurance_expire,
            inspectionExpire=ext.inspection_expire,
            monthlyDepreciation=monthly,
            accumulatedDepreciation=accumulated,
            netValue=net,
        ).model_dump(mode="json")

    @staticmethod
    async def update_asset_card(
        db: AsyncSession, vehicle_id: int, body: AssetCardUpdate
    ) -> dict:
        await FleetAssetCostService._get_vehicle(db, vehicle_id)
        ext = await FleetAssetCostService._get_or_create_ext(db, vehicle_id)
        data = body.model_dump(exclude_unset=True)

        if "depreciationMethod" in data and data["depreciationMethod"]:
            if data["depreciationMethod"] != "straight_line":
                raise BizException("当前仅支持直线法折旧")

        if "depreciableMonths" in data and data["depreciableMonths"] is not None:
            if data["depreciableMonths"] <= 0:
                raise BizException("折旧月数需大于 0")

        mapping = {
            "purchaseDate": "purchase_date",
            "originalValue": "original_value",
            "residualValue": "residual_value",
            "depreciableMonths": "depreciable_months",
            "depreciationMethod": "depreciation_method",
            "depreciationStartDate": "depreciation_start_date",
        }
        for k, col in mapping.items():
            if k in data:
                val = data[k]
                if k in ("originalValue", "residualValue") and val is not None:
                    val = float(val)
                setattr(ext, col, val)

        if ext.depreciation_method is None:
            ext.depreciation_method = "straight_line"
        await db.flush()
        return await FleetAssetCostService.get_asset_card(db, vehicle_id)

    # ---------- 成本汇总 ----------

    @staticmethod
    async def cost_summary(
        db: AsyncSession,
        *,
        date_from: date,
        date_to: date,
        vehicle_id: Optional[int] = None,
    ) -> dict:
        if date_to < date_from:
            raise BizException("结束日期不能早于开始日期")

        # 维保：完工日在区间内
        wo_conds = [
            FleetWorkOrder.is_deleted == 0,
            FleetWorkOrder.status == "completed",
            FleetWorkOrder.finished_at.is_not(None),
            func.date(FleetWorkOrder.finished_at) >= date_from,
            func.date(FleetWorkOrder.finished_at) <= date_to,
        ]
        if vehicle_id:
            wo_conds.append(FleetWorkOrder.vehicle_id == vehicle_id)
        wo_rows = (
            await db.execute(select(FleetWorkOrder).where(*wo_conds))
        ).scalars().all()

        # 续期：生效日在区间内
        rn_conds = [
            FleetRenewal.is_deleted == 0,
            FleetRenewal.status == "effective",
            FleetRenewal.effective_date >= date_from,
            FleetRenewal.effective_date <= date_to,
        ]
        if vehicle_id:
            rn_conds.append(FleetRenewal.vehicle_id == vehicle_id)
        rn_rows = (
            await db.execute(select(FleetRenewal).where(*rn_conds))
        ).scalars().all()

        # 折旧：有资产卡片的车辆
        veh_q = (
            select(Vehicle, VehicleExt)
            .join(VehicleExt, VehicleExt.vehicle_id == Vehicle.id)
            .where(
                Vehicle.is_deleted == 0,
                VehicleExt.is_deleted == 0,
                VehicleExt.original_value.is_not(None),
                VehicleExt.depreciable_months.is_not(None),
            )
        )
        if vehicle_id:
            veh_q = veh_q.where(Vehicle.id == vehicle_id)
        veh_rows = (await db.execute(veh_q)).all()

        by_vehicle: dict[int, dict[str, Any]] = {}

        def _bucket(vid: int, plate: str) -> dict:
            if vid not in by_vehicle:
                by_vehicle[vid] = {
                    "vehicleId": vid,
                    "plateNumber": plate,
                    "maintenance": _ZERO,
                    "insurance": _ZERO,
                    "inspection": _ZERO,
                    "depreciation": _ZERO,
                    "total": _ZERO,
                }
            return by_vehicle[vid]

        for wo in wo_rows:
            b = _bucket(wo.vehicle_id, wo.plate_number)
            b["maintenance"] += _money(wo.cost_amount)

        for rn in rn_rows:
            b = _bucket(rn.vehicle_id, rn.plate_number)
            key = "insurance" if rn.renewal_type == "insurance" else "inspection"
            b[key] += _money(rn.amount)

        for vehicle, ext in veh_rows:
            _, _, _, period = FleetAssetCostService._calc_depreciation(
                original=_d(ext.original_value),
                residual=_d(ext.residual_value),
                months=ext.depreciable_months,
                start=ext.depreciation_start_date or ext.purchase_date,
                range_from=date_from,
                range_to=date_to,
            )
            if period > 0:
                b = _bucket(vehicle.id, vehicle.plate_number)
                b["depreciation"] += period

        items = []
        totals = {
            "maintenance": _ZERO,
            "insurance": _ZERO,
            "inspection": _ZERO,
            "depreciation": _ZERO,
            "total": _ZERO,
        }
        for b in by_vehicle.values():
            b["total"] = (
                b["maintenance"]
                + b["insurance"]
                + b["inspection"]
                + b["depreciation"]
            )
            for k in totals:
                totals[k] += b[k]
            items.append(
                {
                    **b,
                    "maintenance": float(b["maintenance"]),
                    "insurance": float(b["insurance"]),
                    "inspection": float(b["inspection"]),
                    "depreciation": float(b["depreciation"]),
                    "total": float(b["total"]),
                }
            )
        items.sort(key=lambda x: x["total"], reverse=True)

        return {
            "dateFrom": date_from.isoformat(),
            "dateTo": date_to.isoformat(),
            "totals": {k: float(v) for k, v in totals.items()},
            "vehicles": items,
            "disclaimer": "本页为经营视角的资产成本汇总，不等于会计总账。",
        }

    @staticmethod
    async def cost_details(
        db: AsyncSession,
        *,
        date_from: date,
        date_to: date,
        vehicle_id: Optional[int] = None,
        cost_type: Optional[str] = None,
    ) -> dict:
        summary = await FleetAssetCostService.cost_summary(
            db,
            date_from=date_from,
            date_to=date_to,
            vehicle_id=vehicle_id,
        )
        details: list[dict] = []

        if cost_type in (None, "maintenance"):
            wo_conds = [
                FleetWorkOrder.is_deleted == 0,
                FleetWorkOrder.status == "completed",
                FleetWorkOrder.finished_at.is_not(None),
                func.date(FleetWorkOrder.finished_at) >= date_from,
                func.date(FleetWorkOrder.finished_at) <= date_to,
            ]
            if vehicle_id:
                wo_conds.append(FleetWorkOrder.vehicle_id == vehicle_id)
            for wo in (
                await db.execute(select(FleetWorkOrder).where(*wo_conds))
            ).scalars().all():
                details.append(
                    {
                        "costType": "maintenance",
                        "vehicleId": wo.vehicle_id,
                        "plateNumber": wo.plate_number,
                        "occurDate": wo.finished_at.date().isoformat()
                        if wo.finished_at
                        else None,
                        "amount": float(_money(wo.cost_amount)),
                        "refType": "work_order",
                        "refId": wo.id,
                        "title": wo.title,
                        "refNo": wo.work_order_no,
                    }
                )

        if cost_type in (None, "insurance", "inspection"):
            rn_conds = [
                FleetRenewal.is_deleted == 0,
                FleetRenewal.status == "effective",
                FleetRenewal.effective_date >= date_from,
                FleetRenewal.effective_date <= date_to,
            ]
            if vehicle_id:
                rn_conds.append(FleetRenewal.vehicle_id == vehicle_id)
            if cost_type in ("insurance", "inspection"):
                rn_conds.append(FleetRenewal.renewal_type == cost_type)
            for rn in (
                await db.execute(select(FleetRenewal).where(*rn_conds))
            ).scalars().all():
                details.append(
                    {
                        "costType": rn.renewal_type,
                        "vehicleId": rn.vehicle_id,
                        "plateNumber": rn.plate_number,
                        "occurDate": rn.effective_date.isoformat(),
                        "amount": float(_money(rn.amount)),
                        "refType": "renewal",
                        "refId": rn.id,
                        "title": "保险续期"
                        if rn.renewal_type == "insurance"
                        else "年检续期",
                        "refNo": rn.policy_no,
                    }
                )

        if cost_type in (None, "depreciation"):
            for v in summary["vehicles"]:
                if v["depreciation"] > 0 and (
                    not vehicle_id or v["vehicleId"] == vehicle_id
                ):
                    details.append(
                        {
                            "costType": "depreciation",
                            "vehicleId": v["vehicleId"],
                            "plateNumber": v["plateNumber"],
                            "occurDate": f"{date_from.isoformat()}~{date_to.isoformat()}",
                            "amount": v["depreciation"],
                            "refType": "asset_card",
                            "refId": v["vehicleId"],
                            "title": "直线法折旧",
                            "refNo": None,
                        }
                    )

        details.sort(key=lambda x: (x.get("occurDate") or "", x["costType"]))
        return {
            "dateFrom": date_from.isoformat(),
            "dateTo": date_to.isoformat(),
            "list": details,
            "total": sum(d["amount"] for d in details),
            "disclaimer": summary["disclaimer"],
        }
