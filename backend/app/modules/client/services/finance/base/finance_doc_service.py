"""财务单据通用 service 模板

对账单、结算单、工资单、发票的骨架动作是同一套：生成单号 → 草稿 → 提交 →
审批 → 支付/收款 → 撤销，每一步都要校验状态机、补齐操作人时间、写审计事件。
这些逻辑与具体单据无关，集中在这里一份实现，子类只写领域特有的部分。

用法：

    class CustomerReconService(FinanceDocService):
        model = CustomerRecon
        doc_kind = "customer_recon"
        doc_label = "客户对账单"
        doc_no_prefix = "CR"
        direction = FinanceDirection.RECEIVE

        # 领域特有：候选生成、行增删、金额重算…

已落地的 ``task_finance_service`` 出于向后兼容不改为继承本模板（它的
``_change_status`` 与本类语义一致），新单据一律走这里，避免每类单据各写一遍
状态切换与事件写入后互相漂移。

注意：本模板的方法都**不 commit**，随外层事务提交；这样一次请求内的多单据
联动（如结算单收款同时锁定运单）能保证原子性。
"""

from datetime import date as ddate, datetime
from decimal import Decimal
from typing import Any, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.services.finance.base.constants import FinanceDirection
from app.modules.client.services.finance.base.finance_doc_event_writer import (
    FinanceDocEventWriter,
    FinanceEventType,
)
from app.modules.client.services.finance.base.finance_state_machine import (
    FIN_CANCELLED,
    FIN_DRAFT,
    FIN_PAID,
    FIN_PENDING_REVIEW,
    FIN_REVIEWED,
    FIN_SETTLED,
    FinanceStateMachine,
    label as status_label,
)

# 撤销 / 撤销支付 / 强制撤销原因最小长度（与既有任务级费用单一致）
CANCEL_REASON_MIN_LEN = 5
# 单号日序号宽度
_DOC_NO_SEQ_WIDTH = 4


