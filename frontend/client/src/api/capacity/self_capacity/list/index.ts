import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  Capacity,
  CapacityParam,
  CapacityBindData,
  CapacityUnbindData,
  DriverOption,
  VehicleOption
} from './model';

const BASE = '/capacity/self_capacity/list';

export async function pageCapacities(params: CapacityParam) {
  const res = await request.get<ApiResult<PageResult<Capacity>>>(
    BASE,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function bindCapacity(data: CapacityBindData) {
  const res = await request.post<ApiResult<Capacity>>(
    `${BASE}/bind`,
    data
  );
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

export async function listAvailableDrivers(keyword?: string) {
  const res = await request.get<ApiResult<PageResult<DriverOption>>>(
    '/capacity/self_capacity/driver',
    { params: { status: 1, limit: 50, keyword } }
  );
  if (res.data.code === 0) {
    return res.data.data?.list ?? [];
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listAvailableVehicles(keyword?: string) {
  const res = await request.get<ApiResult<PageResult<VehicleOption>>>(
    '/capacity/self_capacity/vehicle',
    { params: { status: 1, limit: 50, keyword } }
  );
  if (res.data.code === 0) {
    return res.data.data?.list ?? [];
  }
  return Promise.reject(new Error(res.data.message));
}
