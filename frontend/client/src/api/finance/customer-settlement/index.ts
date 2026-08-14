import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { FinanceDocEvent } from '@/api/finance/customer-recon/model';
import type {
  SettleCreatePayload,
  SettleDetail,
  SettleListItem,
  SettleParam,
  SettleReceivePayload,
  SettleReconCandidate,
  SettleReconItemPayload,
  SettleUpdatePayload
} from './model';

const BASE = '/finance/customer-settlement';

export async function listSettleReconCandidates(params: {
  customerId: number;
  settleId?: number;
  keyword?: string;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: SettleReconCandidate[]; count: number }>
  >(`${BASE}/recon-candidates`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function pageSettlements(params: SettleParam) {
  const res = await request.get<ApiResult<PageResult<SettleListItem>>>(BASE, {
    params
  });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getSettlement(settleId: number) {
  const res = await request.get<ApiResult<SettleDetail>>(`${BASE}/${settleId}`);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function addSettlement(data: SettleCreatePayload) {
  const res = await request.post<ApiResult<SettleDetail>>(BASE, data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateSettlement(
  settleId: number,
  data: SettleUpdatePayload
) {
  const res = await request.put<ApiResult<SettleDetail>>(
    `${BASE}/${settleId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeSettlement(settleId: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${settleId}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function linkSettleRecons(
  settleId: number,
  recons: SettleReconItemPayload[]
) {
  const res = await request.post<ApiResult<SettleDetail>>(
    `${BASE}/${settleId}/recons`,
    { recons }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function unlinkSettleRecon(settleId: number, linkId: number) {
  const res = await request.delete<ApiResult<SettleDetail>>(
    `${BASE}/${settleId}/recons/${linkId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function submitSettlement(settleId: number) {
  const res = await request.post<ApiResult<SettleDetail>>(
    `${BASE}/${settleId}/submit`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function approveSettlement(settleId: number) {
  const res = await request.post<ApiResult<SettleDetail>>(
    `${BASE}/${settleId}/approve`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function rejectSettlement(settleId: number, reason: string) {
  const res = await request.post<ApiResult<SettleDetail>>(
    `${BASE}/${settleId}/reject`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function withdrawSettlement(settleId: number, reason: string) {
  const res = await request.post<ApiResult<SettleDetail>>(
    `${BASE}/${settleId}/withdraw`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function receiveSettlement(
  settleId: number,
  data: SettleReceivePayload
) {
  const res = await request.post<ApiResult<SettleDetail>>(
    `${BASE}/${settleId}/receive`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelSettleReceive(settleId: number, reason: string) {
  const res = await request.post<ApiResult<SettleDetail>>(
    `${BASE}/${settleId}/cancel-receive`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelSettlement(settleId: number, reason: string) {
  const res = await request.post<ApiResult<SettleDetail>>(
    `${BASE}/${settleId}/cancel`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listSettleEvents(settleId: number) {
  const res = await request.get<ApiResult<FinanceDocEvent[]>>(
    `${BASE}/${settleId}/events`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}
