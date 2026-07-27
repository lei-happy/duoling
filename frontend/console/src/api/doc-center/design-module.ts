import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type {
  DesignModule,
  DesignModuleForm,
  DesignModuleParam,
  DesignModuleSortItem
} from './model/design-module';

/**
 * 分页列表
 */
export async function pageDesignModules(params: DesignModuleParam) {
  const res = await request.get<
    ApiResult<{
      list: DesignModule[];
      total: number;
      page: number;
      limit: number;
    }>
  >('/doc-center/design-modules', { params });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 看板数据（按状态分组）
 */
export async function boardDesignModules(params?: DesignModuleParam) {
  const res = await request.get<
    ApiResult<{ board: Record<string, DesignModule[]> }>
  >('/doc-center/design-modules', {
    params: { ...params, view: 'board' }
  });
  if (res.data.code === 0) {
    return res.data.data?.board ?? {};
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 详情
 */
export async function getDesignModule(id: number) {
  const res = await request.get<ApiResult<DesignModule>>(
    `/doc-center/design-modules/${id}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 创建
 */
export async function createDesignModule(data: DesignModuleForm) {
  const res = await request.post<ApiResult<DesignModule>>(
    '/doc-center/design-modules',
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 更新
 */
export async function updateDesignModule(id: number, data: DesignModuleForm) {
  const res = await request.put<ApiResult<DesignModule>>(
    `/doc-center/design-modules/${id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 更新状态
 */
export async function updateDesignModuleStatus(id: number, status: number) {
  const res = await request.patch<ApiResult<DesignModule>>(
    `/doc-center/design-modules/${id}/status`,
    { status }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 更新优先级
 */
export async function updateDesignModulePriority(id: number, priority: number) {
  const res = await request.patch<ApiResult<DesignModule>>(
    `/doc-center/design-modules/${id}/priority`,
    { priority }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 批量排序
 */
export async function sortDesignModules(items: DesignModuleSortItem[]) {
  const res = await request.put<ApiResult<unknown>>(
    '/doc-center/design-modules/sort',
    { items }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 删除
 */
export async function removeDesignModule(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/doc-center/design-modules/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
