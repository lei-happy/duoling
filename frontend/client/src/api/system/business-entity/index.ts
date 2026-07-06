import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  BusinessEntity,
  BusinessEntityOption,
  BusinessEntityParam
} from './model';

const BASE = '/system/business-entity';

/**
 * 分页查询经营主体
 */
export async function pageBusinessEntities(params: BusinessEntityParam) {
  const res = await request.get<ApiResult<PageResult<BusinessEntity>>>(
    `${BASE}/page`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 经营主体下拉选项（仅正常状态）
 */
export async function listBusinessEntityOptions() {
  const res = await request.get<ApiResult<BusinessEntityOption[]>>(
    `${BASE}/options`
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 经营主体详情
 */
export async function getBusinessEntity(id: number) {
  const res = await request.get<ApiResult<BusinessEntity>>(`${BASE}/${id}`);
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 新增经营主体
 */
export async function addBusinessEntity(data: BusinessEntity) {
  const res = await request.post<ApiResult<BusinessEntity>>(BASE, data);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 编辑经营主体
 */
export async function updateBusinessEntity(id: number, data: BusinessEntity) {
  const res = await request.put<ApiResult<BusinessEntity>>(
    `${BASE}/${id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 设为默认主体
 */
export async function setDefaultBusinessEntity(id: number) {
  const res = await request.patch<ApiResult<BusinessEntity>>(
    `${BASE}/${id}/default`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 启用/停用主体
 */
export async function toggleBusinessEntityStatus(id: number, status: number) {
  const res = await request.patch<ApiResult<BusinessEntity>>(
    `${BASE}/${id}/status`,
    { status }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 删除经营主体
 */
export async function removeBusinessEntity(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${id}`);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
