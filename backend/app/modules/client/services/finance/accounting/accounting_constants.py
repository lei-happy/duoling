"""经营核算口径常量（文档 13 §二）

口径写死在这里而不是散在查询里：核算的数字一旦对外报出去就不能变，纳入状态集改一个
值就会让上个月的报表对不上，必须集中一处、改动可见。
"""

from app.modules.client.services.finance.base.constants import DocType
from app.modules.client.services.finance.base.finance_state_machine import (
    FIN_PAID,
    FIN_REVIEWED,
    FIN_SETTLED,
)

# ===== 收入纳入 =====
# 对账单：已确认(2) / 已结清(3) 都算已确认收入（权责发生制主口径）
REVENUE_RECON_STATUSES = (FIN_REVIEWED, FIN_SETTLED)
# 结算单：已收款(3) 才算已实现收入（收付实现制口径）
REVENUE_SETTLE_STATUSES = (FIN_PAID,)

# ===== 成本纳入 =====
COST_CARRIER_SETTLE_STATUSES = (FIN_REVIEWED, FIN_PAID)
COST_PAYROLL_STATUSES = (FIN_REVIEWED, FIN_PAID)
COST_TASK_FINANCE_STATUSES = (FIN_PAID,)
# 预付单不计成本：它是资金流出不是成本发生，与结算单同计会翻倍（文档 13 §2.2）
COST_TASK_FINANCE_DOC_TYPES = (
    DocType.SUPPLEMENT, DocType.SETTLE, DocType.CONTRACTED,
)

# ===== 税率 =====
OUTPUT_TAX_RATE_CONFIG_KEY = "finance.default_output_tax_rate"
OUTPUT_TAX_RATE_CONFIG_GROUP = "finance"
OUTPUT_TAX_RATE_DESCRIPTION = (
    "默认销项税率（百分数）。未开票的收入按此税率折算不含税额，公路运输为 9"
)
DEFAULT_OUTPUT_TAX_RATE = 9
# 缺票税损用的进项税率：承运商开的运输专票同为 9%
DEFAULT_INPUT_TAX_RATE = 9

# ===== 维度 =====
DIM_CUSTOMER = "customer"
DIM_ENTITY = "entity"
DIM_ROUTE = "route"
DIM_VEHICLE = "vehicle"
DIM_DRIVER = "driver"
DIM_CARRIER_TYPE = "carrier_type"

DIMENSIONS = (
    DIM_CUSTOMER, DIM_ENTITY, DIM_ROUTE, DIM_VEHICLE, DIM_DRIVER, DIM_CARRIER_TYPE,
)
DIMENSION_LABELS = {
    DIM_CUSTOMER: "客户",
    DIM_ENTITY: "经营主体",
    DIM_ROUTE: "线路",
    DIM_VEHICLE: "车辆",
    DIM_DRIVER: "司机",
    DIM_CARRIER_TYPE: "承运类型",
}
# 需要把任务成本按台数摊到运单才能算的维度（其余直接取单据字段）
ALLOCATED_DIMENSIONS = (DIM_CUSTOMER, DIM_ROUTE)

CARRIER_TYPE_LABELS = {1: "自有车", 2: "承运商", 3: "社会运力"}

# 未分摊成本的维度值：空驶调令、无挂接行的任务成本都归这里
UNALLOCATED_KEY = "__unallocated__"
UNALLOCATED_LABEL = "未分摊成本"

# ===== 税口径 =====
TAX_MODE_INCL = "incl"
TAX_MODE_EXCL = "excl"
TAX_MODES = (TAX_MODE_INCL, TAX_MODE_EXCL)
