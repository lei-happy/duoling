import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { Vehicle, VehicleParam, TrailerOption } from './model';

export async function pageVehicles(params: VehicleParam) {
  const res = await request.get<ApiResult<PageResult<Vehicle>>>(
    '/resource/vehicle',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getVehicle(id: number) {
  const res = await request.get<ApiResult<Vehicle>>(
    `/resource/vehicle/${id}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addVehicle(data: Vehicle) {
  const res = await request.post<ApiResult<unknown>>(
    '/resource/vehicle',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateVehicle(data: Vehicle) {
  const res = await request.put<ApiResult<unknown>>(
    `/resource/vehicle/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeVehicle(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/resource/vehicle/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listAvailableTrailers(excludeVehicleId?: number) {
  const res = await request.get<ApiResult<TrailerOption[]>>(
    '/resource/trailer/available',
    { params: { excludeVehicleId } }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
