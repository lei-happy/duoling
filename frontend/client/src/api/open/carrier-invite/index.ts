import axios from 'axios';
import type { ApiResult } from '@/api';

export interface CarrierInviteInfo {
  inviteCode: string;
  sourceTenantName: string;
  expectedCarrierName: string;
  invitePhoneMasked: string;
  invitePath: string;
  status: number;
  expiresAt: string;
  expired: boolean;
  userExisted: boolean;
}

export interface CarrierInviteActivatePayload {
  inviteCode: string;
  contactPhone: string;
  smsCode: string;
  realName: string;
  tenantName: string;
  shortName?: string;
}

export interface CarrierInviteActivateResult {
  tenantCode: string;
  tenantName: string;
  versionCode: string;
  accessToken: string;
  refreshToken?: string;
  message: string;
}

const BASE = '/api/open/carrier-invite';

export async function getInviteInfo(inviteCode: string) {
  const res = await axios.get<ApiResult<CarrierInviteInfo>>(
    `${BASE}/${inviteCode}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function activateInvite(payload: CarrierInviteActivatePayload) {
  const res = await axios.post<ApiResult<CarrierInviteActivateResult>>(
    `${BASE}/activate`,
    payload
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}
