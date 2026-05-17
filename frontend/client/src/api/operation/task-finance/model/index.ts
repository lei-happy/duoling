import type { PageParam } from '@/api';

export interface TaskFinanceItem {
  id?: number;
  financeDocId?: number;
  itemType: string;
  itemName?: string;
  quantity?: number | null;
  unit?: string;
  unitPrice?: number | null;
  amount: number;
  sortOrder?: number;
  remark?: string;
  createdAt?: string;
}

export interface TaskFinanceDoc {
  id?: number;
  taskId: number;
  docNo?: string;
  docType: number; // 1-预付单 2-补款单 3-结算单
  isFinal?: number;
  payeeType: number; // 1-司机 2-承运商 3-其他
  payeeId?: number | null;
  payeeName?: string;
  payeeAccountType?: number | null;
  payeeAccountId?: number | null;
  payeeBankName?: string;
  payeeBankAccountMasked?: string;
  plannedAmount: number;
  actualAmount?: number | null;
  currency?: string;
  payMethod?: number | null;
  plannedPayTime?: string;
  actualPayTime?: string;
  payVoucherUrl?: string;
  status?: number;
  createdBy?: number;
  reviewedBy?: number;
  reviewedAt?: string;
  paidBy?: number;
  approvalNo?: string;
  remark?: string;
  createdAt?: string;
  items?: TaskFinanceItem[];
}

export interface TaskFinanceDocCreatePayload {
  docType: number;
  isFinal?: number;
  payeeType: number;
  payeeId?: number | null;
  payeeName?: string;
  payeeAccountType?: number | null;
  payeeAccountId?: number | null;
  payeeBankName?: string;
  payeeBankAccountMasked?: string;
  plannedAmount: number;
  currency?: string;
  payMethod?: number | null;
  plannedPayTime?: string;
  remark?: string;
  items: TaskFinanceItem[];
}

export type TaskFinanceDocUpdatePayload = Partial<TaskFinanceDocCreatePayload>;

export interface TaskFinanceDocPayPayload {
  actualAmount: number;
  payMethod: number;
  actualPayTime: string;
  payVoucherUrl?: string;
  remark?: string;
}

export interface TaskFinanceDocListItem {
  id: number;
  taskId: number;
  taskNo?: string;
  docNo: string;
  docType: number;
  isFinal: number;
  payeeType: number;
  payeeName?: string;
  plannedAmount: number;
  actualAmount?: number;
  payMethod?: number;
  status: number;
  createdAt: string;
  plannedPayTime?: string;
  actualPayTime?: string;
}

export interface TaskFinanceDocParam extends PageParam {
  keyword?: string;
  taskId?: number;
  docType?: number;
  status?: number;
  payeeType?: number;
  createdAtStart?: string;
  createdAtEnd?: string;
}

/** 费用工作台 KPI */
export interface TaskFinanceWorkbenchStats {
  statusCounts: Record<number, number>;
  totals: {
    draft: number;
    pendingReview: number;
    pendingPay: number;
    paid: number;
    cancelled: number;
  };
  amounts: {
    pendingReviewAmount: number;
    pendingPayAmount: number;
    todayPaidAmount: number;
  };
}

/** 批量动作请求 */
export interface TaskFinanceBatchActionPayload {
  ids: number[];
  action: 'approve' | 'pay' | 'cancel' | 'submit';
  actualAmount?: number;
  payMethod?: number;
  actualPayTime?: string;
  payVoucherUrl?: string;
  reason?: string;
  remark?: string;
}

export interface TaskFinanceBatchActionResult {
  success: number;
  failed: number;
  failures: Array<{ id: number; error: string }>;
}
