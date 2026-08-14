"""企业端财务结算模块 API 汇总

各单据一个文件，在 ``client/api/__init__.py`` 统一挂载并按 feature 门控。
"""

from app.modules.client.api.finance.ar_aging import router as ar_aging_router
from app.modules.client.api.finance.bank_account import (
    router as bank_account_router,
)
from app.modules.client.api.finance.carrier_recon import (
    router as carrier_recon_router,
)
from app.modules.client.api.finance.carrier_settlement import (
    router as carrier_settlement_router,
)
from app.modules.client.api.finance.customer_invoice import (
    router as customer_invoice_router,
)
from app.modules.client.api.finance.customer_recon import (
    router as customer_recon_router,
)
from app.modules.client.api.finance.customer_settlement import (
    router as customer_settlement_router,
)
from app.modules.client.api.finance.driver_payroll import (
    router as driver_payroll_router,
)
from app.modules.client.api.finance.payment_batch import (
    router as payment_batch_router,
)
from app.modules.client.api.finance.profit_accounting import (
    router as profit_accounting_router,
)
from app.modules.client.api.finance.receipt_voucher import (
    router as receipt_voucher_router,
)
from app.modules.client.api.finance.recon_workbench import (
    router as recon_workbench_router,
)
from app.modules.client.api.finance.vendor_invoice import (
    router as vendor_invoice_router,
)

__all__ = [
    "ar_aging_router",
    "bank_account_router",
    "carrier_recon_router",
    "carrier_settlement_router",
    "customer_invoice_router",
    "customer_recon_router",
    "customer_settlement_router",
    "driver_payroll_router",
    "payment_batch_router",
    "profit_accounting_router",
    "receipt_voucher_router",
    "recon_workbench_router",
    "vendor_invoice_router",
]
