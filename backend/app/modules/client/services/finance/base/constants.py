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


class FinanceDirection:
    """收/付方向（``task_finance_doc.direction``）"""

    RECEIVE = 1  # 收款（应收）
    PAY = 2      # 付款（应付），任务级费用单恒为 2
