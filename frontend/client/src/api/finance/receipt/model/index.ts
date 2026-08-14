import type { PageParam } from '@/api';
import type { FinanceDocEvent } from '@/api/finance/customer-recon/model';

export type { FinanceDocEvent };

/** 收款单已核销到的结算单 */
export interface ReceiptSettleLink {
  id: number;
  receiptId: number;
  settleId: number;
  settleDocNo?: string;
  appliedAmount: number;
  settledAt?: string;
  settledBy?: number;
  remark?: string;
}

export interface ReceiptListItem {
  id: number;
  docNo: string;
  customerId?: number;
  customerName?: string;
  payerName?: string;
  bankAccountId?: number;
  bankAccountLabel?: string;
  receivedAt?: string;
  receiveMethod?: number;
  receiveMethodLabel?: string;
  bankSerialNo?: string;
  plannedAmount: number;
  settledAmount: number;
  unsettledAmount: number;
  voucherUrl?: string;
  status: number;
  statusLabel?: string;
  createdBy?: number;
  createdAt?: string;
  remark?: string;
}

export interface ReceiptActionFlags {
  canEdit?: boolean;
  canDelete?: boolean;
  canClaim?: boolean;
  canUnclaim?: boolean;
  canCancel?: boolean;
}

export interface ReceiptDetail extends ReceiptListItem {
  cancelReason?: string;
  links: ReceiptSettleLink[];
  actions: ReceiptActionFlags;
}

/** 可核销的结算单候选 */
export interface ReceiptClaimCandidate {
  settleId: number;
  docNo: string;
  customerId?: number;
  customerName?: string;
  plannedAmount: number;
  receivedAmountTotal: number;
  unreceivedAmount: number;
  appliedByThisReceipt: number;
  dueDate?: string;
}

export interface ReceiptParam extends PageParam {
  keyword?: string;
  customerId?: number;
  status?: number;
  receivedStart?: string;
  receivedEnd?: string;
  onlyUnsettled?: boolean;
}

export interface ReceiptPayload {
  amount?: number;
  receivedAt?: string;
  receiveMethod?: number;
  customerId?: number;
  payerName?: string;
  bankAccountId?: number;
  bankAccountLabel?: string;
  bankSerialNo?: string;
  voucherUrl?: string;
  remark?: string;
}

export interface ReceiptAllocation {
  settleId: number;
  amount: number;
  remark?: string;
}

export interface ReceiptStats {
  pendingClaimCount: number;
  pendingClaimAmount: number;
  todayReceivedAmount: number;
}
