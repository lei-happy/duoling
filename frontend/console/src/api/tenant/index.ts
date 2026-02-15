import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  Tenant,
  TenantParam,
  TenantProduct,
  TenantProductCreate
} from './model';

/**
 * 分页查询企业列表
 */
export async function pageTenants(params: TenantParam) {
  const res = await request.get<ApiResult<PageResult<Tenant>>>(
    '/tenant/page',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 获取企业详情
 */
export async function getTenant(id: number) {
  const res = await request.get<ApiResult<Tenant>>(`/tenant/${id}`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 注册企业
 */
export async function addTenant(data: Tenant) {
  const res = await request.post<ApiResult<unknown>>('/tenant', data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 修改企业
 */
export async function updateTenant(data: Tenant) {
  const res = await request.put<ApiResult<unknown>>('/tenant', data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 批量删除企业
 */
export async function removeTenants(data: (number | undefined)[]) {
  const res = await request.delete<ApiResult<unknown>>('/tenant/batch', {
    data
  });
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 修改企业状态
 */
export async function updateTenantStatus(data: {
  id: number;
  status: number;
}) {
  const res = await request.put<ApiResult<unknown>>('/tenant/status', data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 查询企业已授权的产品列表
 */
export async function listTenantProducts(tenantId: number) {
  const res = await request.get<ApiResult<TenantProduct[]>>(
    `/tenant/${tenantId}/products`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 为企业开通产品版本授权
 */
export async function assignTenantProduct(
  tenantId: number,
  data: TenantProductCreate
) {
  const res = await request.post<ApiResult<unknown>>(
    `/tenant/${tenantId}/products`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 取消企业产品授权
 */
export async function removeTenantProduct(
  tenantId: number,
  productId: number
) {
  const res = await request.delete<ApiResult<unknown>>(
    `/tenant/${tenantId}/products/${productId}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 查询产品版本列表（用于授权时选择）
 */
export async function listProductVersions() {
  const res = await request.get<ApiResult<any>>('/product-version', {
    params: { page: 1, page_size: 100 }
  });
  if (res.data.code === 0) {
    return res.data.data?.list || [];
  }
  return Promise.reject(new Error(res.data.message));
}
