import request from '@/utils/request';
import type { ApiResult } from '@/api';

export interface OpenRegisterPolicy {
  versionCode: string;
  trialDays: number;
}

export async function getOpenRegisterPolicy() {
  const res = await request.get<ApiResult<OpenRegisterPolicy>>(
    '/system/open-register-policy'
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateOpenRegisterPolicy(data: OpenRegisterPolicy) {
  const res = await request.put<ApiResult<OpenRegisterPolicy>>(
    '/system/open-register-policy',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
