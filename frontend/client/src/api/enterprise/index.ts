import request from '@/utils/request';
import type { ApiResult } from '@/api';

/**
 * 企业信息
 */
export interface EnterpriseInfo {
  tenantName: string;
  systemName?: string;
  contactPerson?: string;
  contactPhone?: string;
  version?: VersionInfo;
}

/**
 * 版本信息
 */
export interface VersionInfo {
  versionName?: string;
  versionCode?: string;
  maxUsers?: number;
  maxVehicles?: number;
  startTime?: string;
  endTime?: string;
}

/**
 * 获取企业信息及版本详情
 */
export async function getEnterpriseInfo(): Promise<EnterpriseInfo> {
  const res = await request.get<ApiResult<EnterpriseInfo>>('/enterprise/info');
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 更新系统自定义名称
 */
export async function updateSystemName(
  systemName?: string | null
): Promise<string> {
  const res = await request.put<ApiResult<unknown>>('/enterprise/system-name', {
    systemName
  });
  if (res.data.code === 0) {
    return res.data.message ?? '更新成功';
  }
  return Promise.reject(new Error(res.data.message));
}
