import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { SystemConfig } from './model';

export async function listConfigs() {
  const res = await request.get<ApiResult<SystemConfig[]>>(
    '/system/config'
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listConfigsByGroup(group: string) {
  const res = await request.get<ApiResult<SystemConfig[]>>(
    `/system/config/group/${group}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateConfig(key: string, configValue: string) {
  const res = await request.put<ApiResult<SystemConfig>>(
    `/system/config/${key}`,
    { configValue }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
