import type { PageParam } from '@/api';

/** 可并入结算的已确认对账单 */
export interface SettleReconCandidate {
  reconId: number;
  docNo: string;
  periodStart?: string;
  periodEnd?: string;
  waybillCount: number;
  plannedAmount: number;
  appliedAmountTotal: number;
  availableAmount: number;
  confirmedByCustomerAt?: string;
  diffForcedCount: number;
}

/** 结算单已关联的对账单 */
export interface SettleReconLink {
  id: number;
  settleId: number;
  reconId: number;
  reconDocNo?: string;
  appliedAmount: number;
  remark?: string;
}

/** 本单的到账构成（收款单核销明细） */
export interface SettleReceiptLink {
  id: number;
  receiptId: number;
  settleId: number;
  appliedAmount: number;
  settledAt?: string;
  settledBy?: number;
  remark?: string;
}

export interface SettleListItem {
  id: number;
  docNo: string;
  customerId: number;
  customerName?: string;
  enterpriseId?: number;
  reconCount: number;
  plannedAmount: number;
  receivedAmountTotal: number;
  unreceivedAmount: number;
  actualAmount?: number;
  receivedAt?: string;
  payMethod?: number;
  payMethodLabel?: string;
  receivedAccountLabel?: string;
  dueDate?: string;
  invoiceRequired: number;
  invoiceCount: number;
  status: number;
  statusLabel?: string;
  createdBy?: number;
  createdAt?: string;
  remark?: string;
}

export interface SettleActionFlags {
  canEdit?: boolean;
  canDelete?: boolean;
  canSubmit?: boolean;
  canApprove?: boolean;
  canReject?: boolean;
  canWithdraw?: boolean;
  canCancel?: boolean;
  canForceCancel?: boolean;
  canLinkRecon?: boolean;
  canReceive?: boolean;
  canClaimReceipt?: boolean;
  canCancelReceive?: boolean;
  canInvoice?: boolean;
  unreceivedAmount?: number;
}

export interface SettleDetail extends SettleListItem {
  receivedAccountId?: number;
  receivedVoucherUrl?: string;
  invoiceAmountTotal: number;
  submittedAt?: string;
  reviewedBy?: number;
  reviewedAt?: string;
  cancelReason?: string;
  recons: SettleReconLink[];
  receipts: SettleReceiptLink[];
  actions: SettleActionFlags;
}

export interface SettleParam extends PageParam {
  keyword?: string;
  customerId?: number;
  enterpriseId?: number;
  status?: number;
  dueBefore?: string;
  onlyUnreceived?: boolean;
  invoiceRequired?: number;
}

export interface SettleReconItemPayload {
  reconId: number;
  /** 留空表示认领该对账单全部未结金额 */
  appliedAmount?: number;
  remark?: string;
}

export interface SettleCreatePayload {
  customerId: number;
  recons: SettleReconItemPayload[];
  dueDate?: string;
  invoiceRequired?: number;
  remark?: string;
}

export interface SettleUpdatePayload {
  dueDate?: string;
  invoiceRequired?: number;
  remark?: string;
}

export interface SettleReceivePayload {
  actualAmount: number;
  receivedAt: string;
  receiveMethod: number;
  receivedAccountId?: number;
  receivedAccountLabel?: string;
  voucherUrl?: string;
}
