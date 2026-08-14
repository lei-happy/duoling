import type { PageParam } from '@/api';
import type { FinanceDocEvent } from '@/api/finance/customer-recon/model';

export type { FinanceDocEvent };

/** 可入批的应付单 */
export interface PayableCandidate {
  docKind: string;
  docKindLabel?: string;
  docId: number;
  docNo?: string;
  amount: number;
  payeeType: number;
  payeeId?: number;
  payeeName?: string;
  payeeBankName?: string;
  payeeBankAccount?: string;
  dueDate?: string;
  reviewedAt?: string;
  remark?: string;
}

export interface PaymentBatchItem {
  id: number;
  batchId: number;
  docKind: string;
  docKindLabel?: string;
  docId: number;
  docNo?: string;
  payeeType: number;
  payeeId?: number;
  payeeName?: string;
  payeeBankName?: string;
  payeeBankAccount?: string;
  amount: number;
  payMethod?: number;
  payMethodLabel?: string;
  execStatus: number;
  execStatusLabel?: string;
  failReason?: string;
  bankSerialNo?: string;
  paidAt?: string;
  remark?: string;
}

export interface PaymentBatchListItem {
  id: number;
  docNo: string;
  status: number;
  statusLabel?: string;
  enterpriseId?: number;
  bankAccountId?: number;
  bankAccountLabel?: string;
  payMethod?: number;
  payMethodLabel?: string;
  itemCount: number;
  successCount: number;
  failCount: number;
  totalAmount: number;
  paidAmount: number;
  planPayDate?: string;
  execStartedAt?: string;
  execFinishedAt?: string;
  createdBy?: number;
  createdAt?: string;
  remark?: string;
}

export interface PaymentBatchActionFlags {
  canEdit?: boolean;
  canDelete?: boolean;
  canSubmit?: boolean;
  canApprove?: boolean;
  canReject?: boolean;
  canExecute?: boolean;
  canCancel?: boolean;
  canAddItem?: boolean;
}

export interface PaymentBatchDetail extends PaymentBatchListItem {
  cancelReason?: string;
  items: PaymentBatchItem[];
  actions: PaymentBatchActionFlags;
}

export interface PaymentBatchParam extends PageParam {
  keyword?: string;
  status?: number;
  bankAccountId?: number;
  enterpriseId?: number;
  dateFrom?: string;
  dateTo?: string;
}

export interface PayableDocRef {
  docKind: string;
  docId: number;
}

export interface PaymentBatchCreatePayload {
  docs: PayableDocRef[];
  bankAccountId?: number;
  enterpriseId?: number;
  payMethod?: number;
  planPayDate?: string;
  remark?: string;
}

export interface PaymentBatchUpdatePayload {
  bankAccountId?: number;
  payMethod?: number;
  planPayDate?: string;
  remark?: string;
}

export interface BatchExecItem {
  itemId: number;
  success?: boolean;
  bankSerialNo?: string;
  paidAt?: string;
  payMethod?: number;
  failReason?: string;
}

/** 出纳台顶部指标 */
export interface CashierOverview {
  pendingClaimCount: number;
  pendingClaimAmount: number;
  todayReceivedAmount: number;
  accountCount: number;
  balanceTotal: number;
  payablePendingCount: number;
  payablePendingAmount: number;
  payableOverdueCount: number;
  batchWaitingCount: number;
  batchWaitingAmount: number;
  receivablePendingCount: number;
  receivablePendingAmount: number;
  todayPaidAmount: number;
  asOf?: string;
}

export interface FundFlowRow {
  flowId: string;
  direction: number;
  docKind?: string;
  docKindLabel?: string;
  docId?: number;
  docNo?: string;
  batchId?: number;
  batchDocNo?: string;
  counterparty?: string;
  amount: number;
  method?: number;
  methodLabel?: string;
  bankAccountId?: number;
  bankAccountLabel?: string;
  bankSerialNo?: string;
  occurredAt?: string;
  status?: number;
  remark?: string;
}

export interface FundFlowSummary {
  inAmount: number;
  outAmount: number;
  netAmount: number;
}

export interface FundFlowParam extends PageParam {
  direction?: number;
  bankAccountId?: number;
  dateFrom?: string;
  dateTo?: string;
  keyword?: string;
}

export interface PayCalendarDay {
  date: string;
  batchCount: number;
  batchAmount: number;
  docCount: number;
  docAmount: number;
  totalAmount: number;
}
