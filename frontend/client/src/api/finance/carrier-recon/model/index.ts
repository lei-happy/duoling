import type { PageParam } from '@/api';
import type {
  FinanceDocEvent,
  ReconDiff
} from '@/api/finance/customer-recon/model';

export type { FinanceDocEvent, ReconDiff };

/** 可加入对账的任务候选 */
export interface CarrierReconCandidate {
  taskId: number;
  taskNo?: string;
  plateNumber?: string;
  mainDriverName?: string;
  origin?: string;
  destination?: string;
  signedQuantity: number;
  signedAt?: string;
  carrierCostAmount?: number;
  prepaidOffsetAmount?: number;
  netAmount?: number;
  status: number;
}

/** 承运商对账行 */
export interface CarrierReconLine {
  id: number;
  reconId: number;
  taskId: number;
  taskNo?: string;
  plateNumber?: string;
  billingBase: number;
  billingBaseLabel?: string;
  quantity: number;
  unitPrice: number;
  grossAmount: number;
  adjustAmount: number;
  adjustReason?: string;
  prepaidOffsetAmount: number;
  netAmount: number;
  carrierCostSnapshot?: number;
  signedQuantitySnapshot?: number;
  signedAtSnapshot?: string;
  lockedSnapshotAt?: string;
  reconDirty: number;
  dirtyReason?: string;
  dirtyAt?: string;
  remark?: string;
}

/** 列表行 */
export interface CarrierReconListItem {
  id: number;
  docNo: string;
  carrierId: number;
  carrierName?: string;
  carrierShortName?: string;
  enterpriseId?: number;
  periodStart?: string;
  periodEnd?: string;
  taskCount: number;
  totalQuantity: number;
  grossAmountTotal: number;
  prepaidOffsetTotal: number;
  plannedAmount: number;
  adjustAmountTotal: number;
  appliedAmountTotal: number;
  paidAmountTotal: number;
  settleCount: number;
  dirtyLineCount: number;
  diffOpenCount: number;
  diffForcedCount: number;
  confirmedByCarrierAt?: string;
  settlementAccountLabel?: string;
  settlementTypeSnapshot?: number;
  settlementTypeLabel?: string;
  status: number;
  statusLabel?: string;
  createdBy?: number;
  createdAt?: string;
  remark?: string;
}

/** 按钮位：由后端状态机推导 */
export interface CarrierReconActionFlags {
  canEdit?: boolean;
  canDelete?: boolean;
  canConfirm?: boolean;
  canForceConfirm?: boolean;
  canCarrierSign?: boolean;
  canWithdraw?: boolean;
  canCancel?: boolean;
  canUnlockSettled?: boolean;
  canCheck?: boolean;
  canRecalc?: boolean;
  needAdjustApproval?: boolean;
}

export interface CarrierReconDetail extends CarrierReconListItem {
  settlementAccountId?: number;
  confirmedByCarrierName?: string;
  confirmVoucherUrl?: string;
  carrierContactName?: string;
  carrierContactPhone?: string;
  adjustApprovedBy?: number;
  adjustApprovedAt?: string;
  cancelReason?: string;
  lines: CarrierReconLine[];
  actions: CarrierReconActionFlags;
  refreshedLines?: number;
}

export interface CarrierReconParam extends PageParam {
  keyword?: string;
  carrierId?: number;
  enterpriseId?: number;
  status?: number;
  periodStart?: string;
  periodEnd?: string;
  onlyDirty?: boolean;
  onlyDiff?: boolean;
  onlyUnsigned?: boolean;
}

export interface CarrierReconCreatePayload {
  carrierId: number;
  periodStart: string;
  periodEnd: string;
  taskIds: number[];
  billingBase?: number;
  remark?: string;
}

export interface CarrierReconUpdatePayload {
  periodStart?: string;
  periodEnd?: string;
  carrierContactName?: string;
  carrierContactPhone?: string;
  settlementAccountId?: number;
  remark?: string;
}

export interface CarrierReconLineAdjustPayload {
  quantity?: number;
  unitPrice?: number;
  adjustAmount?: number;
  adjustReason?: string;
  remark?: string;
}

export interface CarrierSignPayload {
  signerName: string;
  voucherUrl?: string;
  signedAt?: string;
}

/** 一次一致性核对的结论 */
export interface CarrierReconCheckReport {
  reconId: number;
  reconKind: string;
  checkedLines: number;
  blockingCount: number;
  warningCount: number;
  dirtyLines: number;
  passed: boolean;
  checkedAt?: string;
  diffs: ReconDiff[];
}
