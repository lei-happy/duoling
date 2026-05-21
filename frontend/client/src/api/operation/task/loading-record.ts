import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type {
  TaskLoadingRecord,
  TaskLoadingRecordPayload
} from './model';

/** 列出某任务的全部装卸事件 */
export async function listLoadingRecords(taskId: number) {
  const res = await request.get<ApiResult<TaskLoadingRecord[]>>(
    `/business/task/${taskId}/loading-records`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

/** 创建装/卸车记录（同事务推进 item / task / waybill 状态） */
export async function createLoadingRecord(
  taskId: number,
  payload: TaskLoadingRecordPayload
) {
  const res = await request.post<ApiResult<TaskLoadingRecord>>(
    `/business/task/${taskId}/loading-records`,
    payload
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/** 撤销一条装/卸车记录（回退 item 状态与任务态） */
export async function revokeLoadingRecord(recordId: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/business/task/loading-records/${recordId}`
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}
