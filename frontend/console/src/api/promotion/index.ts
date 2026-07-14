import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type {
  Banner,
  BannerParam,
  BannerOption,
  BannerStats,
  BannerEvent
} from './model';

interface ListResult<T> {
  list: T[];
  total: number;
  page: number;
  limit: number;
}

/** 分页查询 Banner */
export async function pageBanners(params: BannerParam) {
  const res = await request.get<ApiResult<ListResult<Banner>>>(
    '/promotion/banner/page',
    { params }
  );
  if (res.data.code === 0 && res.data.data) {
    return { list: res.data.data.list, count: res.data.data.total };
  }
  return Promise.reject(new Error(res.data.message));
}

/** Banner 详情 */
export async function getBanner(id: number) {
  const res = await request.get<ApiResult<Banner>>(`/promotion/banner/${id}`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 新建 Banner */
export async function addBanner(data: Partial<Banner>) {
  const res = await request.post<ApiResult<Banner>>('/promotion/banner', data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 更新 Banner */
export async function updateBanner(id: number, data: Partial<Banner>) {
  const res = await request.put<ApiResult<Banner>>(
    `/promotion/banner/${id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 删除 Banner */
export async function removeBanner(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/promotion/banner/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 上线 */
export async function publishBanner(id: number) {
  const res = await request.post<ApiResult<unknown>>(
    `/promotion/banner/${id}/publish`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 下线 */
export async function offlineBanner(id: number) {
  const res = await request.post<ApiResult<unknown>>(
    `/promotion/banner/${id}/offline`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 产品版本下拉 */
export async function getVersionOptions() {
  const res = await request.get<ApiResult<BannerOption[]>>(
    '/promotion/banner/version-options'
  );
  if (res.data.code === 0) {
    return res.data.data || [];
  }
  return Promise.reject(new Error(res.data.message));
}

/** 租户下拉 */
export async function getTenantOptions(keyword?: string) {
  const res = await request.get<ApiResult<BannerOption[]>>(
    '/promotion/banner/tenant-options',
    { params: { keyword } }
  );
  if (res.data.code === 0) {
    return res.data.data || [];
  }
  return Promise.reject(new Error(res.data.message));
}

/** 聚合统计 */
export async function getBannerStats(id: number) {
  const res = await request.get<ApiResult<BannerStats>>(
    `/promotion/banner/${id}/stats`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 事件明细分页 */
export async function pageBannerEvents(
  id: number,
  params: {
    page: number;
    limit: number;
    event_type?: string;
    tenant_code?: string;
  }
) {
  const res = await request.get<ApiResult<ListResult<BannerEvent>>>(
    `/promotion/banner/${id}/events`,
    { params }
  );
  if (res.data.code === 0 && res.data.data) {
    return { list: res.data.data.list, count: res.data.data.total };
  }
  return Promise.reject(new Error(res.data.message));
}
