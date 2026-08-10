"""计划回单 Service

回单是 **计划维度** 的人工动作，与任务/挂接行状态机彼此独立：
- 确认回单：计划 ``5 已交车`` → ``6 已回单``，落一条 ``biz_waybill_receipt`` 凭证；
- 撤销回单：计划 ``6 已回单`` → ``5 已交车``，软删该计划的回单凭证；
- 列举：返回某计划的全部有效回单凭证。

约束：
- 仅 ``5 已交车`` 可确认回单；仅 ``6 已回单`` 可撤销回单（``7 已关闭`` 后不可撤销）。
- 状态跳转统一经 ``WaybillStateMachine.assert_transition`` 校验。
- 全程不触碰任务状态机，也不调用 ``WaybillStatusAggregator``（回单为 skip 态）。
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_receipt import WaybillReceipt
from app.modules.client.schemas.waybill.waybill_receipt import (
    WaybillReceiptConfirm,
    WaybillReceiptOut,
)
from app.modules.client.services.state_machine.waybill_state_machine import (
    WAYBILL_RECEIPTED,
    WAYBILL_SIGNED,
    WaybillStateMachine,
)


class WaybillReceiptService:
    """计划回单服务"""

    @staticmethod
    async def list_receipts(
        db: AsyncSession, waybill_id: int,
    ) -> List[WaybillReceiptOut]:
        r = await db.execute(
            select(WaybillReceipt)
            .where(
                WaybillReceipt.waybill_id == waybill_id,
                WaybillReceipt.is_deleted == 0,
            )
            .order_by(WaybillReceipt.received_at.desc(), WaybillReceipt.id.desc())
        )
        return [WaybillReceiptOut.from_model(m) for m in r.scalars().all()]

    @staticmethod
    async def confirm(
        db: AsyncSession,
        waybill_id: int,
        data: WaybillReceiptConfirm,
        *,
        operator_id: Optional[int] = None,
        operator_name: Optional[str] = None,
    ) -> WaybillReceiptOut:
        """确认回单：计划 5 已交车 → 6 已回单。"""
        waybill = await WaybillReceiptService._lock_waybill(db, waybill_id)
        cur = int(waybill.status or 0)
        if cur != WAYBILL_SIGNED:
            raise BizException("仅「已交车」的计划可以确认回单")
        # 状态机校验 5 → 6
        WaybillStateMachine.assert_transition(cur, WAYBILL_RECEIPTED)

        received_at = data.receivedAt or datetime.now()
        rec = WaybillReceipt(
            waybill_id=waybill_id,
            file_urls=list(data.fileUrls or []),
            file_type=int(data.fileType or 1),
            received_at=received_at,
            uploaded_by=operator_id,
            operator_name=operator_name,
            remark=data.remark,
        )
        db.add(rec)
        waybill.status = WAYBILL_RECEIPTED
        waybill.receipt_at = received_at
        await db.flush()
        await db.refresh(rec)
        return WaybillReceiptOut.from_model(rec)

    @staticmethod
    async def revoke(
        db: AsyncSession, waybill_id: int,
    ) -> None:
        """撤销回单：计划 6 已回单 → 5 已交车，软删凭证。"""
        waybill = await WaybillReceiptService._lock_waybill(db, waybill_id)
        cur = int(waybill.status or 0)
        if cur != WAYBILL_RECEIPTED:
            raise BizException("仅「已回单」的计划可以撤销回单")
        WaybillStateMachine.assert_transition(cur, WAYBILL_SIGNED)

        r = await db.execute(
            select(WaybillReceipt).where(
                WaybillReceipt.waybill_id == waybill_id,
                WaybillReceipt.is_deleted == 0,
            )
        )
        for rec in r.scalars().all():
            rec.is_deleted = 1
        waybill.status = WAYBILL_SIGNED
        waybill.receipt_at = None
        await db.flush()

    @staticmethod
    async def _lock_waybill(db: AsyncSession, waybill_id: int) -> Waybill:
        r = await db.execute(
            select(Waybill)
            .where(Waybill.id == waybill_id, Waybill.is_deleted == 0)
            .with_for_update()
        )
        waybill = r.scalar_one_or_none()
        if not waybill:
            raise BizException("计划不存在")
        return waybill
