import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { Organization, OrganizationParam } from './model';

/**
 * 分页查询机构
 */
export async function pageOrganizations(params: OrganizationParam) {
  const res = await request.get<ApiResult<PageResult<Organization>>>(
    '/system/organization/page',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 查询机构列表
 */
export async function listOrganizations(params?: OrganizationParam) {
  const res = await request.get<ApiResult<Organization[]>>(
    '/system/organization',
    { params }
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 查询机构列表树
 */
export async function listOrganizationsTree(params?: OrganizationParam) {
  const res = await request.get<ApiResult<Organization[]>>(
    '/system/organization/tree',
    { params }
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 添加机构
 */
export async function addOrganization(data: Organization) {
  const res = await request.post<ApiResult<unknown>>(
    '/system/organization',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 修改机构
 */
export async function updateOrganization(data: Organization) {
  const res = await request.put<ApiResult<unknown>>(
    '/system/organization',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 删除机构
 */
export async function removeOrganization(id?: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/system/organization/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
