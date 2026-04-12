import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { PlatformCapacity, PlatformCapacityParam } from './model';

export async function pagePlatformCapacities(params: PlatformCapacityParam) {
  const res = await request.get<ApiResult<PageResult<PlatformCapacity>>>(
    '/capacity',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getPlatformCapacity(id: number) {
  const res = await request.get<ApiResult<PlatformCapacity>>(
    `/capacity/${id}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
