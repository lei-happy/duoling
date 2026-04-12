import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { Driver, DriverParam, DriverAccount, DriverRoute } from './model';

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

export async function getDriver(id: number) {
  const res = await request.get<ApiResult<Driver>>(
    `/resource/driver/${id}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addDriver(data: Partial<Driver>) {
  const res = await request.post<ApiResult<unknown>>(
    '/resource/driver',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateDriver(data: Partial<Driver>) {
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

export async function updateDriverStatus(id: number, status: number) {
  const res = await request.put<ApiResult<unknown>>(
    `/resource/driver/${id}/status`,
    { status }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateOperationStatus(
  id: number,
  operationStatus: number
) {
  const res = await request.put<ApiResult<unknown>>(
    `/resource/driver/${id}/operation-status`,
    { operationStatus }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listDriverAccounts(driverId: number) {
  const res = await request.get<ApiResult<DriverAccount[]>>(
    `/resource/driver/${driverId}/accounts`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addDriverAccount(
  driverId: number,
  data: Partial<DriverAccount>
) {
  const res = await request.post<ApiResult<unknown>>(
    `/resource/driver/${driverId}/accounts`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateDriverAccount(data: Partial<DriverAccount>) {
  const res = await request.put<ApiResult<unknown>>(
    `/resource/driver/accounts/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeDriverAccount(accountId: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/resource/driver/accounts/${accountId}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function toggleAccountStatus(accountId: number, status: number) {
  const res = await request.put<ApiResult<unknown>>(
    `/resource/driver/accounts/${accountId}/status`,
    { status }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listDriverRoutes(driverId: number) {
  const res = await request.get<ApiResult<DriverRoute[]>>(
    `/resource/driver/${driverId}/routes`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function saveDriverRoutes(
  driverId: number,
  routes: Partial<DriverRoute>[]
) {
  const res = await request.put<ApiResult<unknown>>(
    `/resource/driver/${driverId}/routes`,
    routes
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
