"""heuristic_v1：可接单 / 常跑线路 / 运营状态。理由必须可解释。"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Set

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.models.capacity.self_capacity.driver.driver_route import (
    DriverRoute,
)
from app.modules.client.models.capacity.self_capacity.trailer import Trailer
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
from app.modules.client.models.task.task import Task
from app.modules.client.services.capacity.self_capacity.recommend.engine import (
    RecommendItem,
    RecommendReason,
)
from app.modules.client.services.state_machine.task_state_machine import (
    TASK_OCCUPYING_CAPACITY_STATUSES,
)

ENGINE_NAME = "heuristic_v1"

OP_AVAILABLE = 1
OP_IN_TRANSIT = 2
OP_LEAVE = 3
OP_STOPPED = 4
OP_MAINTENANCE = 5

_UNAVAILABLE = {OP_LEAVE, OP_STOPPED, OP_MAINTENANCE}

# 已绑定运力且尚未交车/关闭/取消：司机处于待接单或执行中，不再进默认推荐
_OCCUPYING_TASK_STATUSES = tuple(TASK_OCCUPYING_CAPACITY_STATUSES)

_STATUS_SCORE = {
    OP_AVAILABLE: 100,
    OP_IN_TRANSIT: 50,
    OP_LEAVE: 10,
    OP_STOPPED: 5,
    OP_MAINTENANCE: 5,
}
_OCCUPIED_SCORE = 20

_ROUTE_BONUS = 40


def _codes_match(left: Optional[str], right: Optional[str]) -> bool:
    if not left or not right:
        return False
    a, b = left.strip(), right.strip()
    if not a or not b:
        return False
    return a == b or a.startswith(b) or b.startswith(a)


def _route_hit(
    routes: Sequence[DriverRoute],
    origin_code: Optional[str],
    dest_code: Optional[str],
) -> Optional[DriverRoute]:
    for route in routes:
        if route.status != 1:
            continue
        if _codes_match(route.origin_code, origin_code) and _codes_match(
            route.dest_code, dest_code
        ):
            return route
    return None


async def _occupied_capacity_ids(
    db: AsyncSession,
    *,
    exclude_task_id: int,
) -> Set[int]:
    rows = await db.execute(
        select(Task.capacity_id).where(
            Task.is_deleted == 0,
            Task.capacity_id.isnot(None),
            Task.status.in_(_OCCUPYING_TASK_STATUSES),
            Task.id != exclude_task_id,
        )
    )
    return {int(cid) for cid in rows.scalars().all() if cid}


def _reasons_for(
    operation_status: int,
    matched_route: Optional[DriverRoute],
    task: Task,
    *,
    occupied: bool = False,
) -> List[RecommendReason]:
    reasons: List[RecommendReason] = []
    if occupied:
        reasons.append(
            RecommendReason(code="ASSIGNED_OTHER", text="已派其他任务，待接单或执行中")
        )
    elif operation_status == OP_AVAILABLE:
        reasons.append(RecommendReason(code="AVAILABLE", text="当前可接单"))
    elif operation_status == OP_IN_TRANSIT:
        reasons.append(RecommendReason(code="IN_TRANSIT", text="正在执行其他任务"))
    elif operation_status == OP_LEAVE:
        reasons.append(RecommendReason(code="ON_LEAVE", text="司机休假中"))
    elif operation_status == OP_STOPPED:
        reasons.append(RecommendReason(code="STOPPED", text="当前停运"))
    elif operation_status == OP_MAINTENANCE:
        reasons.append(RecommendReason(code="MAINTENANCE", text="维修保养中"))

    if matched_route is not None:
        origin = (
            matched_route.origin_name
            or task.origin
            or matched_route.origin_code
            or ""
        )
        dest = (
            matched_route.dest_name
            or task.destination
            or matched_route.dest_code
            or ""
        )
        reasons.append(
            RecommendReason(
                code="FAMILIAR_ROUTE",
                text=f"常跑{origin}→{dest}",
            )
        )
    return reasons


def _keyword_hit(cap: Capacity, trailer_plate: Optional[str], keyword: str) -> bool:
    kw = keyword.strip()
    if not kw:
        return True
    hay = " ".join(
        part
        for part in (
            cap.driver_name,
            cap.driver_phone,
            cap.plate_number,
            trailer_plate or "",
        )
        if part
    )
    return kw in hay


class HeuristicCapacityRecommendEngine:
    name = ENGINE_NAME

    async def recommend(
        self,
        db: AsyncSession,
        task: Task,
        *,
        keyword: Optional[str] = None,
        limit: int = 20,
    ) -> List[RecommendItem]:
        rows = await db.execute(
            select(Capacity, Trailer.plate_number, Vehicle.plate_category)
            .outerjoin(
                Vehicle,
                and_(Vehicle.id == Capacity.vehicle_id, Vehicle.is_deleted == 0),
            )
            .outerjoin(
                Trailer,
                and_(Trailer.id == Vehicle.trailer_id, Trailer.is_deleted == 0),
            )
            .where(Capacity.status == 1, Capacity.is_deleted == 0)
        )
        capacities: List[tuple[Capacity, Optional[str], Optional[str]]] = [
            (cap, trailer_plate, plate_category)
            for cap, trailer_plate, plate_category in rows.all()
        ]
        if not capacities:
            return []

        occupied_ids = await _occupied_capacity_ids(db, exclude_task_id=int(task.id))
        driver_ids = {cap.driver_id for cap, _, _ in capacities}
        route_rows = await db.execute(
            select(DriverRoute).where(
                DriverRoute.driver_id.in_(driver_ids),
                DriverRoute.is_deleted == 0,
            )
        )
        routes_by_driver: dict[int, list[DriverRoute]] = {}
        for route in route_rows.scalars().all():
            routes_by_driver.setdefault(int(route.driver_id), []).append(route)

        kw = (keyword or "").strip()
        scored: list[tuple[int, int, RecommendItem]] = []
        for cap, trailer_plate, plate_category in capacities:
            if kw and not _keyword_hit(cap, trailer_plate, kw):
                continue
            op = int(cap.operation_status or OP_AVAILABLE)
            occupied = int(cap.id) in occupied_ids
            if not kw and (op in _UNAVAILABLE or occupied):
                continue
            matched = _route_hit(
                routes_by_driver.get(int(cap.driver_id), []),
                task.origin_code,
                task.destination_code,
            )
            score = _OCCUPIED_SCORE if occupied else _STATUS_SCORE.get(op, 0)
            if matched is not None:
                score += _ROUTE_BONUS
            item = RecommendItem(
                capacityId=int(cap.id),
                driverName=cap.driver_name or "",
                driverPhone=cap.driver_phone or "",
                plateNumber=cap.plate_number or "",
                trailerPlateNumber=trailer_plate or "",
                plateCategory=plate_category or None,
                operationStatus=op,
                reasons=_reasons_for(op, matched, task, occupied=occupied),
            )
            scored.append((score, int(cap.id), item))

        scored.sort(key=lambda row: (-row[0], -row[1]))
        return [item for _, _, item in scored[: max(1, min(limit, 50))]]


def assign_ranks(items: Iterable[RecommendItem]) -> List[RecommendItem]:
    ranked: List[RecommendItem] = []
    for idx, item in enumerate(items, start=1):
        item.rank = idx
        ranked.append(item)
    return ranked
