"""
运费异常中心服务（Phase 4）
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.billing.freight_calc_exception import FreightCalcException
from app.modules.client.services.billing.freight_calc_task_service import (
    FreightCalcTaskService,
    TASK_MANUAL_RECALC,
)


class FreightExceptionService:

    @staticmethod
    async def page_exceptions(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        exception_type: Optional[str] = None,
        waybill_id: Optional[int] = None,
        batch_id: Optional[int] = None,
    ) -> dict:
        base = select(FreightCalcException).where(
            FreightCalcException.is_deleted == 0,
        )
        if status:
            base = base.where(FreightCalcException.status == status)
        if exception_type:
            base = base.where(FreightCalcException.exception_type == exception_type)
        if waybill_id:
            base = base.where(FreightCalcException.waybill_id == waybill_id)
        if batch_id:
            base = base.where(FreightCalcException.batch_id == batch_id)

        total = (
            await db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar() or 0

        r = await db.execute(
            base.order_by(FreightCalcException.id.desc())
            .offset((page - 1) * page_size).limit(page_size)
        )
        items = []
        for e in r.scalars().all():
            items.append({
                "id": e.id,
                "waybillId": e.waybill_id,
                "waybillCargoId": e.waybill_cargo_id,
                "batchId": e.batch_id,
                "importRowId": e.import_row_id,
                "exceptionType": e.exception_type,
                "exceptionMessage": e.exception_message,
                "contextJson": e.context_json,
                "status": e.status,
                "processedBy": e.processed_by,
                "processedAt": e.processed_at,
                "processRemark": e.process_remark,
                "createdAt": e.created_at,
                "updatedAt": e.updated_at,
            })
        return {
            "list": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def stats(db: AsyncSession) -> dict:
        """异常类型分组统计 + 状态统计（用于异常中心顶部 dashboard）"""
        # 按 type 分组（仅 pending）
        r1 = await db.execute(
            select(
                FreightCalcException.exception_type,
                func.count(FreightCalcException.id),
            )
            .where(
                FreightCalcException.is_deleted == 0,
                FreightCalcException.status == "pending",
            )
            .group_by(FreightCalcException.exception_type)
        )
        by_type = {row[0]: row[1] for row in r1.all()}

        r2 = await db.execute(
            select(
                FreightCalcException.status,
                func.count(FreightCalcException.id),
            )
            .where(FreightCalcException.is_deleted == 0)
            .group_by(FreightCalcException.status)
        )
        by_status = {row[0]: row[1] for row in r2.all()}

        return {"pendingByType": by_type, "byStatus": by_status}

    @staticmethod
    async def resolve(
        db: AsyncSession, exception_id: int,
        *, user_id: Optional[int] = None, remark: Optional[str] = None,
    ) -> None:
        await db.execute(
            update(FreightCalcException)
            .where(FreightCalcException.id == exception_id)
            .values(
                status="processed",
                processed_by=user_id,
                processed_at=datetime.now(),
                process_remark=remark,
            )
        )

    @staticmethod
    async def ignore(
        db: AsyncSession, exception_id: int,
        *, user_id: Optional[int] = None, remark: Optional[str] = None,
    ) -> None:
        await db.execute(
            update(FreightCalcException)
            .where(FreightCalcException.id == exception_id)
            .values(
                status="ignored",
                processed_by=user_id,
                processed_at=datetime.now(),
                process_remark=remark,
            )
        )

    @staticmethod
    async def batch_recalc(
        db: AsyncSession, exception_ids: list[int],
        *, user_id: Optional[int] = None,
    ) -> dict:
        """对一批异常关联的运单重新入队重算，并把异常置 processed。"""
        if not exception_ids:
            return {"recalcCount": 0, "skippedCount": 0}

        r = await db.execute(
            select(FreightCalcException).where(
                FreightCalcException.id.in_(exception_ids),
                FreightCalcException.is_deleted == 0,
            )
        )
        excs = list(r.scalars().all())
        waybill_ids = sorted({e.waybill_id for e in excs if e.waybill_id})
        if not waybill_ids:
            return {"recalcCount": 0, "skippedCount": len(excs)}

        enq = await FreightCalcTaskService.enqueue_many_waybills(
            db, waybill_ids,
            task_type=TASK_MANUAL_RECALC,
            source_target_type="exception_batch",
            source_target_id=None,
            priority=15,
            triggered_by_user_id=user_id,
        )

        # 关联异常打 processed
        await db.execute(
            update(FreightCalcException)
            .where(FreightCalcException.id.in_(exception_ids))
            .values(
                status="processed",
                processed_by=user_id,
                processed_at=datetime.now(),
                process_remark="批量重算关闭",
            )
        )
        return {"recalcCount": enq, "waybillCount": len(waybill_ids)}

    @staticmethod
    async def get_or_404(db: AsyncSession, exception_id: int) -> FreightCalcException:
        r = await db.execute(
            select(FreightCalcException).where(
                FreightCalcException.id == exception_id,
                FreightCalcException.is_deleted == 0,
            )
        )
        e = r.scalar_one_or_none()
        if not e:
            raise BizException("异常不存在")
        return e
