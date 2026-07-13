import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type {
  SmartStowageGeneratePayload,
  SmartStowageGenerateResult,
  SmartStowagePlan,
  SmartStowageTask
} from './model';

/** 一键生成配载方案（同步产出） */
export async function generateStowagePlans(data: SmartStowageGeneratePayload) {
  const res = await request.post<ApiResult<SmartStowageGenerateResult>>(
    '/business/smart-stowage/generate',
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/** 查询生成任务状态 */
export async function getStowageTask(taskId: number) {
  const res = await request.get<ApiResult<SmartStowageTask | null>>(
    `/business/smart-stowage/tasks/${taskId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/** 按生成任务拉方案列表 */
export async function listStowagePlans(planTaskId: number) {
  const res = await request.get<ApiResult<SmartStowagePlan[]>>(
    '/business/smart-stowage/plans',
    { params: { planTaskId } }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/** 采纳方案 → 落为任务单，返回 taskId */
export async function adoptStowagePlan(planId: number, remark?: string) {
  const res = await request.post<ApiResult<{ taskId: number }>>(
    `/business/smart-stowage/plans/${planId}/adopt`,
    { remark }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/** 忽略方案 */
export async function ignoreStowagePlan(planId: number) {
  const res = await request.post<ApiResult<unknown>>(
    `/business/smart-stowage/plans/${planId}/ignore`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}
