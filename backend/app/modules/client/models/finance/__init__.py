"""
财务单据模型包（租户库）

**通用基座**

- ``finance_doc_base.FinanceDocBaseMixin``：所有财务单据共享的通用字段集（mixin，不映射表）。
- ``finance_doc_event.FinanceDocEvent``：财务单据领域内的审计事实流（append-only）。
- ``recon_diff.ReconDiff``：对账单与业务事实的差异记录（非单据，无金额流程）。

**客户侧应收（第 2 期）**

- ``customer_recon``：客户对账单主表与对账行（事项确认）。
- ``customer_settlement``：客户结算单主表与对账单桥接（金额确认，账龄原子单位）。
- ``receipt_voucher``：收款单与核销桥接（到账事实）。

**应付侧（第 3 期）**

- ``carrier_recon``：承运商对账单主表与对账行（含预付扣减）。
- ``carrier_settlement_doc``：承运商结算单与对账单桥接（表名带 ``_doc`` 以避开结算账户表）。
- ``driver_payroll``：司机工资单、任务提成行与工资项明细。
- ``vendor_invoice``：进项发票、行明细与结算单核销桥接。

**销项与资金（第 4 期）**

- ``customer_invoice``：客户发票、行明细与结算单桥接（销项，与进项分表）。
- ``bank_account``：企业银行账户（主数据，不是单据，故不继承 mixin）。
- ``payment_batch``：打款批次与批次明细（一次付款动作的执行记录）。

具体单据表通过 mixin 复用字段集，避免每类单据各写一套草稿/审批/支付字段。
"""

from app.modules.client.models.finance.bank_account import BankAccount
from app.modules.client.models.finance.carrier_recon import (
    CarrierRecon,
    CarrierReconTaskLink,
)
from app.modules.client.models.finance.carrier_settlement_doc import (
    CarrierSettleReconLink,
    CarrierSettlementDoc,
)
from app.modules.client.models.finance.customer_invoice import (
    CustomerInvoice,
    CustomerInvoiceItem,
    CustomerInvoiceSettleLink,
)
from app.modules.client.models.finance.customer_recon import (
    CustomerRecon,
    CustomerReconWaybillLink,
)
from app.modules.client.models.finance.customer_settlement import (
    CustomerSettleReconLink,
    CustomerSettlement,
)
from app.modules.client.models.finance.driver_payroll import (
    DriverPayroll,
    DriverPayrollItem,
    DriverPayrollTaskLink,
)
from app.modules.client.models.finance.finance_doc_base import (
    FinanceDocBaseMixin,
)
from app.modules.client.models.finance.finance_doc_event import FinanceDocEvent
from app.modules.client.models.finance.payment_batch import (
    PaymentBatch,
    PaymentBatchItem,
)
from app.modules.client.models.finance.receipt_voucher import (
    ReceiptSettleLink,
    ReceiptVoucher,
)
from app.modules.client.models.finance.recon_diff import ReconDiff
from app.modules.client.models.finance.vendor_invoice import (
    VendorInvoice,
    VendorInvoiceItem,
    VendorInvoiceSettleLink,
)

__all__ = [
    "FinanceDocBaseMixin",
    "FinanceDocEvent",
    "ReconDiff",
    "CustomerRecon",
    "CustomerReconWaybillLink",
    "CustomerSettlement",
    "CustomerSettleReconLink",
    "ReceiptVoucher",
    "ReceiptSettleLink",
    "CarrierRecon",
    "CarrierReconTaskLink",
    "CarrierSettlementDoc",
    "CarrierSettleReconLink",
    "DriverPayroll",
    "DriverPayrollTaskLink",
    "DriverPayrollItem",
    "VendorInvoice",
    "VendorInvoiceItem",
    "VendorInvoiceSettleLink",
    "CustomerInvoice",
    "CustomerInvoiceItem",
    "CustomerInvoiceSettleLink",
    "BankAccount",
    "PaymentBatch",
    "PaymentBatchItem",
]
