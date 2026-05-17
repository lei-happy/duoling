import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  BatchActionResult,
  CandidateCargo,
  Task,
  TaskBatchStatusPayload,
  TaskCarrierInfo,
  TaskCreatePayload,
  TaskFinanceSummaryItem,
  TaskParam,
  TaskSegment,
  TaskUpdatePayload,
  TaskWaybillItem,
  TaskWorkbenchStats
} from './model';

export async function pageTasks(params: TaskParam) {
  const res = await request.get<ApiResult<PageResult<Task>>>(
    '/business/task',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getTask(id: number) {
  const res = await request.get<ApiResult<Task>>(`/business/task/${id}`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function checkTaskNoAvailable(
  taskNo: string,
  excludeId?: number
) {
  const q = taskNo.trim();
  if (!q) return true;
  const res = await request.get<ApiResult<{ available: boolean }>>(
    '/business/task/check-task-no',
    { params: { taskNo: q, excludeId } }
  );
  if (res.data.code === 0) return res.data.data?.available ?? true;
  return true;
}

export async function addTask(data: TaskCreatePayload) {
  const res = await request.post<ApiResult<Task>>('/business/task', data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateTask(id: number, data: TaskUpdatePayload) {
  const res = await request.put<ApiResult<Task>>(
    `/business/task/${id}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeTask(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`/business/task/${id}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function updateTaskStatus(
  id: number,
  data: {
    status: number;
    actualLoadTime?: string;
    actualArriveTime?: string;
    remark?: string;
  }
) {
  const res = await request.put<ApiResult<Task>>(
    `/business/task/${id}/status`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function assignCarrier(
  id: number,
  data: {
    carrier: TaskCarrierInfo;
    carrierCostType?: number | null;
    carrierCostAmount?: number | null;
    costRemark?: string;
  }
) {
  const res = await request.post<ApiResult<Task>>(
    `/business/task/${id}/assign-carrier`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelTask(id: number, reason?: string) {
  const res = await request.post<ApiResult<Task>>(
    `/business/task/${id}/cancel`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

// ============================
// 货物挂接
// ============================

export async function listCandidateWaybills(params: {
  keyword?: string;
  customerId?: number;
  originKeyword?: string;
  destinationKeyword?: string;
  limit?: number;
}) {
  const res = await request.get<ApiResult<CandidateCargo[]>>(
    '/business/task/candidate-waybills',
    { params }
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function listTaskWaybillItems(taskId: number) {
  const res = await request.get<ApiResult<TaskWaybillItem[]>>(
    `/business/task/${taskId}/waybill-items`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function addTaskWaybillItems(
  taskId: number,
  items: Array<{
    waybillId: number;
    waybillCargoId: number;
    quantity: number;
    segmentId?: number | null;
    remark?: string;
  }>
) {
  const res = await request.post<ApiResult<TaskWaybillItem[]>>(
    `/business/task/${taskId}/waybill-items`,
    items
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function updateTaskWaybillItem(
  itemId: number,
  data: {
    status: number;
    loadedAt?: string;
    unloadedAt?: string;
    signedAt?: string;
    segmentId?: number | null;
    remark?: string;
  }
) {
  const res = await request.put<ApiResult<TaskWaybillItem>>(
    `/business/task/waybill-items/${itemId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeTaskWaybillItem(itemId: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/business/task/waybill-items/${itemId}`
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

// ============================
// 分段
// ============================

export async function listTaskSegments(taskId: number) {
  const res = await request.get<ApiResult<TaskSegment[]>>(
    `/business/task/${taskId}/segments`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function updateSegmentStatus(
  segId: number,
  data: {
    status: number;
    actualLoadTime?: string;
    actualArriveTime?: string;
    remark?: string;
  }
) {
  const res = await request.put<ApiResult<TaskSegment>>(
    `/business/task/segments/${segId}/status`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

// ============================
// 任务单维度费用单摘要（详情页 tab）
// ============================

export async function listTaskFinanceSummary(taskId: number) {
  const res = await request.get<ApiResult<TaskFinanceSummaryItem[]>>(
    `/business/task/${taskId}/finance-docs-summary`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

// ============================
// 调度工作台聚合 & 批量操作
// ============================

export async function getTaskWorkbenchStats() {
  const res = await request.get<ApiResult<TaskWorkbenchStats>>(
    '/business/task/workbench-stats'
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function batchUpdateTaskStatus(data: TaskBatchStatusPayload) {
  const res = await request.post<ApiResult<BatchActionResult>>(
    '/business/task/batch-status',
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}
