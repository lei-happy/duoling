"""财务单据域共享常量

集中维护 ``biz_task_finance_doc`` 相关的枚举值，避免 doc_type / payee_type /
pay_method 等业务码在各 service 内散落硬编码、跨模块重复定义。

值与 ``models/task/task_finance_doc.py`` 的列注释保持一致。
"""


class DocType:
    """单据类型（``task_finance_doc.doc_type``）"""

    PREPAY = 1        # 预付单
    SUPPLEMENT = 2    # 补款单
    SETTLE = 3        # 结算单
    CONTRACTED = 4    # 承包单

    ALL = (PREPAY, SUPPLEMENT, SETTLE, CONTRACTED)


class PayeeType:
    """收款人类型（``task_finance_doc.payee_type``）"""

    DRIVER = 1     # 司机
    CARRIER = 2    # 承运商
    OTHER = 3      # 其他（自由文本）


class PayMethod:
    """支付方式（``task_finance_doc.pay_method``）"""

    BANK_TRANSFER = 1  # 银行转账
    FUEL_CARD = 2      # 油卡
    FUEL_GAS = 3       # 油气款
    CASH = 4           # 现金
    WECHAT = 5         # 微信
    ALIPAY = 6         # 支付宝

    # 需强制上传支付凭证的方式（社会运力尾款合规）
    VOUCHER_REQUIRED = (CASH, WECHAT, ALIPAY)

    ALL = (BANK_TRANSFER, FUEL_CARD, FUEL_GAS, CASH, WECHAT, ALIPAY)

    LABELS = {
        BANK_TRANSFER: "银行转账",
        FUEL_CARD: "油卡",
        FUEL_GAS: "油气款",
        CASH: "现金",
        WECHAT: "微信",
        ALIPAY: "支付宝",
    }


class FinanceDirection:
    """收/付方向（``task_finance_doc.direction``）"""

    RECEIVE = 1  # 收款（应收）
    PAY = 2      # 付款（应付），任务级费用单恒为 2


class ReceiveMethod:
    """收款方式（应收侧，``customer_settlement.pay_method`` /
    ``receipt_voucher.receive_method``）

    与应付侧 ``PayMethod`` 分开：收款不会有油卡/油气款，付款不会有承兑汇票，
    共用一套枚举会让下拉里出现明显不该出现的选项。
    """

    BANK_TRANSFER = 1  # 银行转账
    CASH = 2           # 现金
    CHECK = 3          # 支票
    ACCEPTANCE = 4     # 承兑汇票
    PLATFORM = 5       # 平台代收

    ALL = (BANK_TRANSFER, CASH, CHECK, ACCEPTANCE, PLATFORM)

    LABELS = {
        BANK_TRANSFER: "银行转账",
        CASH: "现金",
        CHECK: "支票",
        ACCEPTANCE: "承兑汇票",
        PLATFORM: "平台代收",
    }


class BillingBase:
    """对账行计费基础（``customer_recon_waybill_link.billing_base``）"""

    BY_VEHICLE = 1  # 按台
    BY_TON = 2      # 按吨
    BY_TRIP = 3     # 按趟
    FIXED = 4       # 固定金额

    ALL = (BY_VEHICLE, BY_TON, BY_TRIP, FIXED)

    LABELS = {
        BY_VEHICLE: "按台",
        BY_TON: "按吨",
        BY_TRIP: "按趟",
        FIXED: "固定金额",
    }


class SettlementType:
    """客户结算方式（``biz_customer.settlement_type``）

    决定账期起算日：月结从对账周期止日起算，票结从开票日起算，预付按 0 天。
    见文档 12 §2.2。
    """

    MONTHLY = 0     # 月结
    BY_INVOICE = 1  # 票结
    PREPAY = 2      # 预付

    ALL = (MONTHLY, BY_INVOICE, PREPAY)

    LABELS = {MONTHLY: "月结", BY_INVOICE: "票结", PREPAY: "预付"}


class CarrierSettlementType:
    """承运商结算方式（``biz_carrier_settlement.settlement_type``）

    比客户侧多一个「趟结」：跑一趟结一趟是社会运力与个体车的常见方式。
    票结决定「先票后款」，进项票未收齐时打款批次要给警示（文档 11 §2.1）。
    """

    MONTHLY = 0     # 月结
    BY_INVOICE = 1  # 票结
    PREPAY = 2      # 预付
    BY_TRIP = 3     # 趟结

    ALL = (MONTHLY, BY_INVOICE, PREPAY, BY_TRIP)

    LABELS = {
        MONTHLY: "月结", BY_INVOICE: "票结", PREPAY: "预付", BY_TRIP: "趟结",
    }


class PayrollModel:
    """司机薪资模型（``driver_payroll.payroll_model``）"""

    FIXED = 1      # 月薪固定
    PIECE = 2      # 计件提成
    MIXED = 3      # 混合（底薪 + 提成）

    ALL = (FIXED, PIECE, MIXED)

    LABELS = {FIXED: "月薪固定", PIECE: "计件提成", MIXED: "底薪加提成"}


class PayrollPeriodType:
    """工资单发放周期（``driver_payroll.period_type``）"""

    MONTHLY = 1
    WEEKLY = 2
    BY_TRIP = 3

    ALL = (MONTHLY, WEEKLY, BY_TRIP)

    LABELS = {MONTHLY: "月薪", WEEKLY: "周薪", BY_TRIP: "趟薪"}


