import axios from 'axios';
import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { LoginParam, LoginResult, CaptchaResult } from './model';

/**
 * 平台管理后台登录（密码）
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
    { phone, purpose, app_type: 'console' }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 平台管理后台验证码登录
 */
export async function smsLogin(phone: string, code: string) {
  const res = await request.post<ApiResult<LoginResult>>('/auth/sms-login', {
    phone,
    code
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
