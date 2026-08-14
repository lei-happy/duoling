import type { PageParam } from '@/api';

/** 可加入对账的运单候选 */
export interface ReconCandidate {
  waybillId: number;
  waybillNo?: string;
  customerId?: number;
  origin?: string;
  destination?: string;
  dealerName?: string;
  quantity: number;
  signedQuantity: number;
  signedAt?: string;
  freightAmount?: number;
  status: number;
}

/** 对账行 */
export interface ReconLine {
  id: number;
  reconId: number;
  waybillId: number;
  waybillNo?: string;
  billingBase: number;
  billingBaseLabel?: string;
  quantity: number;
  unitPrice: number;
  amount: number;
  adjustAmount: number;
  adjustReason?: string;
  freightAmountSnapshot?: number;
  signedQuantitySnapshot?: number;
  lockedSnapshotAt?: string;
  reconDirty: number;
  dirtyReason?: string;
  dirtyAt?: string;
  remark?: string;
}

/** 对账单列表行 */
export interface ReconListItem {
  id: number;
  docNo: string;
  customerId: number;
  customerName?: string;
  enterpriseId?: number;
  periodStart?: string;
  periodEnd?: string;
  waybillCount: number;
  totalQuantity: number;
  plannedAmount: number;
  adjustAmountTotal: number;
  appliedAmountTotal: number;
  receivedAmountTotal: number;
  settleCount: number;
  dirtyLineCount: number;
  diffOpenCount: number;
  diffForcedCount: number;
  confirmedByCustomerAt?: string;
  status: number;
  statusLabel?: string;
  createdBy?: number;
  createdAt?: string;
  remark?: string;
}

/** 按钮位：由后端状态机推导，前端不自己判状态 */
export interface ReconActionFlags {
  canEdit?: boolean;
  canDelete?: boolean;
  canConfirm?: boolean;
  canForceConfirm?: boolean;
  canCustomerSign?: boolean;
  canWithdraw?: boolean;
  canCancel?: boolean;
  canUnlockSettled?: boolean;
  canCheck?: boolean;
  canRecalc?: boolean;
  needAdjustApproval?: boolean;
}

/** 对账单详情 */
export interface ReconDetail extends ReconListItem {
  settlementType?: number;
  confirmedByCustomerName?: string;
  confirmVoucherUrl?: string;
  customerContactName?: string;
  customerContactPhone?: string;
  adjustApprovedBy?: number;
  adjustApprovedAt?: string;
  cancelReason?: string;
  lines: ReconLine[];
  actions: ReconActionFlags;
  /** 回灌重算接口会附带本次刷新的行数 */
  refreshedLines?: number;
}

export interface ReconParam extends PageParam {
  keyword?: string;
  customerId?: number;
  enterpriseId?: number;
  status?: number;
  periodStart?: string;
  periodEnd?: string;
  onlyDirty?: boolean;
  onlyDiff?: boolean;
  onlyUnsigned?: boolean;
}

export interface ReconCreatePayload {
  customerId: number;
  periodStart: string;
  periodEnd: string;
  waybillIds: number[];
  billingBase?: number;
  remark?: string;
}

export interface ReconUpdatePayload {
  periodStart?: string;
  periodEnd?: string;
  customerContactName?: string;
  customerContactPhone?: string;
  remark?: string;
}

export interface ReconLineAdjustPayload {
  quantity?: number;
  unitPrice?: number;
  adjustAmount?: number;
  adjustReason?: string;
  remark?: string;
}

export interface ReconCustomerSignPayload {
  signerName: string;
  voucherUrl?: string;
  signedAt?: string;
}

/** 一条对账差异 */
export interface ReconDiff {
  id: number;
  reconKind: string;
  reconId?: number;
  reconDocNo?: string;
  linkId?: number;
  bizDocType: number;
  bizDocTypeLabel?: string;
  bizDocId: number;
  bizDocNo?: string;
  diffType: number;
  diffTypeLabel?: string;
  severity: number;
  severityLabel?: string;
  expectedValue?: string;
  actualValue?: string;
  diffAmount?: number;
  detectedAt?: string;
  detectedBy?: number;
  isManual: number;
  status: number;
  statusLabel?: string;
  resolution?: string;
  resolvedBy?: number;
  resolvedAt?: string;
}

/** 一次一致性核对的结论 */
export interface ReconCheckReport {
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

export interface ReconDiffRaisePayload {
  bizDocId: number;
  diffType: number;
  bizDocNo?: string;
  linkId?: number;
  expectedValue?: string;
  actualValue?: string;
  diffAmount?: number;
  severity?: number;
}

export interface ReconDiffResolvePayload {
  status: number;
  resolution: string;
}

/** 单据审计事件（详情抽屉「操作记录」） */
export interface FinanceDocEvent {
  id: number;
  eventType: number;
  fromStatus?: number;
  toStatus?: number;
  occurredAmount?: number;
  operatorId?: number;
  operatorName?: string;
  reason?: string;
  eventTime?: string;
}
