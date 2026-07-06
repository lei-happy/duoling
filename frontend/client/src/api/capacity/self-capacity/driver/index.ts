import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  Driver,
  DriverParam,
  DriverAccount,
  DriverRoute,
  DriverFundAccount,
  DriverFundTransaction,
  DriverFundTransactionParam
} from './model';

const BASE = '/capacity/self_capacity/driver';

export async function pageDrivers(params: DriverParam) {
  const res = await request.get<ApiResult<PageResult<Driver>>>(BASE, {
    params
  });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getDriver(id: number) {
  const res = await request.get<ApiResult<Driver>>(`${BASE}/${id}`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addDriver(data: Partial<Driver>) {
  const res = await request.post<ApiResult<unknown>>(BASE, data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateDriver(data: Partial<Driver>) {
  const res = await request.put<ApiResult<unknown>>(`${BASE}/${data.id}`, data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeDriver(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${id}`);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateDriverStatus(id: number, status: number) {
  const res = await request.put<ApiResult<unknown>>(`${BASE}/${id}/status`, {
    status
  });
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
    `${BASE}/${id}/operation-status`,
    { operationStatus }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listDriverAccounts(driverId: number) {
  const res = await request.get<ApiResult<DriverAccount[]>>(
    `${BASE}/${driverId}/accounts`
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
    `${BASE}/${driverId}/accounts`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateDriverAccount(data: Partial<DriverAccount>) {
  const res = await request.put<ApiResult<unknown>>(
    `${BASE}/accounts/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeDriverAccount(accountId: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `${BASE}/accounts/${accountId}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function toggleAccountStatus(accountId: number, status: number) {
  const res = await request.put<ApiResult<unknown>>(
    `${BASE}/accounts/${accountId}/status`,
    { status }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listDriverRoutes(driverId: number) {
  const res = await request.get<ApiResult<DriverRoute[]>>(
    `${BASE}/${driverId}/routes`
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
    `${BASE}/${driverId}/routes`,
    routes
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 资金账户（往来账） */
export async function getDriverFundAccount(driverId: number) {
  const res = await request.get<ApiResult<DriverFundAccount>>(
    `${BASE}/${driverId}/fund-account`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listDriverFundTransactions(
  driverId: number,
  params: {
    page?: number;
    limit?: number;
    bizType?: number;
    source?: number;
    start?: string;
    end?: string;
  }
) {
  const res = await request.get<
    ApiResult<{ list: DriverFundTransaction[]; total: number }>
  >(`${BASE}/${driverId}/fund-account/transactions`, { params });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function postDriverFundTransaction(
  driverId: number,
  data: DriverFundTransactionParam
) {
  const res = await request.post<ApiResult<DriverFundTransaction>>(
    `${BASE}/${driverId}/fund-account/transactions`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function toggleFundAccountStatus(
  accountId: number,
  status: number
) {
  const res = await request.patch<ApiResult<DriverFundAccount>>(
    `${BASE}/fund-account/${accountId}/status`,
    { status }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
