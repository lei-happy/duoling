import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { Customer, CustomerParam } from './model';

export async function pageCustomers(params: CustomerParam) {
  const res = await request.get<ApiResult<PageResult<Customer>>>(
    '/resource/customer',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addCustomer(data: Customer) {
  const res = await request.post<ApiResult<unknown>>(
    '/resource/customer',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateCustomer(data: Customer) {
  const res = await request.put<ApiResult<unknown>>(
    `/resource/customer/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeCustomer(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/resource/customer/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
