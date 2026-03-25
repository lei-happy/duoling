import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { ProductVersion, ProductFeature, VersionFeature } from './model';

export async function listVersions(params?: {
  page?: number;
  page_size?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: ProductVersion[]; total: number }>
  >('/product-version', { params });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addVersion(data: ProductVersion) {
  const res = await request.post<ApiResult<unknown>>('/product-version', data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateVersion(data: ProductVersion) {
  const res = await request.put<ApiResult<unknown>>(
    `/product-version/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeVersion(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/product-version/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listFeatures(params?: {
  module?: string;
  status?: number;
}) {
  const res = await request.get<ApiResult<ProductFeature[]>>(
    '/product-feature',
    { params }
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addFeature(data: ProductFeature) {
  const res = await request.post<ApiResult<unknown>>(
    '/product-feature',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateFeature(data: ProductFeature) {
  const res = await request.put<ApiResult<unknown>>(
    `/product-feature/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeFeature(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/product-feature/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getVersionFeatures(versionId: number) {
  const res = await request.get<ApiResult<VersionFeature[]>>(
    `/product-feature/version/${versionId}`
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function assignVersionFeatures(
  versionId: number,
  featureIds: number[]
) {
  const res = await request.post<ApiResult<unknown>>(
    '/product-feature/version/assign',
    { version_id: versionId, feature_ids: featureIds }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
