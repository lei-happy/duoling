import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  Carrier,
  CarrierListItem,
  CarrierParam,
  CarrierSelectItem,
  CarrierSettlement,
  CarrierInvitation,
  CarrierInviteRequest,
  CarrierInviteResponse,
  CarrierInvitePhoneCheckResult
} from './model';

const BASE = '/partner/carrier';

export async function pageCarriers(params: CarrierParam) {
  const res = await request.get<ApiResult<PageResult<CarrierListItem>>>(BASE, {
    params
  });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getCarrier(id: number) {
  const res = await request.get<ApiResult<Carrier>>(`${BASE}/${id}`);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function selectCarriers(keyword?: string) {
  const res = await request.get<ApiResult<CarrierSelectItem[]>>(
    `${BASE}/select`,
    { params: keyword ? { keyword } : {} }
  );
  if (res.data.code === 0) return res.data.data ?? [];
  return Promise.reject(new Error(res.data.message));
}

export async function addCarrier(data: Carrier) {
  const res = await request.post<ApiResult<Carrier>>(BASE, data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateCarrier(data: Carrier) {
  const res = await request.put<ApiResult<Carrier>>(
    `${BASE}/${data.id}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeCarrier(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${id}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

// ---------- 结算账户 ----------

export async function listSettlements(carrierId: number) {
  const res = await request.get<ApiResult<CarrierSettlement[]>>(
    `${BASE}/${carrierId}/settlements`
  );
  if (res.data.code === 0) return res.data.data ?? [];
  return Promise.reject(new Error(res.data.message));
}

export async function addSettlement(carrierId: number, data: CarrierSettlement) {
  const res = await request.post<ApiResult<CarrierSettlement>>(
    `${BASE}/${carrierId}/settlements`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateSettlement(
  carrierId: number,
  data: CarrierSettlement
) {
  const res = await request.put<ApiResult<CarrierSettlement>>(
    `${BASE}/${carrierId}/settlements/${data.id}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function setDefaultSettlement(
  carrierId: number,
  settlementId: number
) {
  const res = await request.put<ApiResult<CarrierSettlement>>(
    `${BASE}/${carrierId}/settlements/${settlementId}/default`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function toggleSettlementStatus(
  carrierId: number,
  settlementId: number
) {
  const res = await request.put<ApiResult<CarrierSettlement>>(
    `${BASE}/${carrierId}/settlements/${settlementId}/toggle-status`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeSettlement(carrierId: number, settlementId: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `${BASE}/${carrierId}/settlements/${settlementId}`
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

// ---------- 邀请激活（路径 B） ----------

/**
 * 弹框打开时按手机号查注册状态，决定是显示"邀请生成"还是"请联系对方管理员"。
 */
export async function checkInvitePhone(phone: string) {
  const res = await request.get<ApiResult<CarrierInvitePhoneCheckResult>>(
    `${BASE}/invite/check-phone`,
    { params: { phone } }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function inviteCarrier(
  carrierId: number,
  data: CarrierInviteRequest = { channel: 'link' }
) {
  const res = await request.post<ApiResult<CarrierInviteResponse>>(
    `${BASE}/${carrierId}/invite`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function revokeCarrierInvite(
  carrierId: number,
  reason?: string
) {
  const res = await request.post<ApiResult<unknown>>(
    `${BASE}/${carrierId}/revoke-invite`,
    { reason }
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function listCarrierInvitations(carrierId: number) {
  const res = await request.get<ApiResult<CarrierInvitation[]>>(
    `${BASE}/${carrierId}/invitations`
  );
  if (res.data.code === 0) return res.data.data ?? [];
  return Promise.reject(new Error(res.data.message));
}
