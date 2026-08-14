import type { PageParam } from '@/api';
import type { FinanceDocEvent } from '@/api/finance/customer-recon/model';

export type { FinanceDocEvent };

/** 可并入结算的已确认对账单 */
export interface CarrierSettleReconCandidate {
  reconId: number;
  docNo: string;
  periodStart?: string;
  periodEnd?: string;
  taskCount: number;
  grossAmountTotal: number;
  prepaidOffsetTotal: number;
  plannedAmount: number;
  appliedAmountTotal: number;
  availableAmount: number;
  confirmedByCarrierAt?: string;
  diffForcedCount: number;
}

/** 承运商结算账户 */
export interface CarrierAccount {
  accountId: number;
  accountLabel?: string;
  accountType: number;
  settlementType: number;
  settlementTypeLabel?: string;
  bankName?: string;
  bankAccountMasked?: string;
  bankAccountName?: string;
  isDefault: number;
}

/** 结算单关联的对账单 */
export interface CarrierSettleReconLink {
  id: number;
  settleId: number;
  reconId: number;
  reconDocNo?: string;
  appliedAmount: number;
  remark?: string;
}

/** 结算单已核销的进项票 */
export interface SettleInvoiceLink {
  id: number;
  invoiceId: number;
  settleId: number;
  appliedAmount: number;
  matchedAt?: string;
  matchedBy?: number;
  remark?: string;
}

export interface CarrierSettleListItem {
  id: number;
  docNo: string;
  carrierId: number;
  carrierName?: string;
  enterpriseId?: number;
  reconCount: number;
  plannedAmount: number;
  paidAmountTotal: number;
  unpaidAmount: number;
  actualAmount?: number;
  paidAt?: string;
  payMethod?: number;
  payMethodLabel?: string;
  settlementAccountLabel?: string;
  bankAccountMasked?: string;
  dueDate?: string;
  isOffsetOnly: number;
  invoiceMatched: number;
  invoiceAmountTotal: number;
  invoiceGapAmount: number;
  batchId?: number;
  status: number;
  statusLabel?: string;
  createdBy?: number;
  createdAt?: string;
  remark?: string;
}

export interface CarrierSettleActionFlags {
  canEdit?: boolean;
  canDelete?: boolean;
  canSubmit?: boolean;
  canApprove?: boolean;
  canReject?: boolean;
  canWithdraw?: boolean;
  canPay?: boolean;
  canCancelPayment?: boolean;
  canCancel?: boolean;
  canForceCancel?: boolean;
  canLinkRecon?: boolean;
}

export interface CarrierSettleDetail extends CarrierSettleListItem {
  settlementAccountId?: number;
  bankName?: string;
  payVoucherUrl?: string;
  submittedAt?: string;
  reviewedBy?: number;
  reviewedAt?: string;
  cancelReason?: string;
  recons: CarrierSettleReconLink[];
  invoices: SettleInvoiceLink[];
  actions: CarrierSettleActionFlags;
}

export interface CarrierSettleParam extends PageParam {
  keyword?: string;
  carrierId?: number;
  enterpriseId?: number;
  status?: number;
  dueBefore?: string;
  /** 0 只看未收齐票，1 只看票款相符 */
  invoiceMatched?: number;
}

export interface CarrierSettleReconItem {
  reconId: number;
  appliedAmount?: number;
  remark?: string;
}

export interface CarrierSettleCreatePayload {
  carrierId: number;
  recons: CarrierSettleReconItem[];
  settlementAccountId?: number;
  dueDate?: string;
  isOffsetOnly?: number;
  remark?: string;
}

export interface CarrierSettleUpdatePayload {
  dueDate?: string;
  isOffsetOnly?: number;
  remark?: string;
}

export interface CarrierSettlePayPayload {
  actualAmount?: number;
  paidAt?: string;
  payMethod?: number;
  settlementAccountId?: number;
  payVoucherUrl?: string;
}
