import { get, post, put } from './request';

export interface DriverUserInfo {
  userId: number;
  phone: string;
  realName?: string;
  avatar?: string;
  tenantCode?: string;
  tenantName?: string;
  driverId?: number;
  driverCode?: string;
  forceChangePwd?: number;
  roles: string[];
  permissions: string[];
  menus?: unknown[];
}

export interface LoginResponseData {
  accessToken: string;
  refreshToken: string;
  user: DriverUserInfo;
}

export interface TenantOption {
  tenantCode: string;
  tenantName: string;
}

export interface MultiTenantData {
  tenants: TenantOption[];
}

export type LoginResultUnion = LoginResponseData | MultiTenantData;

export function loginByPassword(payload: {
  phone: string;
  password: string;
  tenantCode?: string;
}) {
  return post<LoginResultUnion>('/auth/login', payload);
}

export function loginBySms(payload: { phone: string; code: string; tenantCode?: string }) {
  return post<LoginResultUnion>('/auth/sms-login', payload);
}

export function refreshToken(payload: { refreshToken: string }) {
  return post<LoginResponseData>('/auth/refresh', payload);
}

export function getUserInfo() {
  return get<DriverUserInfo>('/auth/user-info');
}

export function getUserTenants() {
  return get<TenantOption[]>('/auth/user-tenants');
}

export function switchTenant(payload: { tenantCode: string }) {
  return post<LoginResponseData>('/auth/switch-tenant', payload);
}

export function changePassword(payload: { oldPassword: string; newPassword: string }) {
  return put<void>('/auth/password', payload);
}

// 短信发送（与 client 端共用 /api/open/sms/send；driver 复用 client 的校验策略）
export function sendSmsCode(payload: { phone: string; purpose: number }) {
  return fetch('/api/open/sms/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...payload, app_type: 'client' })
  }).then(async (r) => {
    const j = await r.json();
    if (j.code !== 0) throw new Error(j.message || '验证码发送失败');
    return j.data;
  });
}
