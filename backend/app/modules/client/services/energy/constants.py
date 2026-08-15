"""能源中心常量：能源类型、账户类型、流水类型、匹配/对账/风控状态"""

from __future__ import annotations

from decimal import Decimal


# ---- 能源类型 ----
ENERGY_OIL = "OIL"
ENERGY_GAS = "GAS"
ENERGY_ELECTRIC = "ELECTRIC"
ENERGY_OTHER = "OTHER"

ENERGY_TYPES = [
    {"value": ENERGY_OIL, "label": "油品", "unit": "L"},
    {"value": ENERGY_GAS, "label": "燃气", "unit": "kg"},
    {"value": ENERGY_ELECTRIC, "label": "电力", "unit": "kWh"},
    {"value": ENERGY_OTHER, "label": "其他", "unit": ""},
]

ENERGY_TYPE_UNITS = {
    ENERGY_OIL: "L",
    ENERGY_GAS: "kg",
    ENERGY_ELECTRIC: "kWh",
    ENERGY_OTHER: "",
}

# ---- 供应商类型 ----
SUPPLIER_PETROLEUM = 1
SUPPLIER_GAS = 2
SUPPLIER_CHARGING = 3
SUPPLIER_PLATFORM = 4
SUPPLIER_PRIVATE_STATION = 5
SUPPLIER_OTHER = 9

SUPPLIER_TYPES = [
    {"value": SUPPLIER_PETROLEUM, "label": "石油石化"},
    {"value": SUPPLIER_GAS, "label": "燃气"},
    {"value": SUPPLIER_CHARGING, "label": "充电"},
    {"value": SUPPLIER_PLATFORM, "label": "能源平台"},
    {"value": SUPPLIER_PRIVATE_STATION, "label": "民营油站"},
    {"value": SUPPLIER_OTHER, "label": "其他"},
]

# ---- 账户类型 ----
ACCOUNT_PREPAID = "PREPAID"
ACCOUNT_POSTPAID = "POSTPAID"
ACCOUNT_CREDIT = "CREDIT"
ACCOUNT_CARD_POOL = "CARD_POOL"
ACCOUNT_VIRTUAL = "VIRTUAL"

ACCOUNT_TYPES = [
    {"value": ACCOUNT_PREPAID, "label": "预付账户"},
    {"value": ACCOUNT_POSTPAID, "label": "后付/月结"},
    {"value": ACCOUNT_CREDIT, "label": "授信账户"},
    {"value": ACCOUNT_CARD_POOL, "label": "卡资金池"},
    {"value": ACCOUNT_VIRTUAL, "label": "虚拟账户"},
]

# 允许账面余额为负的账户类型
NEGATIVE_BALANCE_ACCOUNT_TYPES = {ACCOUNT_POSTPAID, ACCOUNT_CREDIT}

# ---- 账户 / 卡状态 ----
STATUS_DISABLED = 0
STATUS_NORMAL = 1
STATUS_FROZEN = 2
STATUS_CLOSED = 3
STATUS_LOST = 4
STATUS_UNACTIVATED = 5

ACCOUNT_STATUSES = [
    {"value": STATUS_NORMAL, "label": "正常"},
    {"value": STATUS_FROZEN, "label": "冻结"},
    {"value": STATUS_DISABLED, "label": "停用"},
    {"value": STATUS_CLOSED, "label": "已关闭"},
]

CARD_STATUSES = [
    {"value": STATUS_UNACTIVATED, "label": "未激活"},
    {"value": STATUS_NORMAL, "label": "正常"},
    {"value": STATUS_FROZEN, "label": "冻结"},
    {"value": STATUS_LOST, "label": "挂失"},
    {"value": STATUS_DISABLED, "label": "停用"},
    {"value": STATUS_CLOSED, "label": "已注销"},
]

# ---- 账户流水类型 ----
TXN_RECHARGE = 1
TXN_CONSUMPTION = 2
TXN_REFUND = 3
TXN_TRANSFER_IN = 4
TXN_TRANSFER_OUT = 5
TXN_ADJUSTMENT = 6
TXN_REVERSAL = 7
TXN_FREEZE = 8
TXN_UNFREEZE = 9
TXN_FEE = 10

TXN_TYPES = [
    {"value": TXN_RECHARGE, "label": "充值"},
    {"value": TXN_CONSUMPTION, "label": "消费"},
    {"value": TXN_REFUND, "label": "退款"},
    {"value": TXN_TRANSFER_IN, "label": "转入"},
    {"value": TXN_TRANSFER_OUT, "label": "转出"},
    {"value": TXN_ADJUSTMENT, "label": "调账"},
    {"value": TXN_REVERSAL, "label": "冲正"},
    {"value": TXN_FREEZE, "label": "冻结"},
    {"value": TXN_UNFREEZE, "label": "解冻"},
    {"value": TXN_FEE, "label": "手续费"},
]

