"""对账一致性核对域常量

集中维护 ``biz_recon_diff`` 的 diff_type / severity / status 取值与中文名，
避免核对器、对账 service、API 层各写一份枚举。

值与文档 ``09.运输单与财务单一致性核对`` §4.1 / §5.1 保持一致。
"""

from typing import Dict, Set


class ReconKind:
    """对账单大类（同 ``FinanceDocBaseMixin.doc_kind`` 中的对账类取值）"""

    CUSTOMER = "customer_recon"
    CARRIER = "carrier_recon"

    ALL = (CUSTOMER, CARRIER)


class BizDocType:
    """差异关联的业务单据类型（``biz_recon_diff.biz_doc_type``）"""

    WAYBILL = 1  # 运单
    TASK = 2     # 任务单

    LABELS: Dict[int, str] = {WAYBILL: "运单", TASK: "任务单"}


class DiffType:
    """差异类型（``biz_recon_diff.diff_type``），见文档 09 §4.1

    9~15 号段留给远期的银行流水比对类差异，勿占用。
    """

    MISSING = 1        # 漏挂：满足候选条件但未挂入任何对账单
    DUPLICATED = 2     # 重挂：同一业务单出现在两张非撤销对账单
    INELIGIBLE = 3     # 资格不符：已挂入但不满足纳入条件
    QUANTITY = 4       # 台数不符：快照台数 ≠ 当前签收台数
    MILEAGE = 5        # 里程不符：按公里计费行的数量 ≠ 当前调令里程
    AMOUNT = 6         # 金额不符：行金额 ≠ 计费引擎当前结果
    OFFSET = 7         # 扣减不符：预付扣减额 ≠ 当前已支付预付补款合计
    STATUS_REVERTED = 8  # 状态回退：关联业务单据已回退至未完成态

    ALL = (
        MISSING, DUPLICATED, INELIGIBLE, QUANTITY,
        MILEAGE, AMOUNT, OFFSET, STATUS_REVERTED,
    )

    LABELS: Dict[int, str] = {
        MISSING: "漏挂",
        DUPLICATED: "重挂",
        INELIGIBLE: "资格不符",
        QUANTITY: "台数不符",
        MILEAGE: "里程不符",
        AMOUNT: "金额不符",
        OFFSET: "扣减不符",
        STATUS_REVERTED: "状态回退",
    }


class DiffSeverity:
    """严重度（``biz_recon_diff.severity``）

    - ``WARNING``：不阻塞对账单确认，只在工作台与详情页提示；
    - ``BLOCKING``：对账单 0→2 确认被拒绝，除非走强制确认。
    """

    WARNING = 1
    BLOCKING = 2

    LABELS: Dict[int, str] = {WARNING: "提示", BLOCKING: "阻塞"}


# 各差异类型的默认严重度（文档 09 §4.1）
DEFAULT_SEVERITY: Dict[int, int] = {
    DiffType.MISSING: DiffSeverity.WARNING,
    DiffType.DUPLICATED: DiffSeverity.BLOCKING,
    DiffType.INELIGIBLE: DiffSeverity.BLOCKING,
    DiffType.QUANTITY: DiffSeverity.BLOCKING,
    DiffType.MILEAGE: DiffSeverity.WARNING,
    DiffType.AMOUNT: DiffSeverity.BLOCKING,
    DiffType.OFFSET: DiffSeverity.BLOCKING,
    DiffType.STATUS_REVERTED: DiffSeverity.BLOCKING,
}


class DiffStatus:
    """差异处置状态（``biz_recon_diff.status``），见文档 09 §5.2"""

    OPEN = 0        # 待处置
    RECALCED = 1    # 已回灌（重算后消解）
    NEGOTIATED = 2  # 已协商确认（手工调整并与对方确认）
    FORCED = 3      # 已强制放行（带差异确认对账单）
    INVALID = 4     # 已失效（业务侧改回 / 对账单撤销）

    # 终态集合：不可再流转，且不参与 dedup_key 去重
    CLOSED: Set[int] = {RECALCED, NEGOTIATED, FORCED, INVALID}

    LABELS: Dict[int, str] = {
        OPEN: "待处置",
        RECALCED: "已回灌",
        NEGOTIATED: "已协商确认",
        FORCED: "已强制放行",
        INVALID: "已失效",
    }


# 允许置脏 / 允许检出差异的对账单状态：仅草稿(0)与已确认(2)
# 已结清(3)/已撤销(4) 不再置脏——钱已经动过，差异要走「解锁结清」重走流程
CHECKABLE_RECON_STATUSES: Set[int] = {0, 2}


def diff_label(diff_type: int) -> str:
    return DiffType.LABELS.get(int(diff_type), f"差异{diff_type}")


def severity_of(diff_type: int) -> int:
    """返回差异类型的默认严重度，未登记类型按「提示」处理（保守不阻塞）。"""
    return DEFAULT_SEVERITY.get(int(diff_type), DiffSeverity.WARNING)
