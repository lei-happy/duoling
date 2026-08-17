"""任务维度的运力推荐入口。

自有车走 heuristic_v1；社会运力本期先出池列表（social_pool_v0），
评价推荐落地后只换社会运力引擎，不改弹窗与响应字段。
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.capacity.social_capacity.social_capacity import (
    SocialCapacity,
)
from app.modules.client.models.capacity.social_capacity.social_capacity_vehicle import (
    SocialCapacityVehicle,
)
from app.modules.client.models.task.constants import CarrierType
from app.modules.client.services.capacity.self_capacity.recommend.engine import (
    CapacityRecommendEngine,
    RecommendItem,
    RecommendReason,
    RecommendResult,
)
from app.modules.client.services.capacity.self_capacity.recommend.heuristic_engine import (
    HeuristicCapacityRecommendEngine,
    assign_ranks,
)
from app.modules.client.services.capacity.social_capacity import (
    APPROVAL_APPROVED,
    STATUS_ACTIVE,
)
from app.modules.client.services.task.task_service import TaskService

SOCIAL_POOL_ENGINE = "social_pool_v0"

_RATING_LABEL = {1: "A", 2: "B", 3: "C", 4: "D"}


def _social_reason(cap: SocialCapacity) -> RecommendReason:
    level = cap.rating_level
    if level in _RATING_LABEL:
        return RecommendReason(
            code="RATING",
            text=f"评级 {_RATING_LABEL[int(level)]}",
        )
    score = cap.rating_score
    if score is not None:
        return RecommendReason(code="RATING", text=f"评分 {score}")
    return RecommendReason(code="POOL", text="社会运力池")


async def _list_social_pool(
    db: AsyncSession,
    *,
    keyword: Optional[str],
    limit: int,
) -> List[RecommendItem]:
    filters = [
        SocialCapacity.is_deleted == 0,
        SocialCapacity.approval_status == APPROVAL_APPROVED,
        SocialCapacity.status == STATUS_ACTIVE,
    ]
    kw = (keyword or "").strip()
    if kw:
        filters.append(
            or_(
                SocialCapacity.social_code.contains(kw),
                SocialCapacity.driver_name.contains(kw),
                SocialCapacity.driver_phone.contains(kw),
                SocialCapacity.plate_number.contains(kw),
            )
        )

    rows = (
        await db.execute(
            select(
                SocialCapacity,
                SocialCapacityVehicle.trailer_plate,
                SocialCapacityVehicle.plate_category,
            )
            .outerjoin(
                SocialCapacityVehicle,
                and_(
                    SocialCapacityVehicle.social_capacity_id == SocialCapacity.id,
                    SocialCapacityVehicle.is_deleted == 0,
                ),
            )
            .where(*filters)
            .order_by(
                desc(SocialCapacity.rating_score),
                desc(SocialCapacity.id),
            )
            .limit(max(1, min(limit, 50)))
        )
    ).all()

    items: List[RecommendItem] = []
    for cap, trailer_plate, plate_category in rows:
        items.append(
            RecommendItem(
                capacityId=int(cap.id),
                driverName=cap.driver_name or "",
                driverPhone=cap.driver_phone or "",
                plateNumber=cap.plate_number or "",
                trailerPlateNumber=trailer_plate or "",
                plateCategory=plate_category or None,
                operationStatus=1,
                reasons=[_social_reason(cap)],
            )
        )
    return items


class CapacityRecommendService:
    _engine: CapacityRecommendEngine = HeuristicCapacityRecommendEngine()

    @classmethod
    def set_engine(cls, engine: CapacityRecommendEngine) -> None:
        cls._engine = engine

    @classmethod
    async def recommend_for_task(
        cls,
        db: AsyncSession,
        task_id: int,
        *,
        keyword: Optional[str] = None,
        limit: int = 20,
    ) -> RecommendResult:
        task = await TaskService.get_or_404(db, task_id)
        carrier_type = int(task.carrier_type or 0)
        if carrier_type == CarrierType.SOCIAL:
            items = await _list_social_pool(db, keyword=keyword, limit=limit)
            return RecommendResult(
                engine=SOCIAL_POOL_ENGINE,
                items=assign_ranks(items),
            )
        if carrier_type != CarrierType.SELF:
            return RecommendResult(engine=cls._engine.name, items=[])
        items = await cls._engine.recommend(
            db, task, keyword=keyword, limit=limit,
        )
        return RecommendResult(engine=cls._engine.name, items=assign_ranks(items))
