import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  ApprovalListParam,
  ApprovalListItem,
  ApprovalDetailOut,
  ApprovalActionBody,
  ApprovalRejectBody,
  ApprovalWithdrawBody,
  ApprovalTransferBody,
  ApprovalAddSignBody,
  ApprovalCcBody,
  FlowOut,
  FlowParam,
  FlowCreateBody,
  FlowUpdateBody,
  FlowVersionLog
} from './model';

const BASE = '/approval';

function unwrap<T>(res: { data: ApiResult<T> }): T {
  if (res.data.code === 0) {
    return res.data.data as T;
  }
  return Promise.reject(new Error(res.data.message)) as never;
}

// ---------------- 列表 ----------------
export async function listPending(params: ApprovalListParam) {
  const res = await request.get<ApiResult<PageResult<ApprovalListItem>>>(
    `${BASE}/pending`,
    { params }
  );
  return unwrap(res);
}

export async function pendingCount() {
  const res = await request.get<ApiResult<{ count: number }>>(
    `${BASE}/pending/count`
  );
  return unwrap(res);
}

export async function listInitiated(params: ApprovalListParam) {
  const res = await request.get<ApiResult<PageResult<ApprovalListItem>>>(
    `${BASE}/initiated`,
    { params }
  );
  return unwrap(res);
}

export async function listHistory(params: ApprovalListParam) {
  const res = await request.get<ApiResult<PageResult<ApprovalListItem>>>(
    `${BASE}/history`,
    { params }
  );
  return unwrap(res);
}

export async function getInstanceDetail(instanceId: number) {
  const res = await request.get<ApiResult<ApprovalDetailOut>>(
    `${BASE}/instance/${instanceId}`
  );
  return unwrap(res);
}

// ---------------- 审批动作 ----------------
export async function agreeTask(taskId: number, data?: ApprovalActionBody) {
  const res = await request.post<ApiResult<null>>(
    `${BASE}/task/${taskId}/agree`,
    data ?? {}
  );
  return unwrap(res);
}

export async function rejectTask(taskId: number, data: ApprovalRejectBody) {
  const res = await request.post<ApiResult<null>>(
    `${BASE}/task/${taskId}/reject`,
    data
  );
  return unwrap(res);
}

export async function transferTask(taskId: number, data: ApprovalTransferBody) {
  const res = await request.post<ApiResult<null>>(
    `${BASE}/task/${taskId}/transfer`,
    data
  );
  return unwrap(res);
}

export async function addSignTask(taskId: number, data: ApprovalAddSignBody) {
  const res = await request.post<ApiResult<null>>(
    `${BASE}/task/${taskId}/add-sign`,
    data
  );
  return unwrap(res);
}

export async function withdrawInstance(
  instanceId: number,
  data?: ApprovalWithdrawBody
) {
  const res = await request.post<ApiResult<null>>(
    `${BASE}/instance/${instanceId}/withdraw`,
    data ?? {}
  );
  return unwrap(res);
}

export async function ccInstance(instanceId: number, data: ApprovalCcBody) {
  const res = await request.post<ApiResult<null>>(
    `${BASE}/instance/${instanceId}/cc`,
    data
  );
  return unwrap(res);
}

// ---------------- 流程模板 ----------------
export async function pageFlows(params: FlowParam) {
  const res = await request.get<ApiResult<PageResult<FlowOut>>>(
    `${BASE}/flow`,
    { params }
  );
  return unwrap(res);
}

export async function getFlow(flowId: number) {
  const res = await request.get<ApiResult<FlowOut>>(`${BASE}/flow/${flowId}`);
  return unwrap(res);
}

export async function createFlow(data: FlowCreateBody) {
  const res = await request.post<ApiResult<FlowOut>>(`${BASE}/flow`, data);
  return unwrap(res);
}

export async function updateFlow(flowId: number, data: FlowUpdateBody) {
  const res = await request.put<ApiResult<FlowOut>>(
    `${BASE}/flow/${flowId}`,
    data
  );
  return unwrap(res);
}

export async function publishFlow(flowId: number) {
  const res = await request.post<ApiResult<FlowOut>>(
    `${BASE}/flow/${flowId}/publish`
  );
  return unwrap(res);
}

export async function disableFlow(flowId: number) {
  const res = await request.post<ApiResult<FlowOut>>(
    `${BASE}/flow/${flowId}/disable`
  );
  return unwrap(res);
}

export async function enableFlow(flowId: number) {
  const res = await request.post<ApiResult<FlowOut>>(
    `${BASE}/flow/${flowId}/enable`
  );
  return unwrap(res);
}

export async function listFlowVersionHistory(flowId: number) {
  const res = await request.get<ApiResult<FlowVersionLog[]>>(
    `${BASE}/flow/${flowId}/version-history`
  );
  return unwrap(res);
}

export async function deleteFlow(flowId: number) {
  const res = await request.delete<ApiResult<null>>(`${BASE}/flow/${flowId}`);
  return unwrap(res);
}
