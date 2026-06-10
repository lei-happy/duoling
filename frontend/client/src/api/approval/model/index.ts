import type { PageParam } from '@/api';

/** 审批实例状态：0-审批中 1-已通过 2-已拒绝 3-已撤回 */
export type ApprovalInstanceStatus = 0 | 1 | 2 | 3;

/** 列表查询参数 */
export interface ApprovalListParam extends PageParam {
  keyword?: string;
  bizType?: string;
  status?: number;
}

/** 列表项 */
export interface ApprovalListItem {
  instanceId: number;
  taskId?: number;
  instanceNo?: string;
  bizType: string;
  bizId: number;
  bizNo?: string;
  title?: string;
  initiatorId: number;
  initiatorName?: string;
  status: number;
  currentNodeOrder: number;
  summary?: Record<string, any> | null;
  submittedAt?: string;
  finishedAt?: string;
  createdAt?: string;
}

/** 审批任务（节点内单个审批人） */
export interface ApprovalTaskOut {
  id: number;
  nodeOrder: number;
  approverId: number;
  approverName?: string;
  assignSource: number;
  signOrder: number;
  status: number;
  comment?: string;
  actedAt?: string;
}

/** 审批节点 */
export interface ApprovalNodeOut {
  id: number;
  nodeOrder: number;
  nodeType: number;
  nodeName: string;
  signType: number;
  status: number;
  resolvedApproverIds?: number[];
  tasks: ApprovalTaskOut[];
}

/** 审批流水记录 */
export interface ApprovalRecordOut {
  id: number;
  nodeOrder: number;
  operatorId: number;
  operatorName?: string;
  action: number;
  targetUserId?: number;
  comment?: string;
  attachments?: any;
  createdAt?: string;
}

/** 抄送记录 */
export interface ApprovalCcOut {
  id: number;
  userId: number;
  userName?: string;
  isRead: number;
  createdAt?: string;
}

/** 实例详情 */
export interface ApprovalDetailOut {
  instanceId: number;
  instanceNo?: string;
  bizType: string;
  bizId: number;
  bizNo?: string;
  flowId?: number;
  initiatorId: number;
  initiatorName?: string;
  initiatorDeptId?: number;
  variables?: Record<string, any> | null;
  summary?: Record<string, any> | null;
  status: number;
  currentNodeOrder: number;
  resultComment?: string;
  submittedAt?: string;
  finishedAt?: string;
  myPendingTaskId?: number;
  canWithdraw: boolean;
  nodes: ApprovalNodeOut[];
  records: ApprovalRecordOut[];
  ccList: ApprovalCcOut[];
}

/** 审批动作入参 */
export interface ApprovalActionBody {
  comment?: string;
  attachments?: any;
}
export interface ApprovalRejectBody {
  comment: string;
  attachments?: any;
}
export interface ApprovalWithdrawBody {
  reason?: string;
}
export interface ApprovalTransferBody {
  targetUserId: number;
  comment?: string;
}
export interface ApprovalAddSignBody {
  targetUserId: number;
  mode?: 'before' | 'after';
  comment?: string;
}
export interface ApprovalCcBody {
  targetUserIds: number[];
}

// ---------------- 流程模板 ----------------
export interface FlowNode {
  id?: number;
  nodeOrder: number;
  nodeType: number;
  nodeName: string;
  approverType: number;
  approverConfig?: Record<string, any> | null;
  signType: number;
  condition?: Record<string, any> | null;
  emptyStrategy: number;
  allowTransfer: number;
  allowAddsign: number;
}

export interface FlowOut {
  id: number;
  bizType: string;
  flowName: string;
  flowCode?: string;
  condition?: Record<string, any> | null;
  priority: number;
  isDefault: number;
  allowWithdraw: number;
  withdrawScope: number;
  status: number;
  version: number;
  remark?: string;
  nodes: FlowNode[];
}

export interface FlowParam extends PageParam {
  bizType?: string;
  status?: number;
  keyword?: string;
}

export interface FlowCreateBody {
  bizType: string;
  flowName: string;
  flowCode?: string;
  condition?: Record<string, any> | null;
  priority?: number;
  isDefault?: number;
  allowWithdraw?: number;
  withdrawScope?: number;
  remark?: string;
  nodes: FlowNode[];
}

export type FlowUpdateBody = Partial<FlowCreateBody>;
