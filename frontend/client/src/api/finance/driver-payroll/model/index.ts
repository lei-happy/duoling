import type { PageParam } from '@/api';
import type { FinanceDocEvent } from '@/api/finance/customer-recon/model';

export type { FinanceDocEvent };

/** 可计提成的任务候选 */
export interface PayrollCandidate {
  taskId: number;
  taskNo?: string;
  plateNumber?: string;
  origin?: string;
  destination?: string;
  signedQuantity: number;
  signedAt?: string;
  prepaidPaidAmount?: number;
  status: number;
}

/** 发薪账户 */
export interface DriverAccount {
  accountId: number;
  accountType: number;
  accountTypeLabel?: string;
  accountName?: string;
  accountNoMasked?: string;
  balance?: number;
}

/** 任务提成行 */
export interface PayrollTaskLink {
  id: number;
  payrollId: number;
  taskId: number;
  taskNo?: string;
  plateNumber?: string;
  signedAt?: string;
  billingBase: number;
  billingBaseLabel?: string;
  quantity: number;
  unitPrice: number;
  commissionAmount: number;
  adjustAmount: number;
  adjustReason?: string;
  signedQuantitySnapshot?: number;
  remark?: string;
}

/** 工资项 */
export interface PayrollItem {
  id: number;
  payrollId: number;
  itemType: string;
  itemName?: string;
  category: number;
  categoryLabel?: string;
  amount: number;
  formula?: string;
  sortOrder: number;
  remark?: string;
  isSystem: boolean;
}

export interface PayrollListItem {
  id: number;
  docNo: string;
  driverId: number;
  driverName?: string;
  driverPhone?: string;
  enterpriseId?: number;
  payrollModel: number;
  payrollModelLabel?: string;
  periodType: number;
  periodTypeLabel?: string;
  periodStart?: string;
  periodEnd?: string;
  taskCount: number;
  totalSignedQuantity: number;
  totalCommissionAmount: number;
  totalBaseAmount: number;
  totalDeductionAmount: number;
  totalPrepaidOffsetAmount: number;
  grossAmount: number;
  netAmount: number;
  actualAmount?: number;
  paidAt?: string;
  payMethod?: number;
  payMethodLabel?: string;
  accountType?: number;
  accountTypeLabel?: string;
  accountNoMasked?: string;
  batchId?: number;
  status: number;
  statusLabel?: string;
  createdBy?: number;
  createdAt?: string;
  remark?: string;
}

export interface PayrollActionFlags {
  canEdit?: boolean;
  canDelete?: boolean;
  canSubmit?: boolean;
  canApprove?: boolean;
  canReject?: boolean;
  canWithdraw?: boolean;
  canPay?: boolean;
  canCancelPayment?: boolean;
  canCancel?: boolean;
  needAdjustApproval?: boolean;
}

export interface PayrollDetail extends PayrollListItem {
  accountId?: number;
  accountNameSnapshot?: string;
  payVoucherUrl?: string;
  payslipPdfUrl?: string;
  adjustApprovedBy?: number;
  adjustApprovedAt?: string;
  submittedAt?: string;
  reviewedBy?: number;
  reviewedAt?: string;
  cancelReason?: string;
  tasks: PayrollTaskLink[];
  items: PayrollItem[];
  actions: PayrollActionFlags;
}

export interface PayrollParam extends PageParam {
  keyword?: string;
  driverId?: number;
  enterpriseId?: number;
  status?: number;
  payrollModel?: number;
  periodStart?: string;
  periodEnd?: string;
}

export interface PayrollCreatePayload {
  driverId: number;
  periodStart: string;
  periodEnd: string;
  taskIds: number[];
  payrollModel?: number;
  periodType?: number;
  unitPrice?: number;
  billingBase?: number;
  accountId?: number;
  remark?: string;
}

export interface PayrollUpdatePayload {
  payrollModel?: number;
  periodType?: number;
  remark?: string;
}

export interface PayrollTaskAdjustPayload {
  quantity?: number;
  unitPrice?: number;
  adjustAmount?: number;
  adjustReason?: string;
  remark?: string;
}

export interface PayrollItemPayload {
  itemType: string;
  amount: number;
  itemName?: string;
  category?: number;
  formula?: string;
  sortOrder?: number;
  remark?: string;
}

export interface PayrollItemUpdatePayload {
  amount?: number;
  itemName?: string;
  formula?: string;
  sortOrder?: number;
  remark?: string;
}

export interface PayrollPayPayload {
  actualAmount?: number;
  paidAt?: string;
  payMethod?: number;
  accountId?: number;
  payVoucherUrl?: string;
}

/** 工资条一行 */
export interface PayslipLine {
  itemType: string;
  itemName?: string;
  amount: number;
  formula?: string;
}

/** 工资条：应发 / 扣减 / 抵账 三区 */
export interface Payslip {
  docNo: string;
  driverName?: string;
  periodStart?: string;
  periodEnd?: string;
  taskCount: number;
  totalSignedQuantity: number;
  additions: PayslipLine[];
  deductions: PayslipLine[];
  offsets: PayslipLine[];
  grossAmount: number;
  netAmount: number;
  accountType?: number;
  accountNoMasked?: string;
  paidAt?: string;
}