class PayrollItemCategory:
    """工资项分类（``driver_payroll_item.category``）

    金额一律填正数，加减由分类决定：扣减项与抵账项都从应发里减。两者分开是为了
    让工资条能分区展示——「扣了钱」和「已经拿过的折抵」在司机看来是两件事。
    """

    ADDITION = 1   # 应发项（加项）
    DEDUCTION = 2  # 扣减项（罚款、社保）
    OFFSET = 3     # 抵账项（油气款、已领预付）

    ALL = (ADDITION, DEDUCTION, OFFSET)

    LABELS = {ADDITION: "应发项", DEDUCTION: "扣减项", OFFSET: "抵账项"}


# 工资项编码与默认名称、分类（文档 04 §3.2 的 payroll_item_type 字典）
PAYROLL_ITEM_TYPES: dict[str, tuple] = {
    "base_salary": ("底薪", PayrollItemCategory.ADDITION),
    "attendance": ("出勤奖", PayrollItemCategory.ADDITION),
    "commission_total": ("任务提成", PayrollItemCategory.ADDITION),
    "oil_subsidy": ("油补", PayrollItemCategory.ADDITION),
    "meal_subsidy": ("餐补", PayrollItemCategory.ADDITION),
    "safety_award": ("安全奖", PayrollItemCategory.ADDITION),
    "other_addition": ("其他补贴", PayrollItemCategory.ADDITION),
    "fine": ("违章扣款", PayrollItemCategory.DEDUCTION),
    "social_insurance": ("社保代扣", PayrollItemCategory.DEDUCTION),
    "other_deduction": ("其他扣款", PayrollItemCategory.DEDUCTION),
    "oil_card_offset": ("油气款抵账", PayrollItemCategory.OFFSET),
}

# 提成汇总项：金额由任务提成行汇总回填，不允许手工改
COMMISSION_ITEM_TYPE = "commission_total"


class InvoiceType:
    """发票类型（``vendor_invoice.invoice_type`` / 销项同值）"""

    PLAIN = 1        # 增值税普通发票
    SPECIAL = 2      # 增值税专用发票
    E_PLAIN = 3      # 电子普通发票
    E_SPECIAL = 4    # 电子专用发票
    OTHER = 5

    ALL = (PLAIN, SPECIAL, E_PLAIN, E_SPECIAL, OTHER)

    LABELS = {
        PLAIN: "增值税普票",
        SPECIAL: "增值税专票",
        E_PLAIN: "电子普票",
        E_SPECIAL: "电子专票",
        OTHER: "其他",
    }

    # 默认可抵扣的票种（专票类）
    DEDUCTIBLE_DEFAULT = (SPECIAL, E_SPECIAL)


class VendorType:
    """进项票供应商类型（``vendor_invoice.vendor_type``）"""

    CARRIER = 1   # 承运商
    SOCIAL = 2    # 社会运力
    OTHER = 3     # 其他供应商（油品、保险、维修等，本期只登记不核销）

    ALL = (CARRIER, SOCIAL, OTHER)

    LABELS = {CARRIER: "承运商", SOCIAL: "社会运力", OTHER: "其他供应商"}


class VerifyStatus:
    """发票验真状态（``vendor_invoice.verify_status``）"""

    UNVERIFIED = 0
    PASSED = 1
    MISMATCH = 2

    ALL = (UNVERIFIED, PASSED, MISMATCH)

    LABELS = {UNVERIFIED: "未验真", PASSED: "已验真", MISMATCH: "验真不符"}


class BankAccountType:
    """银行账户类型（``bank_account.account_type``）"""

    BASIC = 1     # 基本户
    GENERAL = 2   # 一般户
    SPECIAL = 3   # 专用户
    OTHER = 4

    ALL = (BASIC, GENERAL, SPECIAL, OTHER)

    LABELS = {BASIC: "基本户", GENERAL: "一般户", SPECIAL: "专用户", OTHER: "其他"}


class AccountUsageScope:
    """银行账户用途（``bank_account.usage_scope``）

    收付通用是常态；分开是给「专门收客户回款」「专门付运费」的账户用，下拉时按
    用途过滤，免得出纳把付款账户选成收款账户。
    """

    BOTH = 1        # 收付通用
    RECEIVE_ONLY = 2  # 仅收款
    PAY_ONLY = 3      # 仅付款

    ALL = (BOTH, RECEIVE_ONLY, PAY_ONLY)

    LABELS = {BOTH: "收付通用", RECEIVE_ONLY: "仅收款", PAY_ONLY: "仅付款"}


class BatchExecStatus:
    """打款批次明细执行状态（``payment_batch_item.exec_status``）"""

    PENDING = 0  # 待执行
    SUCCESS = 1  # 成功
    FAILED = 2   # 失败

    ALL = (PENDING, SUCCESS, FAILED)

    LABELS = {PENDING: "待执行", SUCCESS: "成功", FAILED: "失败"}


class PayableDocKind:
    """打款批次可打包的应付单据大类（``payment_batch_item.doc_kind``）

    弱关联而非外键：一个批次里可以同时有任务费用单、承运商结算单与司机工资单。
    """

    TASK_FINANCE = "task_finance"
    CARRIER_SETTLE = "carrier_settle"
    DRIVER_PAYROLL = "driver_payroll"

    ALL = (TASK_FINANCE, CARRIER_SETTLE, DRIVER_PAYROLL)

    LABELS = {
        TASK_FINANCE: "任务费用单",
        CARRIER_SETTLE: "承运商结算单",
        DRIVER_PAYROLL: "司机工资单",
    }


class CreditStatus:
    """客户信用状态（``biz_customer.credit_status``）

    三个值都只作为提示依据，**不阻断任何业务操作**（文档 12 §1.2）。
    """

    SUSPENDED = 0  # 暂停合作
    NORMAL = 1     # 正常
    WATCH = 2      # 重点关注

    ALL = (SUSPENDED, NORMAL, WATCH)

    LABELS = {SUSPENDED: "暂停合作", NORMAL: "正常", WATCH: "重点关注"}
