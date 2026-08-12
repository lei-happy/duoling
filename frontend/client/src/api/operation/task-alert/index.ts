import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  TaskAlert,
  TaskAlertBatchResult,
  TaskAlertParam,
  TaskAlertRule,
  TaskAlertRuleCatalogItem,
  TaskAlertRuleConflict,
  TaskAlertRuleParam
} from './model';

// ============================================================
// 预警实例
// ============================================================

export async function pageTaskAlerts(params: TaskAlertParam) {
  const res = await request.get<ApiResult<PageResult<TaskAlert>>>(
    '/business/task-alert',
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/** 某任务的预警：活跃的排在前面，已处置的保留供复盘 */
export async function listTaskAlerts(taskId: number, activeOnly = false) {
  const res = await request.get<ApiResult<TaskAlert[]>>(
    `/business/task/${taskId}/alerts`,
    { params: { activeOnly } }
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function claimTaskAlert(id: number) {
  const res = await request.post<ApiResult<TaskAlert>>(
    `/business/task-alert/${id}/claim`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function resolveTaskAlert(id: number, remark?: string) {
  const res = await request.post<ApiResult<TaskAlert>>(
    `/business/task-alert/${id}/resolve`,
    { remark }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function dismissTaskAlert(id: number, reason: string) {
  const res = await request.post<ApiResult<TaskAlert>>(
    `/business/task-alert/${id}/dismiss`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/** 批量忽略：按预警 ID 或按任务 ID（任务下全部活跃预警）二选一 */
export async function batchDismissTaskAlerts(data: {
  ids?: number[];
  taskIds?: number[];
  reason: string;
}) {
  const res = await request.post<ApiResult<TaskAlertBatchResult>>(
    '/business/task-alert/batch-dismiss',
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

// ============================================================
// 预警规则
// ============================================================

export async function getTaskAlertCatalog() {
  const res = await request.get<ApiResult<TaskAlertRuleCatalogItem[]>>(
    '/business/task-alert-rule/catalog'
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

/** 租户默认阈值（未限定任何维度的那批规则） */
export async function listTaskAlertRuleDefaults() {
  const res = await request.get<ApiResult<TaskAlertRule[]>>(
    '/business/task-alert-rule/defaults'
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function pageTaskAlertRules(params: TaskAlertRuleParam) {
  const res = await request.get<ApiResult<PageResult<TaskAlertRule>>>(
    '/business/task-alert-rule',
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/** 保存前预检：是否已有适用范围与优先级完全相同的规则 */
export async function checkTaskAlertRuleConflict(
  data: TaskAlertRule,
  excludeId?: number
) {
  const res = await request.post<ApiResult<TaskAlertRuleConflict>>(
    '/business/task-alert-rule/check-conflict',
    data,
    { params: { excludeId } }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function addTaskAlertRule(data: TaskAlertRule) {
  const res = await request.post<ApiResult<TaskAlertRule>>(
    '/business/task-alert-rule',
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateTaskAlertRule(id: number, data: TaskAlertRule) {
  const res = await request.put<ApiResult<TaskAlertRule>>(
    `/business/task-alert-rule/${id}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeTaskAlertRule(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/business/task-alert-rule/${id}`
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}
