import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  Capacity,
  CapacityParam,
  CapacityBindData,
  CapacityUnbindData,
  CapacityStatusUpdateData,
  CapacityListStats
} from './model';

const BASE = '/capacity/self_capacity/list';

export async function getCapacityListStats(
  params?: Pick<CapacityParam, 'keyword' | 'enterpriseId'>
) {
  const res = await request.get<ApiResult<CapacityListStats>>(`${BASE}/stats`, {
    params
  });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function pageCapacities(params: CapacityParam) {
  const res = await request.get<ApiResult<PageResult<Capacity>>>(BASE, {
    params
  });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function bindCapacity(data: CapacityBindData) {
  const res = await request.post<ApiResult<Capacity>>(`${BASE}/bind`, data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function unbindCapacity(id: number, data?: CapacityUnbindData) {
  const res = await request.put<ApiResult<unknown>>(
    `${BASE}/${id}/unbind`,
    data ?? {}
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateCapacityOperationStatus(
  id: number,
  data: CapacityStatusUpdateData
) {
  const res = await request.put<ApiResult<Capacity>>(
    `${BASE}/${id}/operation-status`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
