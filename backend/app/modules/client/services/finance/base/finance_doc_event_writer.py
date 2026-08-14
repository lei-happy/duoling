"""财务单据审计事件写入器

封装 ``biz_finance_doc_event`` 的写入，供各财务单据 service 在状态切换时调用。
事件表 append-only：只 insert，不 update / delete。
"""

from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.finance.finance_doc_event import FinanceDocEvent


class FinanceEventType:
    """事件类型常量（与 FinanceDocEvent.event_type 注释一致）

    号段统一在文档 ``00.模块总览`` §6.3 分配，新增类型先登记再落代码，
    避免各期各自取值撞号。
    """

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

    # ===== 对账一致性核对（文档 09） =====
    ADJUST = 16          # 对账行金额调整（adjust_amount 变更）
    DIFF_RAISED = 17     # 差异登记（生成 biz_recon_diff）
    DIFF_CLOSED = 18     # 差异关闭（协商一致或回灌后消解）
    FORCE_CONFIRM = 19   # 带未处置差异强制确认对账单
    RECALC_REFRESH = 20  # 触发计费引擎重算并刷新对账行

    # ===== 资金收付（文档 10）=====
    BATCH_PAY = 21       # 打款批次执行
    RECEIPT_CLAIM = 22   # 收款到账认领（核销分配到结算单）
    UNSETTLE = 23        # 核销冲销（解除核销关系）

    # ===== 进项发票（文档 11，第 3 期）=====
    INVOICE_IN = 24      # 进项票收票登记
    INVOICE_MATCH = 25   # 票款核对通过

    # ===== 信用与账期（文档 12）=====
    # doc_kind 用虚拟大类 'credit_alert'、doc_id 用 customer_id，只记录不拦截
    CREDIT_ALERT = 26

    # ===== 资金账户与销项票（文档 10 §3.3、02 §五，第 4 期）=====
    BALANCE_CALIBRATE = 27  # 银行账户余额校准（必填原因）
    BATCH_ITEM_FAIL = 28    # 打款批次某笔执行失败（批次维度补记，便于筛失败）


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
