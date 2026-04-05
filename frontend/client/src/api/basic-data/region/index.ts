import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { Region, RegionNavNode, RegionParam } from './model';

/**
 * 获取省+市两级导航树（左侧面板）
 */
export async function getRegionNavTree() {
  const res = await request.get<ApiResult<RegionNavNode[]>>(
    '/basic-data/region/nav-tree'
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 分页查询指定节点的子地区列表（右侧表格）
 */
export async function pageRegionChildren(params: RegionParam) {
  const res = await request.get<ApiResult<PageResult<Region>>>(
    '/basic-data/region/children',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 获取地区子级列表（懒加载树）
 */
export async function getRegionTree(parentCode?: string | null) {
  const res = await request.get<ApiResult<Region[]>>(
    '/basic-data/region/tree',
    { params: { parentCode } }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 搜索地区
 */
export async function searchRegions(params: RegionParam) {
  const res = await request.get<ApiResult<Region[]>>(
    '/basic-data/region/search',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 获取地区详情
 */
export async function getRegion(id: number) {
  const res = await request.get<ApiResult<Region>>(
    `/basic-data/region/${id}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 新增自定义地区
 */
export async function addRegion(data: {
  name: string;
  parentCode?: string | null;
  sortOrder?: number;
  status?: number;
  longitude?: number;
  latitude?: number;
}) {
  const res = await request.post<ApiResult<Region>>(
    '/basic-data/region',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 修改自定义地区
 */
export async function updateRegion(
  id: number,
  data: {
    name?: string;
    parentCode?: string | null;
    sortOrder?: number;
    status?: number;
    longitude?: number;
    latitude?: number;
  }
) {
  const res = await request.put<ApiResult<Region>>(
    `/basic-data/region/${id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 删除自定义地区
 */
export async function removeRegion(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/basic-data/region/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
