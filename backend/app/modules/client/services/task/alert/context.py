"""
任务预警求值上下文

引擎判定一张任务是否命中规则时，需要的事实远不止 ``biz_task`` 本表：客户要求时间
在运单上、客户类型在客户表、品牌车系在挂接行、里程在调令、运力状态在运力表。

本模块负责把这些事实**批量**预取并装配成 :class:`TaskAlertContext`，
让引擎的判定过程变成纯内存计算 —— 一轮扫描几千张任务只走十来条 SQL，
而不是每张任务各查一遍。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.models.partner.customer import Customer
from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_dispatch_order import TaskDispatchOrder
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo

# 运力运营状态：1-可接单 2-运输中 3-休假 4-停运 5-维修保养
CAPACITY_STATUS_UNAVAILABLE = (3, 4, 5)
CAPACITY_STATUS_LABELS: dict[int, str] = {
    1: "可接单", 2: "运输中", 3: "休假", 4: "停运", 5: "维修保养",
}

# 挂接行状态：0-待装车 1-已装车 2-已卸车 3-已交车 9-已取消
ITEM_STATUS_CANCELLED = 9
ITEM_STATUS_LOADED_OR_BEYOND = (1, 2, 3)


@dataclass
class TaskAlertContext:
    """单张任务的预警求值上下文（全部字段已在内存，判定不再访问 DB）"""

    task_id: int
    task_no: Optional[str]
    stage: int

    stage_entered_at: Optional[datetime] = None
    planned_load_time: Optional[datetime] = None
    planned_arrive_time: Optional[datetime] = None
    actual_load_time: Optional[datetime] = None
    actual_arrive_time: Optional[datetime] = None

    carrier_type: Optional[int] = None
    capacity_id: Optional[int] = None
    capacity_operation_status: Optional[int] = None

    origin: Optional[str] = None
    destination: Optional[str] = None
    origin_region_chain: tuple[int, ...] = ()
    destination_region_chain: tuple[int, ...] = ()

    total_quantity: int = 0
    loaded_quantity: int = 0
    dispatch_order_count: int = 0

    customer_ids: frozenset[int] = frozenset()
    customer_names: tuple[str, ...] = ()
    customer_types: frozenset[int] = frozenset()
    brand_ids: frozenset[int] = frozenset()
    series_ids: frozenset[int] = frozenset()

    required_load_time: Optional[datetime] = None
    required_deliver_time: Optional[datetime] = None

    mileage: Optional[Decimal] = None

    def snapshot(self) -> dict:
        """触发时的上下文快照，落进 biz_task_alert.snapshot_json。

        阈值改动之后，历史预警只能靠这份快照解释「当时为什么报」。
        """
        return {
            "stage": self.stage,
            "customers": list(self.customer_names)[:5],
            "customerTypes": sorted(self.customer_types),
            "origin": self.origin,
            "destination": self.destination,
            "totalQuantity": self.total_quantity,
            "loadedQuantity": self.loaded_quantity,
            "carrierType": self.carrier_type,
            "mileage": float(self.mileage) if self.mileage is not None else None,
            "plannedLoadTime": _iso(self.planned_load_time),
            "plannedArriveTime": _iso(self.planned_arrive_time),
            "requiredLoadTime": _iso(self.required_load_time),
            "requiredDeliverTime": _iso(self.required_deliver_time),
        }


def _iso(v: Optional[datetime]) -> Optional[str]:
    return v.strftime("%Y-%m-%d %H:%M:%S") if v else None


def _earliest(a: Optional[datetime], b: Optional[datetime]) -> Optional[datetime]:
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)


class RegionChainResolver:
    """行政区上溯链解析（区县 → 市 → 省），整表一次性载入内存。

    行政区是低频变更的主数据，一轮扫描内复用同一份快照即可；
    逐个任务递归查父级会把扫描变成 N+1 灾难。
    """

    def __init__(self) -> None:
        self._parent_of_code: dict[str, Optional[str]] = {}
        self._id_by_code: dict[str, int] = {}
        self._code_by_id: dict[int, str] = {}
        self._cache: dict[int, tuple[int, ...]] = {}
        self._loaded = False

    async def load(self, db: AsyncSession) -> None:
        if self._loaded:
            return
        r = await db.execute(
            select(BizRegion.id, BizRegion.code, BizRegion.parent_code)
            .where(BizRegion.is_deleted == 0)
        )
        for rid, code, parent_code in r.all():
            self._id_by_code[code] = int(rid)
            self._code_by_id[int(rid)] = code
            self._parent_of_code[code] = parent_code
        self._loaded = True

    def chain(self, region_id: Optional[int]) -> tuple[int, ...]:
        """返回 [自身, 父级, 祖父级 ...] 的 region_id 列表。"""
        if not region_id:
            return ()
        cached = self._cache.get(int(region_id))
        if cached is not None:
            return cached
        out: list[int] = []
        code = self._code_by_id.get(int(region_id))
        seen: set[str] = set()
        while code and code not in seen:
            seen.add(code)
            rid = self._id_by_code.get(code)
            if rid:
                out.append(rid)
            code = self._parent_of_code.get(code)
        result = tuple(out)
        self._cache[int(region_id)] = result
        return result


class TaskAlertContextLoader:
    """批量装配 TaskAlertContext"""

    def __init__(self, region_resolver: Optional[RegionChainResolver] = None) -> None:
        self._regions = region_resolver or RegionChainResolver()

    async def load(
        self, db: AsyncSession, tasks: list[Task]
    ) -> dict[int, TaskAlertContext]:
        if not tasks:
            return {}
        await self._regions.load(db)
        task_ids = [int(t.id) for t in tasks]

        item_facts = await self._load_item_facts(db, task_ids)
        required_times = await self._load_required_times(db, task_ids)
        customer_types = await self._load_customer_types(
            db, {cid for f in item_facts.values() for cid in f["customer_ids"]}
        )
        mileage = await self._load_mileage(db, task_ids)
        order_counts = await self._load_dispatch_order_counts(db, task_ids)
        capacity_status = await self._load_capacity_status(
            db, {int(t.capacity_id) for t in tasks if t.capacity_id}
        )

        out: dict[int, TaskAlertContext] = {}
        for t in tasks:
            tid = int(t.id)
            facts = item_facts.get(tid, _empty_item_facts())
            cust_ids = facts["customer_ids"]
            req = required_times.get(tid, (None, None))
            out[tid] = TaskAlertContext(
                task_id=tid,
                task_no=t.task_no,
                stage=int(t.status),
                stage_entered_at=t.stage_entered_at,
                planned_load_time=t.planned_load_time,
                planned_arrive_time=t.planned_arrive_time,
                actual_load_time=t.actual_load_time,
                actual_arrive_time=t.actual_arrive_time,
                carrier_type=int(t.carrier_type) if t.carrier_type is not None else None,
                capacity_id=int(t.capacity_id) if t.capacity_id else None,
                capacity_operation_status=(
                    capacity_status.get(int(t.capacity_id)) if t.capacity_id else None
                ),
                origin=t.origin,
                destination=t.destination,
                origin_region_chain=self._regions.chain(t.origin_region_id),
                destination_region_chain=self._regions.chain(t.destination_region_id),
                total_quantity=int(t.total_quantity or 0),
                loaded_quantity=facts["loaded_quantity"],
                dispatch_order_count=order_counts.get(tid, 0),
                customer_ids=frozenset(cust_ids),
                customer_names=tuple(facts["customer_names"]),
                customer_types=frozenset(
                    customer_types[cid] for cid in cust_ids if cid in customer_types
                ),
                brand_ids=frozenset(facts["brand_ids"]),
                series_ids=frozenset(facts["series_ids"]),
                required_load_time=req[0],
                required_deliver_time=req[1],
                mileage=mileage.get(tid),
            )
        return out

    # ---------- 批量预取 ----------

    async def _load_item_facts(
        self, db: AsyncSession, task_ids: list[int]
    ) -> dict[int, dict]:
        """挂接行聚合：客户、已装台数；品牌/车系走 cargo 表补齐标准 ID。"""
        out: dict[int, dict] = {tid: _empty_item_facts() for tid in task_ids}
        r = await db.execute(
            select(
                TaskWaybillItem.task_id,
                TaskWaybillItem.customer_id,
                TaskWaybillItem.customer_name,
                TaskWaybillItem.quantity,
                TaskWaybillItem.status,
                WaybillCargo.brand_id,
                WaybillCargo.series_id,
            )
            .outerjoin(
                WaybillCargo, WaybillCargo.id == TaskWaybillItem.waybill_cargo_id
            )
            .where(
                TaskWaybillItem.task_id.in_(task_ids),
                TaskWaybillItem.is_deleted == 0,
                TaskWaybillItem.status != ITEM_STATUS_CANCELLED,
            )
        )
        for tid, cust_id, cust_name, qty, st, brand_id, series_id in r.all():
            facts = out.setdefault(int(tid), _empty_item_facts())
            if cust_id:
                facts["customer_ids"].add(int(cust_id))
            if cust_name and cust_name not in facts["customer_names"]:
                facts["customer_names"].append(cust_name)
            if brand_id:
                facts["brand_ids"].add(int(brand_id))
            if series_id:
                facts["series_ids"].add(int(series_id))
            if int(st or 0) in ITEM_STATUS_LOADED_OR_BEYOND:
                facts["loaded_quantity"] += int(qty or 0)
        return out

    async def _load_required_times(
        self, db: AsyncSession, task_ids: list[int]
    ) -> dict[int, tuple[Optional[datetime], Optional[datetime]]]:
        """客户要求装车 / 送达时间；一车多单时取最早（就高不就低）。"""
        r = await db.execute(
            select(
                TaskWaybillItem.task_id,
                func.min(Waybill.required_load_time),
                func.min(Waybill.required_deliver_time),
            )
            .join(Waybill, Waybill.id == TaskWaybillItem.waybill_id)
            .where(
                TaskWaybillItem.task_id.in_(task_ids),
                TaskWaybillItem.is_deleted == 0,
                TaskWaybillItem.status != ITEM_STATUS_CANCELLED,
                Waybill.is_deleted == 0,
            )
            .group_by(TaskWaybillItem.task_id)
        )
        return {int(tid): (rl, rd) for tid, rl, rd in r.all()}

    async def _load_customer_types(
        self, db: AsyncSession, customer_ids: set[int]
    ) -> dict[int, int]:
        if not customer_ids:
            return {}
        r = await db.execute(
            select(Customer.id, Customer.customer_type).where(
                Customer.id.in_(customer_ids), Customer.is_deleted == 0
            )
        )
        return {int(cid): int(ct or 0) for cid, ct in r.all()}

    async def _load_mileage(
        self, db: AsyncSession, task_ids: list[int]
    ) -> dict[int, Decimal]:
        """任务里程 = 各调令公里数合计（任务主表没有里程字段）。"""
        r = await db.execute(
            select(TaskDispatchOrder.task_id, func.sum(TaskDispatchOrder.mileage))
            .where(
                TaskDispatchOrder.task_id.in_(task_ids),
                TaskDispatchOrder.is_deleted == 0,
            )
            .group_by(TaskDispatchOrder.task_id)
        )
        return {int(tid): m for tid, m in r.all() if m is not None}

    async def _load_dispatch_order_counts(
        self, db: AsyncSession, task_ids: list[int]
    ) -> dict[int, int]:
        r = await db.execute(
            select(TaskDispatchOrder.task_id, func.count(TaskDispatchOrder.id))
            .where(
                TaskDispatchOrder.task_id.in_(task_ids),
                TaskDispatchOrder.is_deleted == 0,
            )
            .group_by(TaskDispatchOrder.task_id)
        )
        return {int(tid): int(c or 0) for tid, c in r.all()}

    async def _load_capacity_status(
        self, db: AsyncSession, capacity_ids: set[int]
    ) -> dict[int, int]:
        if not capacity_ids:
            return {}
        r = await db.execute(
            select(Capacity.id, Capacity.operation_status).where(
                Capacity.id.in_(capacity_ids), Capacity.is_deleted == 0
            )
        )
        return {int(cid): int(st or 0) for cid, st in r.all()}


# 锚点型规则的取值入口：规则定义里只存字段名，这里映射到具体读取方式
ANCHOR_LOOKUP = {
    "actual_load_time": lambda ctx: ctx.actual_load_time,
    "actual_arrive_time": lambda ctx: ctx.actual_arrive_time,
}


def _empty_item_facts() -> dict:
    return {
        "customer_ids": set(),
        "customer_names": [],
        "brand_ids": set(),
        "series_ids": set(),
        "loaded_quantity": 0,
    }


__all__ = [
    "TaskAlertContext",
    "TaskAlertContextLoader",
    "RegionChainResolver",
    "ANCHOR_LOOKUP",
    "CAPACITY_STATUS_UNAVAILABLE",
    "CAPACITY_STATUS_LABELS",
    "_earliest",
]
