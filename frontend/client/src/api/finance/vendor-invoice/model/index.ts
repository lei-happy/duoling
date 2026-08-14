import type { PageParam } from '@/api';
import type { FinanceDocEvent } from '@/api/finance/customer-recon/model';

export type { FinanceDocEvent };

/** 多税率发票行 */
export interface VendorInvoiceItem {
  id: number;
  invoiceId: number;
  itemName?: string;
  taxRate?: number;
  amountExclTax: number;
  taxAmount: number;
  amountInclTax: number;
  remark?: string;
}

export interface VendorInvoiceItemPayload {
  itemName?: string;
  taxRate: number;
  amountExclTax?: number;
  taxAmount?: number;
  amountInclTax?: number;
  remark?: string;
}

/** 核销明细 */
export interface InvoiceSettleLink {
  id: number;
  invoiceId: number;
  settleId: number;
  settleDocNo?: string;
  appliedAmount: number;
  matchedAt?: string;
  matchedBy?: number;
  remark?: string;
}

export interface VendorInvoiceListItem {
  id: number;
  docNo: string;
  vendorType: number;
  vendorTypeLabel?: string;
  vendorId?: number;
  vendorName?: string;
  sellerTitle?: string;
  buyerEntityId?: number;
  buyerTitle?: string;
  invoiceType: number;
  invoiceTypeLabel?: string;
  invoiceNo: string;
  invoiceCode?: string;
  invoiceDate?: string;
  receivedAt?: string;
  amountExclTax: number;
  taxRate?: number;
  taxAmount: number;
  amountInclTax: number;
  isMultiRate: number;
  settledAmount: number;
  unsettledAmount: number;
  settleCount: number;
  deductible: number;
  deductPeriod?: string;
  verifyStatus: number;
  verifyStatusLabel?: string;
  status: number;
  statusLabel?: string;
  createdBy?: number;
  createdAt?: string;
  remark?: string;
}

export interface VendorInvoiceActionFlags {
  canEdit?: boolean;
  canDelete?: boolean;
  canMatch?: boolean;
  canUnmatch?: boolean;
  canVoid?: boolean;
  canCancel?: boolean;
}

export interface VendorInvoiceDetail extends VendorInvoiceListItem {
  sellerTaxNo?: string;
  buyerTaxNo?: string;
  attachmentUrl?: string;
  voidReason?: string;
  voidedAt?: string;
  cancelReason?: string;
  items: VendorInvoiceItem[];
  settles: InvoiceSettleLink[];
  actions: VendorInvoiceActionFlags;
  /** 作废时若已过抵扣税期，后端会给一句提醒 */
  deductWarning?: string | null;
}

export interface VendorInvoiceParam extends PageParam {
  keyword?: string;
  vendorId?: number;
  vendorType?: number;
  buyerEntityId?: number;
  status?: number;
  invoiceType?: number;
  deductible?: number;
  deductPeriod?: string;
  dateFrom?: string;
  dateTo?: string;
  onlyUnsettled?: boolean;
}

export interface VendorInvoiceCreatePayload {
  invoiceNo: string;
  invoiceCode?: string;
  invoiceType?: number;
  invoiceDate?: string;
  receivedAt?: string;
  vendorType?: number;
  vendorId?: number;
  sellerTitle?: string;
  sellerTaxNo?: string;
  buyerEntityId?: number;
  buyerTitle?: string;
  buyerTaxNo?: string;
  amountExclTax?: number;
  taxAmount?: number;
  amountInclTax?: number;
  taxRate?: number;
  deductible?: number;
  deductPeriod?: string;
  attachmentUrl?: string;
  items?: VendorInvoiceItemPayload[];
  remark?: string;
}

export type VendorInvoiceUpdatePayload = Omit<
  VendorInvoiceCreatePayload,
  'invoiceNo' | 'invoiceCode' | 'receivedAt' | 'vendorType' | 'vendorId'
>;

/** 可核销的承运商结算单 */
export interface InvoiceMatchCandidate {
  settleId: number;
  docNo: string;
  plannedAmount: number;
  invoiceAmountTotal: number;
  gapAmount: number;
  status: number;
  paidAt?: string;
  dueDate?: string;
}

export interface InvoiceMatchPayload {
  allocations: { settleId: number; appliedAmount: number; remark?: string }[];
}

/** 抵扣台账汇总一行 */
export interface DeductSummaryRow {
  groupBy: string;
  groupKey?: string | number | null;
  invoiceCount: number;
  amountExclTax: number;
  taxAmount: number;
  amountInclTax: number;
}

/** 待收票的结算单 */
export interface PendingInvoiceSettle {
  settleId: number;
  docNo: string;
  carrierId?: number;
  carrierName?: string;
  plannedAmount: number;
  invoiceAmountTotal: number;
  gapAmount: number;
  paidAt?: string;
  paidDays?: number;
}
