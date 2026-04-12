import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { PlatformDriver, PlatformDriverParam } from './model';

export async function pagePlatformDrivers(params: PlatformDriverParam) {
  const res = await request.get<ApiResult<PageResult<PlatformDriver>>>(
    '/driver',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getPlatformDriver(id: number) {
  const res = await request.get<ApiResult<PlatformDriver>>(`/driver/${id}`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
