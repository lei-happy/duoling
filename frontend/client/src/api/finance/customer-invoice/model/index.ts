import type { PageParam } from '@/api';
import type { FinanceDocEvent } from '@/api/finance/customer-recon/model';

export type { FinanceDocEvent };

/** 开票行：金额三项任填两项，后端补第三项 */
export interface CustomerInvoiceItem {
  id: number;
  invoiceId: number;
  itemName?: string;
  taxRate?: number;
  amountExclTax: number;
  taxAmount: number;
  amountInclTax: number;
  sortOrder: number;
  remark?: string;
}

export interface CustomerInvoiceItemPayload {
  itemName?: string;
  taxRate?: number;
  amountExclTax?: number;
  taxAmount?: number;
  amountInclTax?: number;
  sortOrder?: number;
  remark?: string;
}

/** 发票已关联的结算单 */
export interface InvoiceSettleLink {
  id: number;
  invoiceId: number;
  settleId: number;
  settleDocNo?: string;
  appliedAmount: number;
  remark?: string;
}

/** 可开票的结算单候选 */
export interface InvoiceSettleCandidate {
  settleId: number;
  docNo: string;
  plannedAmount: number;
  invoicedAmount: number;
  availableAmount: number;
  appliedAmount: number;
  status: number;
  dueDate?: string;
  receivedAt?: string;
  invoiceRequired: number;
}

/** 待开票池一行 */
export interface PendingInvoiceSettle {
  settleId: number;
  docNo: string;
  customerId?: number;
  customerName?: string;
  plannedAmount: number;
  invoicedAmount: number;
  gapAmount: number;
  status: number;
  dueDate?: string;
  receivedAt?: string;
}

export interface CustomerInvoiceListItem {
  id: number;
  docNo: string;
  customerId: number;
  customerName?: string;
  sellerEntityId?: number;
  sellerTitle?: string;
  buyerTitle?: string;
  invoiceType: number;
  invoiceTypeLabel?: string;
  invoiceNo?: string;
  invoiceCode?: string;
  invoiceDate?: string;
  applicantAt?: string;
  issuedAt?: string;
  amountExclTax: number;
  taxRate?: number;
  taxAmount: number;
  amountInclTax: number;
  settleCount: number;
  isRedFlush: number;
  redFlushFromId?: number;
  status: number;
  statusLabel?: string;
  isLocked: number;
  createdBy?: number;
  createdAt?: string;
  remark?: string;
}

export interface CustomerInvoiceActionFlags {
  canEdit?: boolean;
  canDelete?: boolean;
  canSubmit?: boolean;
  canWithdraw?: boolean;
  canIssue?: boolean;
  canVoid?: boolean;
  canRedFlush?: boolean;
  canCancel?: boolean;
  canLink?: boolean;
}

export interface CustomerInvoiceDetail extends CustomerInvoiceListItem {
  sellerTaxNo?: string;
  buyerTaxNo?: string;
  buyerAddress?: string;
  buyerPhone?: string;
  buyerBank?: string;
  buyerAccount?: string;
  pdfUrl?: string;
  voidReason?: string;
  voidedAt?: string;
  cancelReason?: string;
  items: CustomerInvoiceItem[];
  settles: InvoiceSettleLink[];
  actions: CustomerInvoiceActionFlags;
  warning?: string | null;
}

export interface CustomerInvoiceParam extends PageParam {
  keyword?: string;
  customerId?: number;
  sellerEntityId?: number;
  status?: number;
  invoiceType?: number;
  dateFrom?: string;
  dateTo?: string;
  onlyRed?: boolean;
}

export interface InvoiceAllocation {
  settleId: number;
  appliedAmount?: number;
  remark?: string;
}

export interface CustomerInvoiceCreatePayload {
  customerId: number;
  allocations: InvoiceAllocation[];
  invoiceType?: number;
  sellerEntityId?: number;
  sellerTitle?: string;
  sellerTaxNo?: string;
  buyerTitle?: string;
  buyerTaxNo?: string;
  buyerAddress?: string;
  buyerPhone?: string;
  buyerBank?: string;
  buyerAccount?: string;
  taxRate?: number;
  items?: CustomerInvoiceItemPayload[];
  remark?: string;
}

export type CustomerInvoiceUpdatePayload = Omit<
  CustomerInvoiceCreatePayload,
  'customerId' | 'allocations'
>;

export interface InvoiceIssuePayload {
  invoiceNo: string;
  invoiceCode?: string;
  invoiceDate?: string;
  pdfUrl?: string;
}
