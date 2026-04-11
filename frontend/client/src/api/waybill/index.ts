import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { Waybill, WaybillParam } from './model';

export async function pageWaybills(params: WaybillParam) {
  const res = await request.get<ApiResult<PageResult<Waybill>>>(
    '/business/waybill',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getWaybill(id: number) {
  const res = await request.get<ApiResult<Waybill>>(
    `/business/waybill/${id}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addWaybill(data: Waybill) {
  const res = await request.post<ApiResult<unknown>>(
    '/business/waybill',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateWaybill(data: Waybill) {
  const res = await request.put<ApiResult<unknown>>(
    `/business/waybill/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateWaybillStatus(id: number, status: number) {
  const res = await request.put<ApiResult<unknown>>(
    `/business/waybill/${id}/status`,
    { status }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeWaybill(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/business/waybill/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
