import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { Driver, DriverParam } from './model';

export async function pageDrivers(params: DriverParam) {
  const res = await request.get<ApiResult<PageResult<Driver>>>(
    '/resource/driver',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addDriver(data: Driver) {
  const res = await request.post<ApiResult<unknown>>(
    '/resource/driver',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateDriver(data: Driver) {
  const res = await request.put<ApiResult<unknown>>(
    `/resource/driver/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeDriver(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/resource/driver/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
