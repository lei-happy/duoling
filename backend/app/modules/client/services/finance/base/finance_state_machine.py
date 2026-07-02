"""财务单据通用状态机

集中维护财务单据的状态跳转规则，与 06 模块 ``TaskStateMachine`` /
``WaybillStateMachine`` / ``ItemStateMachine`` 同源风格。

通用状态码（文档 01 §2.2）：
    0-草稿 1-待审批 2-已审批 3-已支付/已收款/已开票
    4-已撤销 5-已核销/已结清 6-部分核销/部分支付 9-已作废

不同子单据只使用其中部分状态码，见 ``DOC_KIND_STATES`` 矩阵。
"""

from typing import Optional, Set

from app.common.exceptions import BizException


# ===== 通用状态码常量 =====
FIN_DRAFT = 0
FIN_PENDING_REVIEW = 1
FIN_REVIEWED = 2
FIN_PAID = 3
FIN_CANCELLED = 4
FIN_SETTLED = 5
FIN_PARTIAL = 6
FIN_VOIDED = 9


FIN_STATUS_LABELS: dict[int, str] = {
    0: "草稿",
    1: "待审批",
    2: "已审批",
    3: "已支付",
    4: "已撤销",
    5: "已核销",
    6: "部分核销",
    9: "已作废",
}


# 通用合法跳转表（子单据可用状态集再做交集裁剪）
FIN_VALID_TRANS: dict[int, Set[int]] = {
    0: {1, 4},        # 草稿 → 待审批 / 已撤销
    1: {0, 2, 4},     # 待审批 → 退回草稿 / 已审批 / 已撤销（拒绝）
    2: {0, 3, 4},     # 已审批 → 退回草稿 / 已支付 / 已撤销
    3: {2, 4, 5},     # 已支付 → 撤销支付 / 强制撤销 / 核销
    4: set(),         # 已撤销：终态
    5: set(),         # 已核销：终态
    6: {3, 5},        # 部分核销 → 已支付 / 已核销（远期）
    9: set(),         # 已作废：终态
}


# 各单据大类可用状态集（文档 01 §2.2.3）
DOC_KIND_STATES: dict[str, Set[int]] = {
    "task_finance": {0, 1, 2, 3, 4},
    "carrier_recon": {0, 2, 3, 4, 5},
    "carrier_settle": {0, 1, 2, 3, 4, 5},
    "driver_payroll": {0, 1, 2, 3, 4},
    "customer_recon": {0, 2, 3, 4, 5},
    "customer_settle": {0, 1, 2, 3, 4, 5},
    "customer_invoice": {0, 1, 3, 4, 9},
}


# 需要强制填写 reason 的目标状态（撤销/退回类）
_REASON_REQUIRED_TO: Set[int] = {FIN_CANCELLED}
# 已支付 → 已审批（撤销支付）也需要 reason
_REASON_REQUIRED_TRANS: Set[tuple[int, int]] = {(FIN_PAID, FIN_REVIEWED)}


def label(status: int) -> str:
    return FIN_STATUS_LABELS.get(status, str(status))


class FinanceStateMachine:
    """财务单据状态机工具方法"""

    @staticmethod
    def assert_transition(
        doc_kind: str,
        old: int,
        new: int,
        *,
        has_reason: bool = False,
    ) -> None:
        """校验单据状态合法跳转。

        - 校验 old→new 在通用跳转表内；
        - 校验 new 在该 doc_kind 的可用状态集内；
        - 撤销 / 退回 / 撤销支付类必须 has_reason=True。
        """
        allowed = FIN_VALID_TRANS.get(old, set())
        if new not in allowed:
            raise BizException(
                f"单据状态从「{label(old)}」不能直接跳转到「{label(new)}」"
            )
        kind_states = DOC_KIND_STATES.get(doc_kind)
        if kind_states is not None and new not in kind_states:
            raise BizException(
                f"单据类型「{doc_kind}」不支持状态「{label(new)}」"
            )
        need_reason = (
            new in _REASON_REQUIRED_TO
            or (old, new) in _REASON_REQUIRED_TRANS
        )
        if need_reason and not has_reason:
            raise BizException("撤销 / 退回 / 撤销支付操作必须填写原因")

    @staticmethod
    def assert_submittable(
        *, planned_amount, has_payee: bool = True
    ) -> None:
        """0 → 1 校验：金额>0、必填业务关联字段已填。"""
        if planned_amount is None or float(planned_amount) <= 0:
            raise BizException("提交审批前计划金额必须大于 0")
        if not has_payee:
            raise BizException("提交审批前必须指定收/付款对象")

    @staticmethod
    def assert_payable(
        *, actual_amount, paid_at, pay_method: Optional[int]
    ) -> None:
        """2 → 3 校验：actual_amount、paid_at、pay_method 填写完整。"""
        if actual_amount is None or float(actual_amount) <= 0:
            raise BizException("支付/收款金额必须大于 0")
        if paid_at is None:
            raise BizException("必须填写支付/收款时间")
        if pay_method is None:
            raise BizException("必须选择支付/收款方式")

    @staticmethod
    def assert_cancellable(old: int, *, with_force: bool = False) -> None:
        """撤销校验：终态 5/4/9 不可撤；3 已支付需 with_force=True。"""
        if old in (FIN_CANCELLED, FIN_SETTLED, FIN_VOIDED):
            raise BizException(f"「{label(old)}」为终态，不可撤销")
        if old == FIN_PAID and not with_force:
            raise BizException("已支付单据需走「强制撤销」（高权限）")

    @staticmethod
    def assert_not_locked(is_locked: Optional[int]) -> None:
        """is_locked=1 时拒绝任何修改。"""
        if int(is_locked or 0) == 1:
            raise BizException("单据已锁定，禁止修改；请先解锁并记录原因")

    @staticmethod
    def legal_next(doc_kind: str, old: int) -> Set[int]:
        """UI 联动用：返回当前状态允许跳转的下一步集合（已按 doc_kind 裁剪）。"""
        allowed = set(FIN_VALID_TRANS.get(old, set()))
        kind_states = DOC_KIND_STATES.get(doc_kind)
        if kind_states is not None:
            allowed &= kind_states
        return allowed
