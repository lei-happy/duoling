import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { SmsCode, SmsCodeParam } from './model';

export async function pageSmsCodes(params: SmsCodeParam) {
  const res = await request.get<ApiResult<PageResult<SmsCode>>>(
    '/system/sms-code/page',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listSmsCodes(params?: SmsCodeParam) {
  const res = await request.get<ApiResult<SmsCode[]>>('/system/sms-code', {
    params
  });
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
