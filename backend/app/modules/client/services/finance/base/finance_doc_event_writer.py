"""财务单据审计事件写入器

封装 ``biz_finance_doc_event`` 的写入，供各财务单据 service 在状态切换时调用。
事件表 append-only：只 insert，不 update / delete。
"""

from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.finance.finance_doc_event import FinanceDocEvent


class FinanceEventType:
    """事件类型常量（与 FinanceDocEvent.event_type 注释一致）"""

    CREATE = 1
    SUBMIT = 2
    APPROVE = 3
    REJECT = 4
    WITHDRAW = 5
    PAY = 6
    CANCEL_PAY = 7
    CANCEL = 8
    FORCE_CANCEL = 9
    SETTLE = 10
    LOCK = 11
    UNLOCK = 12
    INVOICE = 13
    VOID = 14
    RED_OFFSET = 15


class FinanceDocEventWriter:
    """财务单据事件写入器"""

    @staticmethod
    async def write(
        db: AsyncSession,
        *,
        doc_kind: str,
        doc_id: int,
        event_type: int,
        from_status: Optional[int] = None,
        to_status: Optional[int] = None,
        direction: Optional[int] = None,
        occurred_amount: Optional[Decimal] = None,
        operator_id: Optional[int] = None,
        operator_name: Optional[str] = None,
        reason: Optional[str] = None,
        payload_snapshot: Optional[dict[str, Any]] = None,
    ) -> FinanceDocEvent:
        """写入一条审计事件（不 commit，随外层事务提交）。"""
        evt = FinanceDocEvent(
            doc_kind=doc_kind,
            doc_id=doc_id,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            direction=direction,
            occurred_amount=occurred_amount,
            operator_id=operator_id,
            operator_name=operator_name,
            reason=reason,
            payload_snapshot=payload_snapshot,
        )
        db.add(evt)
        await db.flush()
        return evt

    @staticmethod
    async def list_by_doc(
        db: AsyncSession,
        doc_kind: str,
        doc_id: int,
    ) -> list[FinanceDocEvent]:
        """按单据返回时间倒序事件流（详情抽屉审计区块用）。"""
        from sqlalchemy import select

        r = await db.execute(
            select(FinanceDocEvent)
            .where(
                FinanceDocEvent.doc_kind == doc_kind,
                FinanceDocEvent.doc_id == doc_id,
                FinanceDocEvent.is_deleted == 0,
            )
            .order_by(FinanceDocEvent.event_time.desc(), FinanceDocEvent.id.desc())
        )
        return list(r.scalars().all())
