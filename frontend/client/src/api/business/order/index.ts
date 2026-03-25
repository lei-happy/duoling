import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { Order, OrderParam } from './model';

export async function pageOrders(params: OrderParam) {
  const res = await request.get<ApiResult<PageResult<Order>>>(
    '/business/order',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function pageDispatchOrders(params: OrderParam) {
  const res = await request.get<ApiResult<PageResult<Order>>>(
    '/business/order/dispatch',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function pageTrackingOrders(params: OrderParam) {
  const res = await request.get<ApiResult<PageResult<Order>>>(
    '/business/order/tracking',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function pageReceiptOrders(params: OrderParam) {
  const res = await request.get<ApiResult<PageResult<Order>>>(
    '/business/order/receipt',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addOrder(data: Order) {
  const res = await request.post<ApiResult<unknown>>(
    '/business/order',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateOrder(data: Order) {
  const res = await request.put<ApiResult<unknown>>(
    `/business/order/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateOrderStatus(
  id: number,
  data: {
    status: number;
    actualDepartTime?: string;
    actualArriveTime?: string;
  }
) {
  const res = await request.put<ApiResult<unknown>>(
    `/business/order/${id}/status`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeOrder(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/business/order/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
