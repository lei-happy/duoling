import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { CapacityLog, CapacityLogParam } from './model';

const BASE = '/capacity/self_capacity/log';

export async function pageCapacityLogs(params: CapacityLogParam) {
  const res = await request.get<ApiResult<PageResult<CapacityLog>>>(BASE, {
    params
  });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
