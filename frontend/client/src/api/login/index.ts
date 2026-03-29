import axios from 'axios';
import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { LoginParam, LoginResult, CaptchaResult, TenantOption } from './model';

/**
 * 客户端登录（手机号 + 密码）
 * 可能返回正常登录结果或多企业选择列表
 */
export async function login(data: LoginParam) {
  const res = await request.post<ApiResult<LoginResult>>('/auth/login', data);
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 发送短信验证码
 */
export async function sendSmsCode(phone: string, purpose: number) {
  const res = await axios.post<ApiResult<{ message: string; code: string }>>(
    '/api/open/sms/send',
    { phone, purpose, app_type: 'client' }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 客户端验证码登录
 */
export async function smsLogin(
  phone: string,
  code: string,
  tenantCode?: string
) {
  const res = await request.post<ApiResult<LoginResult>>('/auth/sms-login', {
    phone,
    code,
    tenant_code: tenantCode
  });
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 短信验证码重置密码
 */
export async function resetPasswordBySms(
  phone: string,
  code: string,
  newPassword: string
) {
  const res = await axios.post<ApiResult<void>>('/api/open/sms/reset-password', {
    phone,
    code,
    newPassword
  });
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 修改密码
 */
export async function changePassword(data: {
  oldPassword: string;
  newPassword: string;
}) {
  const res = await request.put<ApiResult<void>>('/auth/password', data);
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 获取当前用户关联的所有有效租户列表
 */
export async function getUserTenants() {
  const res = await request.get<ApiResult<TenantOption[]>>('/auth/user-tenants');
  if (res.data.code === 0) {
    return res.data.data ?? [];
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 切换到目标租户
 */
export async function switchTenant(tenantCode: string) {
  const res = await request.post<ApiResult<LoginResult>>('/auth/switch-tenant', {
    tenant_code: tenantCode
  });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 获取验证码（预留）
 */
export async function getCaptcha() {
  const res = await request.get<ApiResult<CaptchaResult>>('/captcha');
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 退出登录
 */
export async function logout() {
  return '退出登录成功';
}
