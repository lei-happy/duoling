"""客户侧应收 service 包（文档 02 / 10 / 12）

- ``customer_recon_service``：客户对账单（事项确认），并向核对器注册客户侧绑定；
- ``customer_settlement_service``：客户结算单（金额确认与收款）；
- ``customer_invoice_service``：销项发票（开票申请、开票、作废与红冲）；
- ``receipt_voucher_service``：银行到账登记与核销；
- ``aging_service``：应收账龄聚合；
- ``credit_alert_service``：信用与账期预警（只提示不拦截）。

导入本包即完成核对器的客户侧绑定注册，业务侧置脏调用随之生效。
"""

from app.modules.client.services.finance.customer.aging_service import AgingService
from app.modules.client.services.finance.customer.credit_alert_service import (
    AlertLevel,
    AlertScene,
    CreditAlertService,
)
from app.modules.client.services.finance.customer.customer_invoice_service import (
    CustomerInvoiceService,
)
from app.modules.client.services.finance.customer.customer_recon_service import (
    CustomerReconService,
)
from app.modules.client.services.finance.customer.customer_settlement_service import (
    CustomerSettlementService,
)
from app.modules.client.services.finance.customer.receipt_voucher_service import (
    ReceiptVoucherService,
)

__all__ = [
    "AgingService",
    "AlertLevel",
    "AlertScene",
    "CreditAlertService",
    "CustomerInvoiceService",
    "CustomerReconService",
    "CustomerSettlementService",
    "ReceiptVoucherService",
]
