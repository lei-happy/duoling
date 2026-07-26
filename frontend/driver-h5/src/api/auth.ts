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
  needSelectTenant?: boolean;
}

export type LoginResultUnion = LoginResponseData | MultiTenantData;

/** 多企业第一步登录后暂存凭证（sessionStorage，避免密码进 URL） */
export const PENDING_LOGIN_KEY = 'zt_driver_pending_login';

export interface PendingLoginCreds {
  phone: string;
  password?: string;
  code?: string;
}

export function savePendingLogin(creds: PendingLoginCreds): void {
  try {
    sessionStorage.setItem(PENDING_LOGIN_KEY, JSON.stringify(creds));
  } catch {
    /* ignore */
  }
}

export function loadPendingLogin(): PendingLoginCreds | null {
  try {
    const raw = sessionStorage.getItem(PENDING_LOGIN_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as PendingLoginCreds;
  } catch {
    return null;
  }
}

export function clearPendingLogin(): void {
  try {
    sessionStorage.removeItem(PENDING_LOGIN_KEY);
  } catch {
    /* ignore */
  }
}

function pickStr(obj: Record<string, unknown>, camel: string, snake: string): string {
  const v = obj[camel] ?? obj[snake];
  return typeof v === 'string' ? v : v != null ? String(v) : '';
}

function pickNum(obj: Record<string, unknown>, camel: string, snake: string): number {
  const v = obj[camel] ?? obj[snake];
  return typeof v === 'number' ? v : Number(v) || 0;
}

/** 将登录/刷新/切换企业响应统一为前端 camelCase，兼容后端 snake_case */
export function normalizeLoginResponse(raw: unknown): LoginResultUnion {
  const data = (raw ?? {}) as Record<string, unknown>;

  // 多企业选择
  if (Array.isArray(data.tenants)) {
    const tenants = (data.tenants as Record<string, unknown>[]).map((t) => ({
      tenantCode: pickStr(t, 'tenantCode', 'tenant_code'),
      tenantName: pickStr(t, 'tenantName', 'tenant_name')
    }));
    return {
      needSelectTenant: data.needSelectTenant !== false,
      tenants
    };
  }

  const userRaw = (data.user ?? {}) as Record<string, unknown>;
  const roles = userRaw.roles;
  const user: DriverUserInfo = {
    userId: pickNum(userRaw, 'userId', 'user_id'),
    phone: pickStr(userRaw, 'phone', 'phone'),
    realName: pickStr(userRaw, 'realName', 'real_name') || undefined,
    avatar: pickStr(userRaw, 'avatar', 'avatar') || undefined,
    tenantCode: pickStr(userRaw, 'tenantCode', 'tenant_code') || undefined,
    tenantName: pickStr(userRaw, 'tenantName', 'tenant_name') || undefined,
    forceChangePwd: pickNum(userRaw, 'forceChangePwd', 'force_change_pwd'),
    roles: Array.isArray(roles) ? (roles as string[]) : [],
    permissions: Array.isArray(userRaw.permissions) ? (userRaw.permissions as string[]) : []
  };

  return {
    accessToken: pickStr(data, 'accessToken', 'access_token'),
    refreshToken: pickStr(data, 'refreshToken', 'refresh_token'),
    user
  };
}

export async function loginByPassword(payload: {
  phone: string;
  password: string;
  tenantCode?: string;
}) {
  const raw = await post<unknown>('/auth/login', {
    phone: payload.phone,
    password: payload.password,
    tenant_code: payload.tenantCode
  });
  return normalizeLoginResponse(raw);
}

export async function loginBySms(payload: {
  phone: string;
  code: string;
  tenantCode?: string;
}) {
  const raw = await post<unknown>('/auth/sms-login', {
    phone: payload.phone,
    code: payload.code,
    tenant_code: payload.tenantCode
  });
  return normalizeLoginResponse(raw);
}

export async function refreshToken(payload: { refreshToken: string }) {
  const raw = await post<unknown>('/auth/refresh', {
    refresh_token: payload.refreshToken
  });
  return normalizeLoginResponse(raw) as LoginResponseData;
}

export function getUserInfo() {
  return get<DriverUserInfo>('/auth/user-info');
}

export function getUserTenants() {
  return get<TenantOption[]>('/auth/user-tenants');
}

export async function switchTenant(payload: { tenantCode: string }) {
  const raw = await post<unknown>('/auth/switch-tenant', {
    tenant_code: payload.tenantCode
  });
  return normalizeLoginResponse(raw) as LoginResponseData;
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
