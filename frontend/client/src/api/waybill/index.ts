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

/** 运单号是否可用（未被占用）；编辑传 excludeId 排除当前单 */
export async function checkWaybillNoAvailable(waybillNo: string, excludeId?: number) {
  const q = waybillNo.trim();
  if (!q) return true;
  const res = await request.get<ApiResult<{ available: boolean }>>(
    '/business/waybill/check-waybill-no',
    { params: { waybillNo: q, excludeId } }
  );
  if (res.data.code === 0) {
    return res.data.data?.available ?? true;
  }
  return true;
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
