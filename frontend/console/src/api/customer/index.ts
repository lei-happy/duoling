import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  Customer,
  CustomerParam,
  CustomerProduct,
  CustomerProductCreate,
  FollowPoolUpdate,
  LifecycleStats
} from './model';

/**
 * 分页查询客户列表
 */
export async function pageCustomers(params: CustomerParam) {
  const res = await request.get<ApiResult<PageResult<Customer>>>(
    '/tenant/page',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 获取客户详情
 */
export async function getCustomer(id: number) {
  const res = await request.get<ApiResult<Customer>>(`/tenant/${id}`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 注册企业
 */
export async function addCustomer(data: Customer) {
  const res = await request.post<ApiResult<unknown>>('/tenant', data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 修改企业
 */
export async function updateCustomer(data: Customer) {
  const res = await request.put<ApiResult<unknown>>('/tenant', data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 批量删除企业
 */
export async function removeCustomers(data: (number | undefined)[]) {
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
export async function updateCustomerStatus(data: {
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
 * 标记/移出跟进池
 */
export async function updateFollowPool(data: FollowPoolUpdate) {
  const res = await request.put<ApiResult<unknown>>(
    '/tenant/follow-pool',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 各生命周期阶段客户数量统计
 */
export async function getCustomerStats() {
  const res = await request.get<ApiResult<LifecycleStats>>(
    '/tenant/stats'
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 手动触发过期检查
 */
export async function checkExpirations() {
  const res = await request.post<ApiResult<{ affected: number }>>(
    '/tenant/check-expirations'
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 查询客户已授权的产品列表
 */
export async function listCustomerProducts(customerId: number) {
  const res = await request.get<ApiResult<CustomerProduct[]>>(
    `/tenant/${customerId}/products`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 为客户开通产品版本授权
 */
export async function assignCustomerProduct(
  customerId: number,
  data: CustomerProductCreate
) {
  const res = await request.post<ApiResult<unknown>>(
    `/tenant/${customerId}/products`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 取消客户产品授权
 */
export async function removeCustomerProduct(
  customerId: number,
  productId: number
) {
  const res = await request.delete<ApiResult<unknown>>(
    `/tenant/${customerId}/products/${productId}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

// 兼容别名，供其他模块平滑迁移
export {
  pageCustomers as pageTenants,
  addCustomer as addTenant,
  updateCustomer as updateTenant,
  removeCustomers as removeTenants,
  updateCustomerStatus as updateTenantStatus,
  listCustomerProducts as listTenantProducts,
  assignCustomerProduct as assignTenantProduct,
  removeCustomerProduct as removeTenantProduct,
};

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
