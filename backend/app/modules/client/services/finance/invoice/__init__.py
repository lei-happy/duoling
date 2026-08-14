"""发票域 Service（进项，销项在第 4 期补）"""

from app.modules.client.services.finance.invoice.vendor_invoice_service import (
    VendorInvoiceService,
)

__all__ = ["VendorInvoiceService"]
