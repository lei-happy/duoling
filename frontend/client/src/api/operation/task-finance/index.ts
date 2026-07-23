import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  TaskFinanceBatchActionPayload,
  TaskFinanceBatchActionResult,
  TaskFinanceDoc,
  TaskFinanceDocCreatePayload,
  TaskFinanceDocListItem,
  TaskFinanceDocParam,
  TaskFinanceDocPayPayload,
  TaskFinanceDocUpdatePayload,
  TaskFinanceWorkbenchStats
} from './model';

export async function pageFinanceDocs(params: TaskFinanceDocParam) {
  const res = await request.get<ApiResult<PageResult<TaskFinanceDocListItem>>>(
    '/business/task-finance',
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listFinanceDocsByTask(taskId: number) {
  const res = await request.get<ApiResult<TaskFinanceDoc[]>>(
    `/business/task-finance/by-task/${taskId}`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

/** 某任务当前节点可发起的费用单类型（入口显隐 / 下拉过滤） */
export interface CreatableDocTypes {
  taskStatus: number;
  enforce: boolean;
  docTypes: number[];
}

export async function getCreatableDocTypes(taskId: number) {
  const res = await request.get<ApiResult<CreatableDocTypes>>(
    `/business/task-finance/by-task/${taskId}/creatable-doc-types`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function addFinanceDoc(
  taskId: number,
  data: TaskFinanceDocCreatePayload
) {
  const res = await request.post<ApiResult<TaskFinanceDoc>>(
    `/business/task-finance/by-task/${taskId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getFinanceDoc(docId: number) {
  const res = await request.get<ApiResult<TaskFinanceDoc>>(
    `/business/task-finance/${docId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateFinanceDoc(
  docId: number,
  data: TaskFinanceDocUpdatePayload
) {
  const res = await request.put<ApiResult<TaskFinanceDoc>>(
    `/business/task-finance/${docId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeFinanceDoc(docId: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/business/task-finance/${docId}`
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function submitFinanceDoc(docId: number) {
  const res = await request.post<ApiResult<TaskFinanceDoc>>(
    `/business/task-finance/${docId}/submit`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function approveFinanceDoc(docId: number) {
  const res = await request.post<ApiResult<TaskFinanceDoc>>(
    `/business/task-finance/${docId}/approve`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function payFinanceDoc(
  docId: number,
  data: TaskFinanceDocPayPayload
) {
  const res = await request.post<ApiResult<TaskFinanceDoc>>(
    `/business/task-finance/${docId}/pay`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelFinanceDoc(docId: number, reason?: string) {
  const res = await request.post<ApiResult<TaskFinanceDoc>>(
    `/business/task-finance/${docId}/cancel`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

// ============================
// 费用工作台聚合 & 批量动作
// ============================

export async function getFinanceWorkbenchStats() {
  const res = await request.get<ApiResult<TaskFinanceWorkbenchStats>>(
    '/business/task-finance/workbench-stats'
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function batchFinanceAction(data: TaskFinanceBatchActionPayload) {
  const res = await request.post<ApiResult<TaskFinanceBatchActionResult>>(
    '/business/task-finance/batch-action',
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}
