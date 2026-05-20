import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { Vehicle, VehicleParam, TrailerOption } from './model';

const BASE = '/capacity/self_capacity/vehicle';

export async function pageVehicles(params: VehicleParam) {
  const res = await request.get<ApiResult<PageResult<Vehicle>>>(BASE, {
    params
  });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getVehicle(id: number) {
  const res = await request.get<ApiResult<Vehicle>>(`${BASE}/${id}`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addVehicle(data: Vehicle) {
  const res = await request.post<ApiResult<unknown>>(BASE, data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateVehicle(data: Vehicle) {
  const res = await request.put<ApiResult<unknown>>(`${BASE}/${data.id}`, data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeVehicle(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${id}`);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listAvailableTrailers(excludeVehicleId?: number) {
  const res = await request.get<ApiResult<TrailerOption[]>>(
    '/capacity/self_capacity/trailer/available',
    { params: { excludeVehicleId } }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
