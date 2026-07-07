"""
任务成本计算编排服务（支出成本引擎 - 编排层）

职责（与收入侧 FreightCalcService 对称）：
  - 把 ORM 加载、标准化、规则筛选、逐费用项匹配与持久化串起来
  - 提供三个入口：
      1) preview_for_task     : 试算（不写库），发运前预览"应给司机多少"
      2) calculate_and_persist: 正式计算，写 result + item，回填 task，写异常
      3) recalculate_many     : 批量重算（政策变更 / Worker 调度）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Iterable, Optional

from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.billing.cost_calc_exception import CostCalcException
from app.modules.client.models.billing.cost_policy import CostPolicy
from app.modules.client.models.billing.cost_rule import CostRule
from app.modules.client.models.billing.task_cost_result import (
    TaskCostResult,
    TaskCostResultItem,
)
from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.models.capacity.self_capacity.driver.driver import Driver
from app.modules.client.models.capacity.self_capacity.driver.driver_operation import (
    DriverOperation,
)
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
from app.modules.client.models.capacity.self_capacity.vehicle_ext import VehicleExt
from app.modules.client.models.billing.freight_calc_result import WaybillFreightResult
from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.models.route import Route
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_dispatch_order import TaskDispatchOrder
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.services.billing.conditions import collect_leaf_types
from app.modules.client.services.billing.cost_constants import (
    COST_ENGINE_VERSION,
    ERR_AREA_NOT_RECOGNIZED,
    ERR_POLICY_NOT_FOUND,
    FEE_TYPES,
    PM_PERCENTAGE,
    PM_PER_TON_KM,
    carrier_cost_type_of,
)
from app.modules.client.services.billing.cost_matcher import (
    CostFactContext,
    CostMatcher,
    FeeItemResult,
    VehicleGroup,
)
from app.modules.client.services.billing.standardize_service import (
    REGION_LEVEL_LABEL,
    StandardizeService,
)


@dataclass
class TaskCostSummary:
    task_id: int
    task_version: int
    total_cost_amount: Decimal
    total_addition_amount: Decimal
    total_deduction_amount: Decimal
    calc_status: str  # success/partial/exception/locked
    items: list[FeeItemResult] = field(default_factory=list)
    carrier_type: Optional[int] = None
    payee_type: Optional[int] = None
    payee_id: Optional[int] = None
    payee_name: Optional[str] = None
    error_message: Optional[str] = None
    persisted_result_id: Optional[int] = None


class TaskCostCalcService:

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
    ) -> list[VehicleGroup]:
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

        groups: list[VehicleGroup] = []
        for (brand, model), qty in agg.items():
            v = await StandardizeService.resolve_vehicle(
                db, brand_id=None, series_id=None,
                raw_brand=brand or None, raw_model=model or None,
            )
            groups.append(VehicleGroup(vehicle=v, quantity=qty))
        return groups

    @staticmethod
    async def _resolve_driver_id(db: AsyncSession, task: Task) -> Optional[int]:
        if not task.capacity_id:
            return None
        r = await db.execute(
            select(Capacity.driver_id).where(
                Capacity.id == task.capacity_id, Capacity.is_deleted == 0,
            )
        )
        row = r.first()
        return row[0] if row else None

    @staticmethod
    async def _load_route_distance(
        db: AsyncSession,
        origin_region_id: Optional[int],
        destination_region_id: Optional[int],
    ) -> Optional[Decimal]:
        if not origin_region_id or not destination_region_id:
            return None
        r = await db.execute(
            select(Route.distance).where(
                Route.origin_region_id == origin_region_id,
                Route.destination_region_id == destination_region_id,
                Route.is_deleted == 0,
                Route.distance.is_not(None),
            ).order_by(Route.id.asc()).limit(1)
        )
        row = r.first()
        if row and row[0] is not None:
            return Decimal(str(row[0]))
        return None

    @staticmethod
    async def _load_active_policies(
        db: AsyncSession,
        task: Task,
        driver_id: Optional[int],
        billing_date: date,
    ) -> list[CostPolicy]:
        scope_conds = [
            CostPolicy.scope_type == 0,  # 全局默认
        ]
        if task.carrier_id:
            scope_conds.append(and_(
                CostPolicy.scope_type == 1, CostPolicy.scope_id == task.carrier_id,
            ))
        if driver_id:
            scope_conds.append(and_(
                CostPolicy.scope_type == 2, CostPolicy.scope_id == driver_id,
            ))
        if task.capacity_id:
            scope_conds.append(and_(
                CostPolicy.scope_type == 3, CostPolicy.scope_id == task.capacity_id,
            ))

        r = await db.execute(
            select(CostPolicy).where(
                CostPolicy.status == 1,
                CostPolicy.is_deleted == 0,
                CostPolicy.effective_date <= billing_date,
                or_(
                    CostPolicy.expiry_date.is_(None),
                    CostPolicy.expiry_date >= billing_date,
                ),
                or_(
                    CostPolicy.carrier_type.is_(None),
                    CostPolicy.carrier_type == task.carrier_type,
                ),
                or_(*scope_conds),
            )
        )
        return list(r.scalars().all())

    @staticmethod
    async def _load_active_rules(
        db: AsyncSession, policy_ids: list[int], billing_date: date,
    ) -> list[CostRule]:
        if not policy_ids:
            return []
        r = await db.execute(
            select(CostRule).where(
                CostRule.policy_id.in_(policy_ids),
                CostRule.status == 1,
                CostRule.is_deleted == 0,
            )
        )
        rules = [
            rule for rule in r.scalars().all()
            if (
                (rule.effective_date is None or rule.effective_date <= billing_date)
                and (rule.expiry_date is None or rule.expiry_date >= billing_date)
            )
        ]
        return rules

    @staticmethod
    def _region_ids_in_tree(node: Optional[dict]) -> set[int]:
        """收集条件树里 region_route 叶子引用的行政区 ID（用于层级评分缓存）。"""
        ids: set[int] = set()
        if not node:
            return ids
        if "type" in node:
            if node.get("type") == "region_route":
                for k in ("originRegionId", "origin_region_id",
                          "destinationRegionId", "destination_region_id"):
                    v = node.get(k)
                    if v:
                        ids.add(int(v))
            return ids
        for ch in node.get("children") or []:
            ids |= TaskCostCalcService._region_ids_in_tree(ch)
        return ids

    @staticmethod
    async def _build_region_level_cache(
        db: AsyncSession, rules: list[CostRule]
    ) -> dict[int, str]:
        ids = {r.origin_region_id for r in rules if r.origin_region_id}
        ids |= {r.destination_region_id for r in rules if r.destination_region_id}
        for r in rules:
            if getattr(r, "conditions_json", None):
                ids |= TaskCostCalcService._region_ids_in_tree(r.condition_tree())
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
    async def _hydrate_rules_region_ids(
        db: AsyncSession, rules: list[CostRule]
    ) -> None:
        for rule in rules:
            if rule.origin_region_id is None and (rule.origin_code or rule.origin):
                res = await StandardizeService.resolve_region(
                    db, region_id=None,
                    code=(rule.origin_code or "").strip() or None,
                    raw_name=(rule.origin or "").strip() or None,
                )
                if res.region_id is not None:
                    rule.origin_region_id = res.region_id
            if rule.destination_region_id is None and (
                rule.destination_code or rule.destination
            ):
                res = await StandardizeService.resolve_region(
                    db, region_id=None,
                    code=(rule.destination_code or "").strip() or None,
                    raw_name=(rule.destination or "").strip() or None,
                )
                if res.region_id is not None:
                    rule.destination_region_id = res.region_id

    @staticmethod
    def _detach_rules(db: AsyncSession, rules: list[CostRule]) -> None:
        for rule in rules:
            db.expunge(rule)

    @staticmethod
    async def _load_freight_income(db: AsyncSession, task_id: int) -> Decimal:
        """percentage 计价基数：任务挂接运单的收入侧运费合计（is_active 结果）。"""
        r = await db.execute(
            select(TaskWaybillItem.waybill_id).where(
                TaskWaybillItem.task_id == task_id,
                TaskWaybillItem.is_deleted == 0,
            ).distinct()
        )
        waybill_ids = [row[0] for row in r.all()]
        if not waybill_ids:
            return Decimal("0")
        r2 = await db.execute(
            select(WaybillFreightResult.total_amount).where(
                WaybillFreightResult.waybill_id.in_(waybill_ids),
                WaybillFreightResult.is_active == 1,
                WaybillFreightResult.is_deleted == 0,
            )
        )
        total = Decimal("0")
        for row in r2.all():
            if row[0] is not None:
                total += Decimal(str(row[0]))
        return total

    @staticmethod
    async def _load_dispatch_orders(
        db: AsyncSession, task_id: int
    ) -> list[TaskDispatchOrder]:
        if not task_id:
            return []
        r = await db.execute(
            select(TaskDispatchOrder).where(
                TaskDispatchOrder.task_id == task_id,
                TaskDispatchOrder.is_deleted == 0,
            ).order_by(TaskDispatchOrder.order_no.asc())
        )
        return list(r.scalars().all())

    @staticmethod
    async def _load_driver_facts(
        db: AsyncSession, driver_id: Optional[int]
    ) -> tuple[Optional[Driver], Optional[DriverOperation]]:
        if not driver_id:
            return None, None
        rd = await db.execute(
            select(Driver).where(Driver.id == driver_id, Driver.is_deleted == 0)
        )
        driver = rd.scalar_one_or_none()
        ro = await db.execute(
            select(DriverOperation).where(
                DriverOperation.driver_id == driver_id,
                DriverOperation.is_deleted == 0,
            )
        )
        return driver, ro.scalar_one_or_none()

    @staticmethod
    async def _load_vehicle_facts(
        db: AsyncSession, capacity_id: Optional[int]
    ) -> tuple[Optional[Vehicle], Optional[VehicleExt]]:
        if not capacity_id:
            return None, None
        rc = await db.execute(
            select(Capacity.vehicle_id).where(
                Capacity.id == capacity_id, Capacity.is_deleted == 0,
            )
        )
        row = rc.first()
        vehicle_id = row[0] if row else None
        if not vehicle_id:
            return None, None
        rv = await db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.is_deleted == 0)
        )
        vehicle = rv.scalar_one_or_none()
        re = await db.execute(
            select(VehicleExt).where(
                VehicleExt.vehicle_id == vehicle_id, VehicleExt.is_deleted == 0,
            )
        )
        return vehicle, re.scalar_one_or_none()

    # ---------- 内部：单次计算（不写库） ----------

    @staticmethod
    def _payee_of(task: Task, driver_id: Optional[int]) -> tuple[Optional[int], Optional[int], Optional[str]]:
        """返回 (payee_type, payee_id, payee_name)"""
        if task.carrier_type == 2:
            return 2, task.carrier_id, task.carrier_name or task.carrier_short_name
        if task.carrier_type == 3:
            return 3, task.social_driver_id, task.main_driver_name
        return 1, driver_id, task.main_driver_name

    @staticmethod
    async def _calculate_in_memory(
        db: AsyncSession,
        task: Task,
        billing_date: Optional[date] = None,
        *,
        driver_id_override: Optional[int] = None,
        vehicle_groups_override: Optional[list[VehicleGroup]] = None,
        distance_km_override: Optional[Decimal] = None,
    ) -> TaskCostSummary:
        billing_date = billing_date or (
            task.planned_load_time.date() if task.planned_load_time else date.today()
        )

        if driver_id_override is not None:
            driver_id = driver_id_override
        else:
            driver_id = await TaskCostCalcService._resolve_driver_id(db, task)
        payee_type, payee_id, payee_name = TaskCostCalcService._payee_of(task, driver_id)

        # 标准化：地区
        origin = await StandardizeService.resolve_region(
            db, region_id=task.origin_region_id,
            code=task.origin_code, raw_name=task.origin,
        )
        destination = await StandardizeService.resolve_region(
            db, region_id=task.destination_region_id,
            code=task.destination_code, raw_name=task.destination,
        )

        # 里程：优先使用显式传入（试算），否则查线路库
        if distance_km_override is not None:
            distance_km = distance_km_override
        else:
            distance_km = await TaskCostCalcService._load_route_distance(
                db, origin.region_id, destination.region_id,
            )

        if vehicle_groups_override is not None:
            vehicle_groups = vehicle_groups_override
        elif task.id:
            vehicle_groups = await TaskCostCalcService._load_vehicle_groups(db, task.id)
        else:
            vehicle_groups = []

        base_summary = TaskCostSummary(
            task_id=task.id,
            task_version=1,
            total_cost_amount=Decimal("0"),
            total_addition_amount=Decimal("0"),
            total_deduction_amount=Decimal("0"),
            calc_status="exception",
            carrier_type=task.carrier_type,
            payee_type=payee_type, payee_id=payee_id, payee_name=payee_name,
        )

        # 地区无法识别：整任务异常（但仍允许 per_trip/fixed 等不依赖线路的费用？
        # 与收入侧一致，起终点无法标准化则整体异常）
        if not origin.region_id or not destination.region_id:
            missing = []
            if not origin.region_id:
                missing.append("起点")
            if not destination.region_id:
                missing.append("终点")
            base_summary.error_message = f"无法识别{','.join(missing)}的标准行政区"
            base_summary.items = [FeeItemResult(
                fee_type="__task__", error_type=ERR_AREA_NOT_RECOGNIZED,
                error_message=base_summary.error_message,
            )]
            return base_summary

        # 加载政策 / 规则
        policies = await TaskCostCalcService._load_active_policies(
            db, task, driver_id, billing_date,
        )
        if not policies:
            base_summary.error_message = "该任务无任何生效成本政策"
            base_summary.items = [FeeItemResult(
                fee_type="__task__", error_type=ERR_POLICY_NOT_FOUND,
                error_message=base_summary.error_message,
            )]
            return base_summary

        policy_ids = [p.id for p in policies]
        rules = await TaskCostCalcService._load_active_rules(
            db, policy_ids, billing_date,
        )
        await TaskCostCalcService._hydrate_rules_region_ids(db, rules)
        TaskCostCalcService._detach_rules(db, rules)
        policy_map = {p.id: p for p in policies}
        region_cache = await TaskCostCalcService._build_region_level_cache(db, rules)

        # percentage 基数（仅当存在 percentage 规则时加载）
        freight_income = None
        if any(r.pricing_method == PM_PERCENTAGE for r in rules):
            freight_income = await TaskCostCalcService._load_freight_income(db, task.id)

        # 条件引擎 v2：按"规则集用到的条件类型"决定富事实的按需加载，避免多余 DB 访问
        needed_types: set[str] = set()
        for rule in rules:
            needed_types |= collect_leaf_types(rule.condition_tree())

        dispatch_orders: list[TaskDispatchOrder] = []
        if needed_types & {"dispatch_route", "text_contains", "mileage_range"}:
            dispatch_orders = await TaskCostCalcService._load_dispatch_orders(
                db, task.id,
            )

        driver_obj = driver_op = None
        if "driver_attr" in needed_types:
            driver_obj, driver_op = await TaskCostCalcService._load_driver_facts(
                db, driver_id,
            )

        transport_vehicle = vehicle_ext = None
        need_vehicle = "vehicle_attr" in needed_types
        has_ton_rule = any(r.pricing_method == PM_PER_TON_KM for r in rules)
        if need_vehicle or has_ton_rule:
            transport_vehicle, vehicle_ext = (
                await TaskCostCalcService._load_vehicle_facts(db, task.capacity_id)
            )

        # 吨位：per_ton_km 缺失里程/吨位一直不可用；以运输车辆核定载重兜底
        ton = None
        if has_ton_rule and vehicle_ext is not None and vehicle_ext.load_capacity:
            ton = Decimal(str(vehicle_ext.load_capacity))

        ctx = CostFactContext(
            carrier_type=task.carrier_type,
            transport_date=billing_date,
            origin=origin,
            destination=destination,
            total_quantity=int(task.total_quantity or 0),
            vehicle_groups=vehicle_groups,
            distance_km=distance_km,
            distance_source="biz_route" if distance_km is not None else None,
            ton=ton,
            freight_income=freight_income,
            payee_id=payee_id,
            payee_name=payee_name,
            carrier_id=task.carrier_id,
            capacity_id=task.capacity_id,
            driver_id=driver_id,
            enterprise_id=getattr(task, "enterprise_id", None),
            dispatch_orders=dispatch_orders,
            driver=driver_obj,
            driver_operation=driver_op,
            transport_vehicle=transport_vehicle,
            vehicle_ext=vehicle_ext,
        )

        # 按 fee_type 分组
        rules_by_fee: dict[str, list[CostRule]] = {}
        for rule in rules:
            rules_by_fee.setdefault(rule.fee_type, []).append(rule)

        # 待处理 fee_type = 候选中出现的 + 必算项（driver_freight 等）
        fee_types = set(rules_by_fee.keys())
        for ft in FEE_TYPES:
            if ft["isRequired"]:
                fee_types.add(ft["code"])

        items: list[FeeItemResult] = []
        for ft in sorted(fee_types):
            fee_results = CostMatcher.match_fee_type(
                ft, rules_by_fee.get(ft, []), policy_map, ctx, region_cache,
            )
            items.extend(fee_results)

        addition = sum(
            (it.amount for it in items
             if it.calc_status == "success" and it.direction == 1),
            Decimal("0"),
        )
        deduction = sum(
            (it.amount for it in items
             if it.calc_status == "success" and it.direction == 2),
            Decimal("0"),
        )
        total = addition - deduction

        success_cnt = sum(1 for it in items if it.calc_status == "success")
        exc_cnt = sum(1 for it in items if it.calc_status == "exception")
        if exc_cnt == 0 and success_cnt > 0:
            calc_status = "success"
        elif success_cnt == 0:
            calc_status = "exception"
        else:
            calc_status = "partial"

        base_summary.total_addition_amount = addition
        base_summary.total_deduction_amount = deduction
        base_summary.total_cost_amount = total
        base_summary.calc_status = calc_status
        base_summary.items = items
        return base_summary

    # ---------- 公共入口 ----------

    @staticmethod
    async def preview_for_task(
        db: AsyncSession, task: Task, billing_date: Optional[date] = None,
    ) -> TaskCostSummary:
        """试算（dry_run）：仅返回内存结果，不落库。"""
        return await TaskCostCalcService._calculate_in_memory(db, task, billing_date)

    @staticmethod
    async def preview_adhoc(
        db: AsyncSession,
        *,
        carrier_type: Optional[int] = None,
        capacity_id: Optional[int] = None,
        carrier_id: Optional[int] = None,
        social_driver_id: Optional[int] = None,
        driver_id: Optional[int] = None,
        origin_region_id: Optional[int] = None,
        destination_region_id: Optional[int] = None,
        total_quantity: Optional[int] = None,
        vehicles: Optional[list[dict]] = None,
        distance_km: Optional[Decimal] = None,
        billing_date: Optional[date] = None,
    ) -> TaskCostSummary:
        """散字段试算：不依赖已有任务，用前端传入的要素直接算。"""
        transient = Task(
            carrier_type=carrier_type,
            capacity_id=capacity_id,
            carrier_id=carrier_id,
            social_driver_id=social_driver_id,
            origin_region_id=origin_region_id,
            destination_region_id=destination_region_id,
            total_quantity=int(total_quantity or 0),
        )

        vehicle_groups: list[VehicleGroup] = []
        for v in (vehicles or []):
            resolved = await StandardizeService.resolve_vehicle(
                db,
                brand_id=v.get("brandId"), series_id=v.get("seriesId"),
                raw_brand=v.get("vehicleBrand"), raw_model=v.get("vehicleModel"),
            )
            vehicle_groups.append(VehicleGroup(
                vehicle=resolved, quantity=int(v.get("quantity") or 0),
            ))

        return await TaskCostCalcService._calculate_in_memory(
            db, transient, billing_date,
            driver_id_override=driver_id,
            vehicle_groups_override=vehicle_groups,
            distance_km_override=distance_km,
        )

    @staticmethod
    async def calculate_and_persist(
        db: AsyncSession,
        task_id: int,
        *,
        triggered_by: str = "manual_recalc",
        triggered_user_id: Optional[int] = None,
        billing_date: Optional[date] = None,
    ) -> TaskCostSummary:
        """正式计算并落库：写 result + item，回填 task，写异常表。"""
        task = await TaskCostCalcService._load_task(db, task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        if task.is_locked == 1:
            db.add(CostCalcException(
                task_id=task.id,
                exception_type="TASK_LOCKED",
                exception_message="任务已锁定，跳过重算",
                context_json={"triggered_by": triggered_by},
            ))
            await db.flush()
            return TaskCostSummary(
                task_id=task.id, task_version=1,
                total_cost_amount=task.carrier_cost_amount or Decimal("0"),
                total_addition_amount=Decimal("0"),
                total_deduction_amount=Decimal("0"),
                calc_status="locked",
                error_message="任务已锁定",
            )

        summary = await TaskCostCalcService._calculate_in_memory(
            db, task, billing_date,
        )

        # 上一条结果置为非活跃
        await db.execute(
            update(TaskCostResult)
            .where(
                TaskCostResult.task_id == task_id,
                TaskCostResult.is_active == 1,
                TaskCostResult.is_deleted == 0,
            )
            .values(is_active=0)
        )

        now = datetime.now()
        result = TaskCostResult(
            task_id=task.id,
            task_version=summary.task_version,
            is_active=1,
            carrier_type=summary.carrier_type,
            payee_type=summary.payee_type,
            payee_id=summary.payee_id,
            payee_name=summary.payee_name,
            total_cost_amount=summary.total_cost_amount,
            total_addition_amount=summary.total_addition_amount,
            total_deduction_amount=summary.total_deduction_amount,
            calc_status=summary.calc_status,
            calc_engine_version=COST_ENGINE_VERSION,
            calc_time=now,
            triggered_by=triggered_by,
            triggered_user_id=triggered_user_id,
            error_message=(
                summary.error_message
                if summary.calc_status != "success" else None
            ),
        )
        db.add(result)
        await db.flush()

        primary_pm: Optional[str] = None
        for it in summary.items:
            # 跳过整任务级占位项（fee_type=__task__）的明细写入，仅写异常
            if it.fee_type != "__task__":
                db.add(TaskCostResultItem(
                    result_id=result.id,
                    task_id=task.id,
                    fee_type=it.fee_type,
                    fee_name=it.fee_name,
                    direction=it.direction,
                    payee_type=it.payee_type,
                    pricing_method=it.pricing_method or "",
                    unit_price=it.unit_price,
                    quantity=it.quantity,
                    distance_km=it.distance_km,
                    amount=it.amount,
                    matched_policy_id=it.matched_policy_id,
                    matched_rule_id=it.matched_rule_id,
                    matched_rule_version=it.matched_rule_version,
                    match_score=it.match_score,
                    match_trace_json=it.match_trace,
                    calc_status=it.calc_status,
                    error_type=it.error_type,
                    error_message=it.error_message,
                ))
            if it.error_type:
                db.add(CostCalcException(
                    task_id=task.id,
                    fee_type=None if it.fee_type == "__task__" else it.fee_type,
                    exception_type=it.error_type,
                    exception_message=it.error_message or it.error_type,
                    context_json={
                        "triggered_by": triggered_by,
                        "match_trace": it.match_trace,
                    },
                ))
            if (
                primary_pm is None and it.calc_status == "success"
                and it.fee_type in ("driver_freight", "carrier_freight")
            ):
                primary_pm = it.pricing_method

        # 回填 task（未锁定）
        if summary.calc_status in ("success", "partial"):
            task.carrier_cost_amount = summary.total_cost_amount
            if primary_pm:
                task.carrier_cost_type = carrier_cost_type_of(primary_pm)

        await db.flush()
        summary.persisted_result_id = result.id
        return summary

    # ---------- 受影响任务查找 ----------

    @staticmethod
    def _extract_region_routes(node: Optional[dict]) -> list[dict]:
        """从条件树里收集顶层 AND 语义下的 region_route 叶子（用于粗筛）。

        仅在"树顶层为 AND 且含 region_route"时用于行政区收敛；OR 树或不含
        region_route 时返回空，交由更宽的召回 + 精算兜底。
        """
        if not node:
            return []
        if "type" in node:
            return [node] if node.get("type") == "region_route" else []
        logic = (node.get("logic") or "and").lower()
        if logic != "and":
            return []
        out: list[dict] = []
        for ch in node.get("children") or []:
            if isinstance(ch, dict) and ch.get("type") == "region_route":
                out.append(ch)
        return out

    @staticmethod
    async def find_affected_tasks_for_rule(
        db: AsyncSession, rule: CostRule, *, only_unlocked: bool = True,
    ) -> list[int]:
        """成本规则变更后，粗匹配受影响任务 ID。

        条件树含顶层 region_route 时保留行政区粗筛；否则放宽到未锁定的在办任务，
        由精算阶段兜底（性能权衡：召回优先，避免漏算）。
        """
        conds = [Task.is_deleted == 0, Task.status.notin_((7, 9))]
        if only_unlocked:
            conds.append(Task.is_locked == 0)

        routes = TaskCostCalcService._extract_region_routes(rule.condition_tree())
        route_ors = []
        for rt in routes:
            oid = rt.get("originRegionId") or rt.get("origin_region_id")
            did = rt.get("destinationRegionId") or rt.get("destination_region_id")
            bidir = int(rt.get("bidirectional") or rt.get("is_bidirectional") or 0)
            if not oid or not did:
                continue
            forward = and_(
                Task.origin_region_id == oid,
                Task.destination_region_id == did,
            )
            if bidir == 1:
                route_ors.append(
                    forward
                    | and_(
                        Task.origin_region_id == did,
                        Task.destination_region_id == oid,
                    )
                )
            else:
                route_ors.append(forward)
        if route_ors:
            conds.append(or_(*route_ors))

        r = await db.execute(select(Task.id).where(*conds))
        return [row[0] for row in r.all()]

    @staticmethod
    async def find_affected_tasks_for_policy(
        db: AsyncSession, policy: CostPolicy, *, only_unlocked: bool = True,
    ) -> list[int]:
        """成本政策变更后，按 scope + carrier_type 粗匹配受影响任务。"""
        conds = [Task.is_deleted == 0, Task.status.notin_((7, 9))]
        if only_unlocked:
            conds.append(Task.is_locked == 0)
        if policy.carrier_type is not None:
            conds.append(Task.carrier_type == policy.carrier_type)
        if policy.scope_type == 1 and policy.scope_id:
            conds.append(Task.carrier_id == policy.scope_id)
        elif policy.scope_type == 3 and policy.scope_id:
            conds.append(Task.capacity_id == policy.scope_id)
        # scope_type=2 司机 / scope_type=0 全局：按 carrier_type 粗筛
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
    ) -> list[TaskCostSummary]:
        out: list[TaskCostSummary] = []
        for tid in task_ids:
            try:
                summary = await TaskCostCalcService.calculate_and_persist(
                    db, tid,
                    triggered_by=triggered_by,
                    triggered_user_id=triggered_user_id,
                )
                out.append(summary)
            except Exception as e:  # noqa: BLE001
                out.append(TaskCostSummary(
                    task_id=tid, task_version=0,
                    total_cost_amount=Decimal("0"),
                    total_addition_amount=Decimal("0"),
                    total_deduction_amount=Decimal("0"),
                    calc_status="exception",
                    error_message=str(e),
                ))
        return out
