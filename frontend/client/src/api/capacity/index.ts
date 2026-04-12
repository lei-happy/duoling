import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  Capacity,
  CapacityParam,
  CapacityBindData,
  CapacityUnbindData,
  CapacityLog,
  CapacityLogParam,
  DriverOption,
  VehicleOption
} from './model';

export async function pageCapacities(params: CapacityParam) {
  const res = await request.get<ApiResult<PageResult<Capacity>>>(
    '/capacity',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function bindCapacity(data: CapacityBindData) {
  const res = await request.post<ApiResult<Capacity>>(
    '/capacity/bind',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function unbindCapacity(id: number, data?: CapacityUnbindData) {
  const res = await request.put<ApiResult<unknown>>(
    `/capacity/${id}/unbind`,
    data ?? {}
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function pageCapacityLogs(params: CapacityLogParam) {
  const res = await request.get<ApiResult<PageResult<CapacityLog>>>(
    '/capacity/log',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listAvailableDrivers(keyword?: string) {
  const res = await request.get<ApiResult<PageResult<DriverOption>>>(
    '/resource/driver',
    { params: { status: 1, limit: 50, keyword } }
  );
  if (res.data.code === 0) {
    return res.data.data?.list ?? [];
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listAvailableVehicles(keyword?: string) {
  const res = await request.get<ApiResult<PageResult<VehicleOption>>>(
    '/resource/vehicle',
    { params: { status: 1, limit: 50, keyword } }
  );
  if (res.data.code === 0) {
    return res.data.data?.list ?? [];
  }
  return Promise.reject(new Error(res.data.message));
}
