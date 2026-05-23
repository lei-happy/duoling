import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  BatchActionResult,
  CandidateCargo,
  RouteDistanceLookup,
  Task,
  TaskBatchStatusPayload,
  TaskBatchCarrierAssignmentPayload,
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
  const res = await request.get<ApiResult<PageResult<Task>>>('/business/task', {
    params
  });
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

export async function checkTaskNoAvailable(taskNo: string, excludeId?: number) {
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
  const res = await request.put<ApiResult<Task>>(`/business/task/${id}`, data);
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
    signedAt?: string;
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
    isProxy?: boolean;
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

/** 待分配 → 待派车：确认承运方式（不要求等同派车的完整运力） */
export async function completeCarrierAssignment(
  id: number,
  data: TaskCarrierInfo
) {
  const res = await request.post<ApiResult<Task>>(
    `/business/task/${id}/complete-carrier-assignment`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/** 待分配 → 待派车：批量确认承运方式（仅自有车 / 承运商） */
export async function batchCompleteCarrierAssignment(
  data: TaskBatchCarrierAssignmentPayload
) {
  const res = await request.post<ApiResult<BatchActionResult>>(
    '/business/task/batch-complete-carrier-assignment',
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/**
 * 规划任务单运输路线（补齐 / 重做分段，独立于派车）
 *
 * 适用状态：待派车 / 已派车 / 已装车
 */
export async function planTaskRoute(
  id: number,
  data: { segments: TaskSegment[] }
) {
  const res = await request.post<ApiResult<Task>>(
    `/business/task/${id}/plan-route`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/**
 * 段表里程联想：按起终行政区匹配 biz_route 中已维护的线路
 *
 * 未匹配返回 null。
 */
export async function lookupRouteDistance(params: {
  originRegionId: number;
  destinationRegionId: number;
}) {
  const res = await request.get<ApiResult<RouteDistanceLookup | null>>(
    '/business/task/route-distance',
    { params }
  );
  if (res.data.code === 0) return res.data.data ?? null;
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

/** 撤销至上一态（专项接口；见 02.运单与任务单状态机联动设计.md §4.5） */
export async function revertTaskStatus(
  id: number,
  data: { targetStatus: number; reason: string }
) {
  const res = await request.post<ApiResult<Task>>(
    `/business/task/${id}/revert-status`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/** 强制取消（线下取消，2/3/4 → 9） */
export async function forceCancelTask(
  id: number,
  data: { reason: string; cancelUnpaidFinanceDocs?: boolean }
) {
  const res = await request.post<ApiResult<Task>>(
    `/business/task/${id}/force-cancel`,
    {
      reason: data.reason,
      cancelUnpaidFinanceDocs: data.cancelUnpaidFinanceDocs ?? true
    }
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
  const res = await request.get<ApiResult<CandidateCargoListResult>>(
    '/business/task/candidate-waybills',
    { params }
  );
  if (res.data.code === 0) {
    return (
      res.data.data || {
        items: [],
        lineCount: 0,
        quantityTotal: 0,
        truncated: false
      }
    );
  }
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
    dispatchOrderId?: number | null;
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
    dispatchOrderId?: number | null;
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
