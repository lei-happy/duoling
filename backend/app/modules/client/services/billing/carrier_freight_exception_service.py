"""
承运商运费计算异常服务（分页 / 统计 / 处理 / 批量重算）
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.billing.carrier_freight_calc_exception import (
    CarrierFreightCalcException,
)
from app.modules.client.services.billing.carrier_freight_calc_task_service import (
    CarrierFreightCalcTaskService,
    TASK_MANUAL_RECALC,
)


class CarrierFreightExceptionService:

    @staticmethod
    async def page_exceptions(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        exception_type: Optional[str] = None,
        task_id: Optional[int] = None,
    ) -> dict:
        base = select(CarrierFreightCalcException).where(
            CarrierFreightCalcException.is_deleted == 0
        )
        if status:
            base = base.where(CarrierFreightCalcException.status == status)
        if exception_type:
            base = base.where(
                CarrierFreightCalcException.exception_type == exception_type
            )
        if task_id:
            base = base.where(CarrierFreightCalcException.task_id == task_id)

        total = (
            await db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar() or 0
        r = await db.execute(
            base.order_by(CarrierFreightCalcException.id.desc())
            .offset((page - 1) * page_size).limit(page_size)
        )
        items = []
        for e in r.scalars().all():
            items.append({
                "id": e.id,
                "taskId": e.task_id,
                "carrierId": e.carrier_id,
                "exceptionType": e.exception_type,
                "exceptionMessage": e.exception_message,
                "contextJson": e.context_json,
                "status": e.status,
                "processedBy": e.processed_by,
                "processedAt": e.processed_at,
                "processRemark": e.process_remark,
                "createdAt": e.created_at,
            })
        return {"list": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    async def stats(db: AsyncSession) -> dict:
        r = await db.execute(
            select(CarrierFreightCalcException.status, func.count())
            .where(CarrierFreightCalcException.is_deleted == 0)
            .group_by(CarrierFreightCalcException.status)
        )
        by_status = {row[0]: int(row[1]) for row in r.all()}
        r2 = await db.execute(
            select(CarrierFreightCalcException.exception_type, func.count())
            .where(
                CarrierFreightCalcException.is_deleted == 0,
                CarrierFreightCalcException.status == "pending",
            )
            .group_by(CarrierFreightCalcException.exception_type)
        )
        by_type = {row[0]: int(row[1]) for row in r2.all()}
        return {
            "pending": by_status.get("pending", 0),
            "processed": by_status.get("processed", 0),
            "ignored": by_status.get("ignored", 0),
            "byType": by_type,
        }

    @staticmethod
    async def _get(
        db: AsyncSession, exception_id: int
    ) -> CarrierFreightCalcException:
        r = await db.execute(
            select(CarrierFreightCalcException).where(
                CarrierFreightCalcException.id == exception_id,
                CarrierFreightCalcException.is_deleted == 0,
            )
        )
        e = r.scalar_one_or_none()
        if not e:
            raise BizException("异常记录不存在")
        return e

    @staticmethod
    async def resolve(
        db: AsyncSession, exception_id: int, *,
        user_id: Optional[int] = None, remark: Optional[str] = None,
    ) -> None:
        e = await CarrierFreightExceptionService._get(db, exception_id)
        e.status = "processed"
        e.processed_by = user_id
        e.processed_at = datetime.now()
        e.process_remark = remark
        await db.flush()

    @staticmethod
    async def ignore(
        db: AsyncSession, exception_id: int, *,
        user_id: Optional[int] = None, remark: Optional[str] = None,
    ) -> None:
        e = await CarrierFreightExceptionService._get(db, exception_id)
        e.status = "ignored"
        e.processed_by = user_id
        e.processed_at = datetime.now()
        e.process_remark = remark
        await db.flush()

    @staticmethod
    async def batch_recalc(
        db: AsyncSession, exception_ids: list[int], *,
        user_id: Optional[int] = None,
    ) -> dict:
        if not exception_ids:
            return {"enqueuedTaskCount": 0}
        r = await db.execute(
            select(CarrierFreightCalcException.task_id).where(
                CarrierFreightCalcException.id.in_(exception_ids),
                CarrierFreightCalcException.is_deleted == 0,
            ).distinct()
        )
        task_ids = [row[0] for row in r.all() if row[0]]
        enqueued = await CarrierFreightCalcTaskService.enqueue_many_tasks(
            db, task_ids,
            task_type=TASK_MANUAL_RECALC,
            source_target_type="exception",
            priority=8,
            triggered_by_user_id=user_id,
        )
        return {"enqueuedTaskCount": enqueued, "affectedTaskCount": len(task_ids)}