class FinanceDocService:
    """财务单据通用动作模板（子类通过类属性声明单据身份）"""

    # ===== 子类必须覆盖 =====
    model: Any = None
    doc_kind: str = ""
    doc_label: str = "单据"
    doc_no_prefix: str = "F"
    direction: int = FinanceDirection.PAY

    # ===== 子类可覆盖 =====
    # 允许编辑的状态集：多数单据仅草稿可改，任务级费用单放开到待审批
    editable_statuses: Sequence[int] = (FIN_DRAFT,)
    # 允许删除（软删）的状态集：草稿与已撤销
    deletable_statuses: Sequence[int] = (FIN_DRAFT, FIN_CANCELLED)

    # ------------------------------------------------------------------
    # 单号与取单
    # ------------------------------------------------------------------
    @classmethod
    async def generate_doc_no(cls, db: AsyncSession) -> str:
        """生成单号：前缀 + 日期 + 4 位日序号，如 ``CR202608130001``。

        取当天最大单号递增而非计数递增：单据被物理删除时计数会回退并撞号，
        取最大值不会。
        """
        prefix = f"{cls.doc_no_prefix}{ddate.today().strftime('%Y%m%d')}"
        r = await db.execute(
            select(func.max(cls.model.doc_no)).where(
                cls.model.doc_no.like(f"{prefix}%")
            )
        )
        last = r.scalar()
        seq = 1
        if last:
            try:
                seq = int(str(last)[len(prefix):]) + 1
            except (TypeError, ValueError):
                seq = 1
        return f"{prefix}{seq:0{_DOC_NO_SEQ_WIDTH}d}"

    @classmethod
    async def get_or_404(cls, db: AsyncSession, doc_id: int) -> Any:
        r = await db.execute(
            select(cls.model).where(
                cls.model.id == doc_id, cls.model.is_deleted == 0,
            )
        )
        doc = r.scalar_one_or_none()
        if doc is None:
            raise BizException(f"{cls.doc_label}不存在")
        return doc

    @classmethod
    async def list_events(cls, db: AsyncSession, doc_id: int) -> list:
        """该单据的审计事件流（时间倒序，详情抽屉审计区块用）。"""
        await cls.get_or_404(db, doc_id)
        return await FinanceDocEventWriter.list_by_doc(db, cls.doc_kind, doc_id)

    # ------------------------------------------------------------------
    # 校验
    # ------------------------------------------------------------------
    @classmethod
    def assert_editable(cls, doc: Any) -> None:
        FinanceStateMachine.assert_not_locked(getattr(doc, "is_locked", 0))
        if int(doc.status) not in tuple(cls.editable_statuses):
            raise BizException(
                f"{cls.doc_label}当前是「{_label(doc.status, cls.doc_kind)}」，不能修改；"
                "请先退回草稿"
            )

    @classmethod
    def assert_deletable(cls, doc: Any) -> None:
        if int(doc.status) not in tuple(cls.deletable_statuses):
            raise BizException(
                f"{cls.doc_label}当前是「{_label(doc.status, cls.doc_kind)}」，不能删除；"
                "仅草稿与已撤销的单据可删除"
            )

    @classmethod
    def assert_reason(cls, reason: Optional[str], *, action: str = "撤销") -> str:
        text = (reason or "").strip()
        if len(text) < CANCEL_REASON_MIN_LEN:
            raise BizException(
                f"请填写{action}原因，且不少于 {CANCEL_REASON_MIN_LEN} 个字"
            )
        return text

    # ------------------------------------------------------------------
    # 状态切换
    # ------------------------------------------------------------------
    @classmethod
    async def change_status(
        cls,
        db: AsyncSession,
        doc: Any,
        new_status: int,
        *,
        event_type: int,
        operator_id: Optional[int] = None,
        operator_name: Optional[str] = None,
        reason: Optional[str] = None,
        occurred_amount: Optional[Decimal] = None,
        payload_snapshot: Optional[dict] = None,
        skip_lock_check: bool = False,
    ) -> None:
        """通用状态切换：状态机校验 + 补齐操作人时间 + 写审计事件。

        ``skip_lock_check=True`` 仅用于「撤销已支付」这类需要先解锁的场景，
        由调用方在解锁后自行保证安全。
        """
        old = int(doc.status)
        has_reason = bool(reason and reason.strip())
        if not skip_lock_check:
            FinanceStateMachine.assert_not_locked(getattr(doc, "is_locked", 0))
        FinanceStateMachine.assert_transition(
            cls.doc_kind, old, new_status, has_reason=has_reason,
        )

        doc.status = new_status
        now = datetime.now()
        if new_status == FIN_PENDING_REVIEW:
            doc.submitted_by = operator_id
            doc.submitted_at = now
        elif new_status == FIN_REVIEWED:
            doc.reviewed_by = operator_id
            doc.reviewed_at = now
        elif new_status == FIN_PAID:
            doc.paid_by = operator_id
            if getattr(doc, "paid_at", None) is None:
                doc.paid_at = now
        elif new_status == FIN_CANCELLED:
            doc.cancelled_by = operator_id
            doc.cancelled_at = now
            if reason:
                doc.cancel_reason = reason.strip()

        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=doc.id,
            event_type=event_type,
            from_status=old,
            to_status=new_status,
            direction=int(getattr(doc, "direction", cls.direction) or cls.direction),
            occurred_amount=occurred_amount,
            operator_id=operator_id,
            operator_name=operator_name,
            reason=reason.strip() if reason else None,
            payload_snapshot=payload_snapshot,
        )
        await db.flush()

    @classmethod
    async def submit(
        cls, db: AsyncSession, doc_id: int, operator_id: Optional[int] = None,
    ) -> Any:
        """草稿 → 待审批。"""
        doc = await cls.get_or_404(db, doc_id)
        FinanceStateMachine.assert_submittable(
            planned_amount=doc.planned_amount,
        )
        await cls.change_status(
            db, doc, FIN_PENDING_REVIEW,
            event_type=FinanceEventType.SUBMIT,
            operator_id=operator_id,
            occurred_amount=doc.planned_amount,
        )
        return doc

    @classmethod
    async def approve(
        cls, db: AsyncSession, doc_id: int, operator_id: Optional[int] = None,
    ) -> Any:
        """待审批 → 已审批。"""
        doc = await cls.get_or_404(db, doc_id)
        await cls.change_status(
            db, doc, FIN_REVIEWED,
            event_type=FinanceEventType.APPROVE,
            operator_id=operator_id,
            occurred_amount=doc.planned_amount,
        )
        return doc

    @classmethod
    async def reject(
        cls,
        db: AsyncSession,
        doc_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> Any:
        """待审批 → 已撤销（审批拒绝）。"""
        doc = await cls.get_or_404(db, doc_id)
        if int(doc.status) != FIN_PENDING_REVIEW:
            raise BizException(
                f"只有「待审批」的{cls.doc_label}可以拒绝"
                f"（当前：{_label(doc.status, cls.doc_kind)}）"
            )
        text = cls.assert_reason(reason, action="拒绝")
        await cls.change_status(
            db, doc, FIN_CANCELLED,
            event_type=FinanceEventType.REJECT,
            operator_id=operator_id,
            reason=text,
        )
        return doc

    @classmethod
    async def withdraw_to_draft(
        cls, db: AsyncSession, doc_id: int, operator_id: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Any:
        """待审批 / 已审批 → 草稿（录错后修改）。"""
        doc = await cls.get_or_404(db, doc_id)
        if int(doc.status) not in (FIN_PENDING_REVIEW, FIN_REVIEWED):
            raise BizException(
                f"只有「待审批 / 已审批」的{cls.doc_label}可以退回草稿"
                f"（当前：{_label(doc.status, cls.doc_kind)}）"
            )
        await cls.change_status(
            db, doc, FIN_DRAFT,
            event_type=FinanceEventType.WITHDRAW,
            operator_id=operator_id,
            reason=reason,
        )
        return doc

    @classmethod
    async def pay(
        cls,
        db: AsyncSession,
        doc_id: int,
        *,
        actual_amount: Decimal,
        paid_at: datetime,
        pay_method: Optional[int],
        pay_voucher_url: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> Any:
        """已审批 → 已支付 / 已收款。

        应收单据语义为「收款」，应付为「付款」，字段与状态共用一套。
        """
        doc = await cls.get_or_404(db, doc_id)
        if int(doc.status) != FIN_REVIEWED:
            raise BizException(
                f"只有「已审批」的{cls.doc_label}可以登记收付款"
                f"（当前：{_label(doc.status, cls.doc_kind)}）"
            )
        FinanceStateMachine.assert_payable(
            actual_amount=actual_amount, paid_at=paid_at, pay_method=pay_method,
        )
        doc.actual_amount = Decimal(str(actual_amount))
        doc.paid_at = paid_at
        doc.pay_method = pay_method
        if pay_voucher_url:
            doc.pay_voucher_url = pay_voucher_url
        await cls.change_status(
            db, doc, FIN_PAID,
            event_type=FinanceEventType.PAY,
            operator_id=operator_id,
            occurred_amount=doc.actual_amount,
        )
        return doc

    @classmethod
    async def cancel_payment(
        cls,
        db: AsyncSession,
        doc_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> Any:
        """已支付 → 已审批（撤销收付款，高权限）。

        解锁下游业务对象由子类在调用前后自行编排（``LockOrchestrator``），
        本方法只负责单据自身的状态与留痕。
        """
        doc = await cls.get_or_404(db, doc_id)
        if int(doc.status) != FIN_PAID:
            raise BizException(
                f"只有「已支付 / 已收款」的{cls.doc_label}可以撤销收付款"
                f"（当前：{_label(doc.status, cls.doc_kind)}）"
            )
        text = cls.assert_reason(reason, action="撤销收付款")
        amount = doc.actual_amount
        await cls.change_status(
            db, doc, FIN_REVIEWED,
            event_type=FinanceEventType.CANCEL_PAY,
            operator_id=operator_id,
            reason=text,
            occurred_amount=(-amount if amount is not None else None),
            skip_lock_check=True,
        )
        return doc

    @classmethod
    async def cancel(
        cls,
        db: AsyncSession,
        doc_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> Any:
        """未支付单据撤销。已支付需走 ``force_cancel``。"""
        doc = await cls.get_or_404(db, doc_id)
        FinanceStateMachine.assert_cancellable(int(doc.status), with_force=False)
        text = cls.assert_reason(reason)
        await cls.change_status(
            db, doc, FIN_CANCELLED,
            event_type=FinanceEventType.CANCEL,
            operator_id=operator_id,
            reason=text,
        )
        return doc

    @classmethod
    async def force_cancel(
        cls,
        db: AsyncSession,
        doc_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> Any:
        """已支付单据强制撤销（高权限）。"""
        doc = await cls.get_or_404(db, doc_id)
        FinanceStateMachine.assert_cancellable(int(doc.status), with_force=True)
        text = cls.assert_reason(reason, action="强制撤销")
        amount = doc.actual_amount
        await cls.change_status(
            db, doc, FIN_CANCELLED,
            event_type=FinanceEventType.FORCE_CANCEL,
            operator_id=operator_id,
            reason=text,
            occurred_amount=(-amount if amount is not None else None),
            skip_lock_check=True,
        )
        return doc

    @classmethod
    async def settle(
        cls, db: AsyncSession, doc_id: int, operator_id: Optional[int] = None,
    ) -> Any:
        """已支付 → 已核销（下游单据全部结清后调用）。"""
        doc = await cls.get_or_404(db, doc_id)
        await cls.change_status(
            db, doc, FIN_SETTLED,
            event_type=FinanceEventType.SETTLE,
            operator_id=operator_id,
            occurred_amount=doc.actual_amount,
            skip_lock_check=True,
        )
        return doc

    @classmethod
    async def soft_delete(cls, db: AsyncSession, doc_id: int) -> None:
        doc = await cls.get_or_404(db, doc_id)
        cls.assert_deletable(doc)
        doc.is_deleted = 1
        await db.flush()

    # ------------------------------------------------------------------
    # 前端按钮显隐
    # ------------------------------------------------------------------
    @classmethod
    def action_flags(cls, doc: Any) -> dict:
        """返回 ``*Out`` 的动作可用标记，供前端按钮显隐。

        只反映**状态机允许**，不含角色权限——权限由前端按 ``menu_code`` 独立
        判断，两者是与的关系。
        """
        status = int(doc.status)
        locked = int(getattr(doc, "is_locked", 0) or 0) == 1
        allowed = FinanceStateMachine.legal_next(cls.doc_kind, status)
        return {
            "canEdit": (not locked) and status in tuple(cls.editable_statuses),
            "canDelete": status in tuple(cls.deletable_statuses),
            "canSubmit": (not locked) and FIN_PENDING_REVIEW in allowed,
            "canApprove": status == FIN_PENDING_REVIEW,
            "canReject": status == FIN_PENDING_REVIEW,
            "canWithdraw": status in (FIN_PENDING_REVIEW, FIN_REVIEWED),
            "canPay": (not locked) and status == FIN_REVIEWED,
            "canCancelPay": status == FIN_PAID,
            "canCancel": status not in (FIN_CANCELLED, FIN_SETTLED, FIN_PAID),
            "canForceCancel": status == FIN_PAID,
        }


def _label(status: Any, doc_kind: Optional[str] = None) -> str:
    return status_label(int(status or 0), doc_kind)
