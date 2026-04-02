import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { TenantOperationLog, TenantOperationLogParam } from './model';

/**
 * 分页查询租户操作日志
 */
export async function pageTenantOperationLogs(
  params: TenantOperationLogParam
) {
  const res = await request.get<ApiResult<PageResult<TenantOperationLog>>>(
    '/log-center/operation-log/page',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 查询租户操作日志列表（不分页，用于导出）
 */
export async function listTenantOperationLogs(
  params?: TenantOperationLogParam
) {
  const res = await request.get<ApiResult<TenantOperationLog[]>>(
    '/log-center/operation-log',
    { params }
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 获取租户操作日志详情
 */
export async function getTenantOperationLog(id: number) {
  const res = await request.get<ApiResult<TenantOperationLog>>(
    `/log-center/operation-log/${id}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