# 改变账面余额的方向：+1 入账 / -1 出账 / 0 仅改冻结
_TXN_LEDGER_SIGN = {
    TXN_RECHARGE: 1,
    TXN_CONSUMPTION: -1,
    TXN_REFUND: 1,
    TXN_TRANSFER_IN: 1,
    TXN_TRANSFER_OUT: -1,
    TXN_ADJUSTMENT: 0,  # 由调用方传入带符号 delta
    TXN_REVERSAL: 0,    # 由调用方传入带符号 delta
    TXN_FREEZE: 0,
    TXN_UNFREEZE: 0,
    TXN_FEE: -1,
}


def compute_ledger_delta(txn_type: int, amount: Decimal) -> Decimal:
    """计算账面余额变动额。

    调账 / 冲正由调用方直接传入带符号 ``amount``（此时 txn_type 的符号表为 0）。
    冻结 / 解冻不改账面余额。
    """
    amt = Decimal(amount)
    sign = _TXN_LEDGER_SIGN.get(int(txn_type))
    if sign is None:
        raise ValueError(f"未知流水类型: {txn_type}")
    if sign == 0 and int(txn_type) in (TXN_ADJUSTMENT, TXN_REVERSAL):
        return amt
    return amt.copy_abs() * sign


def compute_frozen_delta(txn_type: int, amount: Decimal) -> Decimal:
    """计算冻结金额变动额。冻结 +、解冻 -，其余为 0。"""
    amt = Decimal(amount).copy_abs()
    if int(txn_type) == TXN_FREEZE:
        return amt
    if int(txn_type) == TXN_UNFREEZE:
        return -amt
    return Decimal("0")


def reversal_deltas(original_ledger_delta: Decimal, original_frozen_delta: Decimal) -> tuple[Decimal, Decimal]:
    """冲正：原流水的反向变动。"""
    return -Decimal(original_ledger_delta), -Decimal(original_frozen_delta)


# ---- 消费来源渠道 ----
CHANNEL_CONNECTOR = 1
CHANNEL_EXCEL = 2
CHANNEL_MANUAL = 3
CHANNEL_DRIVER_ADVANCE = 4
CHANNEL_MONTHLY_BILL = 5

SOURCE_CHANNELS = [
    {"value": CHANNEL_CONNECTOR, "label": "供应商直连"},
    {"value": CHANNEL_EXCEL, "label": "Excel 导入"},
    {"value": CHANNEL_MANUAL, "label": "手工录入"},
    {"value": CHANNEL_DRIVER_ADVANCE, "label": "司机垫付引用"},
    {"value": CHANNEL_MONTHLY_BILL, "label": "月结账单"},
]

# ---- 匹配状态 ----
MATCH_MATCHED = "MATCHED"
MATCH_PARTIAL = "PARTIAL"
MATCH_UNMATCHED = "UNMATCHED"
MATCH_CONFLICT = "CONFLICT"

# ---- 对账结果 ----
RECON_MATCHED = "MATCHED"
RECON_MISSING_INTERNAL = "MISSING_INTERNAL"
RECON_MISSING_EXTERNAL = "MISSING_EXTERNAL"
RECON_AMOUNT_DIFF = "AMOUNT_DIFF"
RECON_QTY_DIFF = "QTY_DIFF"
RECON_DUPLICATED = "DUPLICATED"

RECON_TYPE_BALANCE = 1
RECON_TYPE_CONSUMPTION = 2

# ---- 风控规则编码 ----
RULE_OVER_TANK = "OVER_TANK"
RULE_REPEAT_FILL = "REPEAT_FILL"
RULE_ABNORMAL_PRICE = "ABNORMAL_PRICE"
RULE_ABNORMAL_CONSUMPTION = "ABNORMAL_CONSUMPTION"
RULE_UNBOUND_VEHICLE = "UNBOUND_VEHICLE"
RULE_UNBOUND_DRIVER = "UNBOUND_DRIVER"

# ---- 异常处理状态 ----
EXC_PENDING = "pending"
EXC_PROCESSED = "processed"
EXC_IGNORED = "ignored"

# ---- 同步任务状态 ----
SYNC_PENDING = "pending"
SYNC_RUNNING = "running"
SYNC_SUCCESS = "success"
SYNC_FAILED = "failed"

# ---- 原始数据处理状态 ----
RAW_PENDING = "pending"
RAW_PROCESSED = "processed"
RAW_DUPLICATE = "duplicate"
RAW_FAILED = "failed"

# ---- 归集维度 ----
DIM_VEHICLE = "vehicle"
DIM_DRIVER = "driver"
DIM_TASK = "task"
DIM_WAYBILL = "waybill"
DIM_ROUTE = "route"
DIM_SUPPLIER = "supplier"

# ---- 单据大类 ----
DOC_KIND_RECHARGE = "energy_recharge"
DOC_KIND_RECON = "energy_recon"

# ---- 单据状态（复用财务通用码）----
DOC_DRAFT = 0
DOC_PENDING = 1
DOC_REVIEWED = 2
DOC_PAID = 3
DOC_CANCELLED = 4
DOC_SETTLED = 5
