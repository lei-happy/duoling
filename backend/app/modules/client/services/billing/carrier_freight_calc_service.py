"""
承运商运费计算编排服务（承运运费引擎 - 编排层）

职责（与客户收入侧 FreightCalcService 对称，粒度为「任务」）：
  - 把 ORM 加载、标准化、合同/规则筛选、逐车型分组匹配与持久化串起来
  - 提供三个入口：
      1) preview_for_task     : 试算（不写库），派车前预览"该给承运商多少运费"
      2) calculate_and_persist: 正式计算，写 result + detail，回填 task，写异常
      3) recalculate_many     : 批量重算（合同/规则变更、Worker 调度）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Iterable, Optional

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.billing.carrier_contract import CarrierContract
from app.modules.client.models.billing.carrier_freight_calc_exception import (
    CarrierFreightCalcException,
)
from app.modules.client.models.billing.carrier_freight_result import (
    CarrierFreightResult,
    CarrierFreightResultDetail,
)
from app.modules.client.models.billing.carrier_rate import CarrierRate
from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.services.billing.carrier_freight_matcher import (
    CARRIER_ENGINE_VERSION,
    CarrierContext,
    CarrierFreightMatcher,
    GroupMatchResult,
    VehicleGroupInput,
)
from app.modules.client.services.billing.standardize_service import (
    REGION_LEVEL_LABEL,
    StandardizeService,
    vehicle_alias_key,
)


# 承运成本类型映射（回填 task.carrier_cost_type）：1-包车 2-按台 3-按吨公里 4-其他
def _carrier_cost_type_of(billing_mode: Optional[int]) -> int:
    if billing_mode == 2:
        return 1   # 整单价 → 包车
    if billing_mode == 0:
        return 2   # 台单价 → 按台
    return 4       # 单公里单价等 → 其他


@dataclass
class CarrierFreightSummary:
    task_id: int
    task_version: int
    total_amount: Decimal
    calc_status: str  # success/partial/exception/locked
    groups: list[GroupMatchResult] = field(default_factory=list)
    carrier_id: Optional[int] = None
    carrier_name: Optional[str] = None
    matched_contract_id: Optional[int] = None
    error_message: Optional[str] = None
    persisted_result_id: Optional[int] = None


class CarrierFreightCalcService:

    # ---------- 数据加载 ----------

    @staticmethod
    async def _load_task(db: AsyncSession, task_id: int) -> Optional[Task]:
        r = await db.execute(
            select(Task).where(Task.id == task_id, Task.is_deleted == 0)
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def _load_vehicle_groups(
        db: AsyncSession, task_id: int
    ) -> list[VehicleGroupInput]:
        """按车型（品牌+型号）聚合任务挂接的商品车并标准化。"""
        r = await db.execute(
            select(TaskWaybillItem).where(
                TaskWaybillItem.task_id == task_id,
                TaskWaybillItem.is_deleted == 0,
            )
        )
        items = list(r.scalars().all())
        agg: dict[tuple, int] = {}
        for it in items:
            key = (it.vehicle_brand or "", it.vehicle_model or "")
            agg[key] = agg.get(key, 0) + int(it.quantity or 0)

        groups: list[VehicleGroupInput] = []
        for (brand, model), qty in agg.items():
            v = await StandardizeService.resolve_vehicle(
                db, brand_id=None, series_id=None,
                raw_brand=brand or None, raw_model=model or None,
            )
            groups.append(VehicleGroupInput(
                quantity=qty, vehicle=v, group_key=vehicle_alias_key(brand, model),
            ))
        return groups

    @staticmethod
    async def _load_active_contracts(
        db: AsyncSession, carrier_id: int, billing_date: date
    ) -> list[CarrierContract]:
        r = await db.execute(
            select(CarrierContract).where(
                CarrierContract.carrier_id == carrier_id,
                CarrierContract.status == 1,
                CarrierContract.is_deleted == 0,
                CarrierContract.effective_date <= billing_date,
                CarrierContract.expiry_date >= billing_date,
            )
        )
        return list(r.scalars().all())

    @staticmethod
    async def _load_active_rules(
        db: AsyncSession,
        carrier_id: int,
        contract_ids: list[int],
        billing_date: date,
    ) -> list[CarrierRate]:
        if not contract_ids:
            return []
        r = await db.execute(
            select(CarrierRate).where(
                CarrierRate.contract_id.in_(contract_ids),
                CarrierRate.carrier_id == carrier_id,
                CarrierRate.status == 1,
                CarrierRate.is_deleted == 0,
            )
        )
        return [
            r0 for r0 in r.scalars().all()
            if (
                (r0.effective_date is None or r0.effective_date <= billing_date)
                and (r0.expiry_date is None or r0.expiry_date >= billing_date)
            )
        ]

    @staticmethod
    async def _build_region_level_cache(
        db: AsyncSession, rules: list[CarrierRate]
    ) -> dict[int, str]:
        ids = {r.origin_region_id for r in rules if r.origin_region_id}
        ids |= {r.destination_region_id for r in rules if r.destination_region_id}
        if not ids:
            return {}
        r = await db.execute(
            select(BizRegion).where(
                BizRegion.id.in_(ids), BizRegion.is_deleted == 0,
            )
        )
        return {
            row.id: REGION_LEVEL_LABEL.get(row.level, "custom")
            for row in r.scalars().all()
        }

    @staticmethod
    async def _hydrate_rules_region_ids_from_codes(
        db: AsyncSession, rules: list[CarrierRate],
    ) -> None:
        """规则表 origin/destination_region_id 为空时，用国标码或名称反查 biz_region.id。

        仅填充内存中的 ORM 属性，供匹配使用；调用方应对 rule 做 expunge，避免 flush 误写回库。
        """
        for rule in rules:
            if rule.origin_region_id is None:
                oc = (rule.origin_code or "").strip() or None
                on = (rule.origin or "").strip() or None
                if oc or on:
                    res = await StandardizeService.resolve_region(
                        db, region_id=None, code=oc, raw_name=on,
                    )
                    if res.region_id is not None:
                        rule.origin_region_id = res.region_id
            if rule.destination_region_id is None:
                dc = (rule.destination_code or "").strip() or None
                dn = (rule.destination or "").strip() or None
                if dc or dn:
                    res = await StandardizeService.resolve_region(
                        db, region_id=None, code=dc, raw_name=dn,
                    )
                    if res.region_id is not None:
                        rule.destination_region_id = res.region_id

    @staticmethod
    def _detach_rules(db: AsyncSession, rules: list[CarrierRate]) -> None:
        for rule in rules:
            db.expunge(rule)

    # ---------- 内部：单次计算（不写库） ----------

    @staticmethod
    async def _calculate_in_memory(
        db: AsyncSession,
        task: Task,
        billing_date: Optional[date] = None,
        *,
        vehicle_groups_override: Optional[list[VehicleGroupInput]] = None,
    ) -> CarrierFreightSummary:
        billing_date = billing_date or (
            task.planned_load_time.date() if task.planned_load_time else date.today()
        )
        carrier_name = task.carrier_name or task.carrier_short_name
        base_summary = CarrierFreightSummary(
            task_id=task.id or 0,
            task_version=1,
            total_amount=Decimal("0"),
            calc_status="exception",
            carrier_id=task.carrier_id,
            carrier_name=carrier_name,
        )

        # 缺少承运商：无法定位承运商合同
        if not task.carrier_id:
            base_summary.error_message = "任务缺少承运商，无法计算承运运费"
            base_summary.groups = [GroupMatchResult(
                group_key="__task__", quantity=0,
                error_type="CARRIER_MISSING",
                error_message=base_summary.error_message,
            )]
            return base_summary

        # 标准化：地区
        origin = await StandardizeService.resolve_region(
            db, region_id=task.origin_region_id,
            code=task.origin_code, raw_name=task.origin,
        )
        destination = await StandardizeService.resolve_region(
            db, region_id=task.destination_region_id,
            code=task.destination_code, raw_name=task.destination,
        )
        ctx = CarrierContext(
            carrier_id=task.carrier_id,
            transport_date=billing_date,
            origin=origin,
            destination=destination,
        )

        # 车型分组
        if vehicle_groups_override is not None:
            groups = vehicle_groups_override
        elif task.id:
            groups = await CarrierFreightCalcService._load_vehicle_groups(db, task.id)
        else:
            groups = []
        if not groups:
            # 无明细：以任务总台数作为通用车型一组
            groups = [VehicleGroupInput(
                quantity=int(task.total_quantity or 0),
                vehicle=(await StandardizeService.resolve_vehicle(db)),
                group_key="__all__",
            )]

        # 加载合同/规则
        contracts = await CarrierFreightCalcService._load_active_contracts(
            db, task.carrier_id, billing_date,
        )
        if not contracts:
            base_summary.error_message = "承运商在该运输日期无生效合同"
            base_summary.groups = [GroupMatchResult(
                group_key=g.group_key, quantity=g.quantity,
                brand_id=g.vehicle.brand_id, series_id=g.vehicle.series_id,
                vehicle_brand=g.vehicle.brand_name, vehicle_model=g.vehicle.series_name,
                error_type="CONTRACT_NOT_FOUND",
                error_message="承运商在该运输日期无生效合同",
            ) for g in groups]
            return base_summary

        rules = await CarrierFreightCalcService._load_active_rules(
            db, task.carrier_id, [c.id for c in contracts], billing_date,
        )
        await CarrierFreightCalcService._hydrate_rules_region_ids_from_codes(db, rules)
        CarrierFreightCalcService._detach_rules(db, rules)
        contract_map = {c.id: c for c in contracts}
        region_cache = await CarrierFreightCalcService._build_region_level_cache(db, rules)

        results = [
            CarrierFreightMatcher.match_one_group(
                ctx=ctx, group=g, candidate_rules=rules,
                contract_map=contract_map, region_level_cache=region_cache,
            )
            for g in groups
        ]

        # 整单价（billing_mode=2）：多分组命中同一规则时按 quantity 分摊，避免重复加总
        CarrierFreightCalcService._reallocate_whole_trip_amount(results)

        total = sum((r.amount for r in results if r.calc_status == "success"),
                    Decimal("0"))
        success_cnt = sum(1 for r in results if r.calc_status == "success")
        if success_cnt == len(results) and results:
            calc_status = "success"
        elif success_cnt == 0:
            calc_status = "exception"
        else:
            calc_status = "partial"

        first_hit = next(
            (r for r in results if r.calc_status == "success" and r.matched_contract),
            None,
        )
        base_summary.total_amount = total
        base_summary.calc_status = calc_status
        base_summary.groups = results
        base_summary.matched_contract_id = (
            first_hit.matched_contract.id if first_hit else None
        )
        if calc_status != "success":
            base_summary.error_message = "存在异常明细，详见 result_detail"
        return base_summary

    @staticmethod
    def _reallocate_whole_trip_amount(results: list[GroupMatchResult]) -> None:
        """整单价规则的金额按 quantity 分摊；同一 rule_id 只算一次。"""
        groups: dict[int, list[GroupMatchResult]] = {}
        for r in results:
            if (
                r.calc_status == "success"
                and r.matched_rule is not None
                and r.billing_mode == 2
            ):
                groups.setdefault(r.matched_rule.id, []).append(r)

        for items in groups.values():
            if len(items) <= 1:
                continue
            unit_price = items[0].matched_rule.unit_price or Decimal("0")
            min_amount = items[0].matched_rule.min_amount
            base = unit_price
            if min_amount is not None and base < min_amount:
                base = min_amount
            qtys = [max(int(it.quantity or 0), 0) for it in items]
            total_qty = sum(qtys) or len(items)
            allocated = Decimal("0")
            shares: list[Decimal] = []
            for q in qtys[:-1]:
                share = (base * Decimal(q) / Decimal(total_qty)).quantize(Decimal("0.01"))
                shares.append(share)
                allocated += share
            shares.append((base - allocated).quantize(Decimal("0.01")))
            for it, share in zip(items, shares):
                it.amount = share

    # ---------- 公共入口 ----------

    @staticmethod
    async def preview_for_task(
        db: AsyncSession, task: Task, billing_date: Optional[date] = None,
    ) -> CarrierFreightSummary:
        """试算（dry_run）：仅返回内存结果，不落库。"""
        return await CarrierFreightCalcService._calculate_in_memory(
            db, task, billing_date,
        )

    @staticmethod
    async def preview_adhoc(
        db: AsyncSession,
        *,
        carrier_id: Optional[int] = None,
        origin_region_id: Optional[int] = None,
        destination_region_id: Optional[int] = None,
        total_quantity: Optional[int] = None,
        vehicles: Optional[list[dict]] = None,
        billing_date: Optional[date] = None,
    ) -> CarrierFreightSummary:
        """散字段试算：不依赖已有任务，用前端传入的要素直接算。"""
        transient = Task(
            carrier_type=2,
            carrier_id=carrier_id,
            origin_region_id=origin_region_id,
            destination_region_id=destination_region_id,
            total_quantity=int(total_quantity or 0),
        )
        vehicle_groups: list[VehicleGroupInput] = []
        for v in (vehicles or []):
            resolved = await StandardizeService.resolve_vehicle(
                db,
                brand_id=v.get("brandId"), series_id=v.get("seriesId"),
                raw_brand=v.get("vehicleBrand"), raw_model=v.get("vehicleModel"),
            )
            vehicle_groups.append(VehicleGroupInput(
                quantity=int(v.get("quantity") or 0), vehicle=resolved,
                group_key=vehicle_alias_key(v.get("vehicleBrand"), v.get("vehicleModel")),
            ))
        return await CarrierFreightCalcService._calculate_in_memory(
            db, transient, billing_date,
            vehicle_groups_override=vehicle_groups or None,
        )

    @staticmethod
    async def calculate_and_persist(
        db: AsyncSession,
        task_id: int,
        *,
        triggered_by: str = "manual_recalc",
        triggered_user_id: Optional[int] = None,
        billing_date: Optional[date] = None,
    ) -> CarrierFreightSummary:
        """正式计算并落库：写 result + detail，回填 task，写异常表。"""
        task = await CarrierFreightCalcService._load_task(db, task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        if task.is_locked == 1:
            db.add(CarrierFreightCalcException(
                task_id=task.id,
                carrier_id=task.carrier_id,
                exception_type="TASK_LOCKED",
                exception_message="任务已锁定，跳过重算",
                context_json={"triggered_by": triggered_by},
            ))
            await db.flush()
            return CarrierFreightSummary(
                task_id=task.id, task_version=1,
                total_amount=task.carrier_cost_amount or Decimal("0"),
                calc_status="locked",
                error_message="任务已锁定",
            )

        summary = await CarrierFreightCalcService._calculate_in_memory(
            db, task, billing_date,
        )

        # 上一条结果置为非活跃
        await db.execute(
            update(CarrierFreightResult)
            .where(
                CarrierFreightResult.task_id == task_id,
                CarrierFreightResult.is_active == 1,
                CarrierFreightResult.is_deleted == 0,
            )
            .values(is_active=0)
        )

        now = datetime.now()
        result = CarrierFreightResult(
            task_id=task.id,
            task_version=summary.task_version,
            is_active=1,
            carrier_id=summary.carrier_id,
            carrier_name=summary.carrier_name,
            total_amount=summary.total_amount,
            calc_status=summary.calc_status,
            calc_engine_version=CARRIER_ENGINE_VERSION,
            calc_time=now,
            triggered_by=triggered_by,
            triggered_user_id=triggered_user_id,
            matched_contract_id=summary.matched_contract_id,
            error_message=(
                summary.error_message if summary.calc_status != "success" else None
            ),
        )
        db.add(result)
        await db.flush()

        primary_mode: Optional[int] = None
        for gr in summary.groups:
            if gr.group_key not in ("__task__",):
                db.add(CarrierFreightResultDetail(
                    result_id=result.id,
                    task_id=task.id,
                    brand_id=gr.brand_id,
                    series_id=gr.series_id,
                    vehicle_brand=gr.vehicle_brand,
                    vehicle_model=gr.vehicle_model,
                    quantity=int(gr.quantity or 0),
                    matched_contract_id=(
                        gr.matched_contract.id if gr.matched_contract else None
                    ),
                    matched_rule_id=gr.matched_rule.id if gr.matched_rule else None,
                    matched_rule_version=(
                        gr.matched_rule.rule_version if gr.matched_rule else None
                    ),
                    origin_match_region_id=gr.origin_match_region_id,
                    origin_match_level=gr.origin_match_level,
                    destination_match_region_id=gr.destination_match_region_id,
                    destination_match_level=gr.destination_match_level,
                    direction=gr.direction,
                    model_match_type=gr.model_match_type,
                    unit_price=gr.unit_price,
                    billing_mode=gr.billing_mode,
                    distance_km=gr.distance_km,
                    amount=gr.amount,
                    match_score=gr.score,
                    match_trace_json=gr.match_trace,
                    calc_status=gr.calc_status,
                    error_type=gr.error_type,
                    error_message=gr.error_message,
                ))
            if gr.error_type:
                db.add(CarrierFreightCalcException(
                    task_id=task.id,
                    carrier_id=task.carrier_id,
                    exception_type=gr.error_type,
                    exception_message=gr.error_message or gr.error_type,
                    context_json={
                        "triggered_by": triggered_by,
                        "match_trace": gr.match_trace,
                    },
                ))
            if primary_mode is None and gr.calc_status == "success":
                primary_mode = gr.billing_mode

        # 回填 task（未锁定）
        if summary.calc_status in ("success", "partial"):
            task.carrier_cost_amount = summary.total_amount
            if primary_mode is not None:
                task.carrier_cost_type = _carrier_cost_type_of(primary_mode)

        await db.flush()
        summary.persisted_result_id = result.id
        return summary

    # ---------- 受影响任务查找 ----------

    @staticmethod
    async def find_affected_tasks_for_rule(
        db: AsyncSession, rule: CarrierRate, *, only_unlocked: bool = True,
    ) -> list[int]:
        """承运价规则变更后，粗匹配受影响任务 ID（承运商 + 线路 + 未锁定在办）。"""
        conds = [
            Task.carrier_type == 2,
            Task.carrier_id == rule.carrier_id,
            Task.is_deleted == 0,
            Task.status.notin_((7, 9)),
        ]
        if only_unlocked:
            conds.append(Task.is_locked == 0)

        if rule.origin_region_id and rule.destination_region_id:
            if rule.is_bidirectional == 1:
                line_cond = (
                    and_(
                        Task.origin_region_id == rule.origin_region_id,
                        Task.destination_region_id == rule.destination_region_id,
                    )
                    | and_(
                        Task.origin_region_id == rule.destination_region_id,
                        Task.destination_region_id == rule.origin_region_id,
                    )
                )
            else:
                line_cond = and_(
                    Task.origin_region_id == rule.origin_region_id,
                    Task.destination_region_id == rule.destination_region_id,
                )
            conds.append(line_cond)

        r = await db.execute(select(Task.id).where(*conds))
        return [row[0] for row in r.all()]

    @staticmethod
    async def find_affected_tasks_for_contract(
        db: AsyncSession, contract: CarrierContract, *, only_unlocked: bool = True,
    ) -> list[int]:
        """合同变更后，按承运商范围扫描受影响任务。"""
        conds = [
            Task.carrier_type == 2,
            Task.carrier_id == contract.carrier_id,
            Task.is_deleted == 0,
            Task.status.notin_((7, 9)),
        ]
        if only_unlocked:
            conds.append(Task.is_locked == 0)
        r = await db.execute(select(Task.id).where(*conds))
        return [row[0] for row in r.all()]

    # ---------- 批量重算 ----------

    @staticmethod
    async def recalculate_many(
        db: AsyncSession,
        task_ids: Iterable[int],
        *,
        triggered_by: str,
        triggered_user_id: Optional[int] = None,
    ) -> list[CarrierFreightSummary]:
        out: list[CarrierFreightSummary] = []
        for tid in task_ids:
            try:
                summary = await CarrierFreightCalcService.calculate_and_persist(
                    db, tid,
                    triggered_by=triggered_by,
                    triggered_user_id=triggered_user_id,
                )
                out.append(summary)
            except Exception as e:  # noqa: BLE001
                out.append(CarrierFreightSummary(
                    task_id=tid, task_version=0,
                    total_amount=Decimal("0"),
                    calc_status="exception",
                    error_message=str(e),
                ))
        return out
