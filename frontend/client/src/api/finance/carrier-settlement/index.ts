import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  CarrierAccount,
  CarrierSettleCreatePayload,
  CarrierSettleDetail,
  CarrierSettleListItem,
  CarrierSettleParam,
  CarrierSettlePayPayload,
  CarrierSettleReconCandidate,
  CarrierSettleReconItem,
  CarrierSettleUpdatePayload,
  FinanceDocEvent
} from './model';

const BASE = '/finance/carrier-settlement';

export async function listSettleReconCandidates(params: {
  carrierId: number;
  settleId?: number;
  keyword?: string;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: CarrierSettleReconCandidate[]; count: number }>
  >(`${BASE}/recon-candidates`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listCarrierAccounts(carrierId: number) {
  const res = await request.get<ApiResult<CarrierAccount[]>>(
    `${BASE}/accounts`,
    { params: { carrierId } }
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

/** 出纳台待付池：已审批且未进入打款批次 */
export async function pagePayableSettles(params: CarrierSettleParam) {
  const res = await request.get<ApiResult<PageResult<CarrierSettleListItem>>>(
    `${BASE}/payable`,
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function pageCarrierSettles(params: CarrierSettleParam) {
  const res = await request.get<ApiResult<PageResult<CarrierSettleListItem>>>(
    BASE,
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getCarrierSettle(settleId: number) {
  const res = await request.get<ApiResult<CarrierSettleDetail>>(
    `${BASE}/${settleId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function addCarrierSettle(data: CarrierSettleCreatePayload) {
  const res = await request.post<ApiResult<CarrierSettleDetail>>(BASE, data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateCarrierSettle(
  settleId: number,
  data: CarrierSettleUpdatePayload
) {
  const res = await request.put<ApiResult<CarrierSettleDetail>>(
    `${BASE}/${settleId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeCarrierSettle(settleId: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${settleId}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function linkSettleRecons(
  settleId: number,
  recons: CarrierSettleReconItem[]
) {
  const res = await request.post<ApiResult<CarrierSettleDetail>>(
    `${BASE}/${settleId}/recons`,
    { recons }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function unlinkSettleRecon(settleId: number, linkId: number) {
  const res = await request.delete<ApiResult<CarrierSettleDetail>>(
    `${BASE}/${settleId}/recons/${linkId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateSettleAccount(
  settleId: number,
  settlementAccountId: number
) {
  const res = await request.put<ApiResult<CarrierSettleDetail>>(
    `${BASE}/${settleId}/account`,
    { settlementAccountId }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function submitCarrierSettle(settleId: number) {
  const res = await request.post<ApiResult<CarrierSettleDetail>>(
    `${BASE}/${settleId}/submit`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function approveCarrierSettle(settleId: number) {
  const res = await request.post<ApiResult<CarrierSettleDetail>>(
    `${BASE}/${settleId}/approve`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function rejectCarrierSettle(settleId: number, reason: string) {
  const res = await request.post<ApiResult<CarrierSettleDetail>>(
    `${BASE}/${settleId}/reject`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function withdrawCarrierSettle(settleId: number, reason: string) {
  const res = await request.post<ApiResult<CarrierSettleDetail>>(
    `${BASE}/${settleId}/withdraw`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function payCarrierSettle(
  settleId: number,
  data: CarrierSettlePayPayload
) {
  const res = await request.post<ApiResult<CarrierSettleDetail>>(
    `${BASE}/${settleId}/pay`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelSettlePay(settleId: number, reason: string) {
  const res = await request.post<ApiResult<CarrierSettleDetail>>(
    `${BASE}/${settleId}/cancel-pay`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelCarrierSettle(settleId: number, reason: string) {
  const res = await request.post<ApiResult<CarrierSettleDetail>>(
    `${BASE}/${settleId}/cancel`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listSettleTaskIds(settleId: number) {
  const res = await request.get<
    ApiResult<{ taskIds: number[]; count: number }>
  >(`${BASE}/${settleId}/tasks`);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listCarrierSettleEvents(settleId: number) {
  const res = await request.get<ApiResult<FinanceDocEvent[]>>(
    `${BASE}/${settleId}/events`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}
