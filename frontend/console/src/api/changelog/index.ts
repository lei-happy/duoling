import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { Changelog, ChangelogParam } from './model';

interface ChangelogPageResult {
  list: Changelog[];
  total: number;
  page: number;
  limit: number;
}

/**
 * 分页查询更新记录
 */
export async function pageChangelogs(params: ChangelogParam) {
  const res = await request.get<ApiResult<ChangelogPageResult>>('/changelog', {
    params: {
      page: params.page,
      limit: params.limit,
      status: params.status
    }
  });
  if (res.data.code === 0 && res.data.data) {
    const d = res.data.data;
    return { list: d.list, count: d.total };
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 获取更新记录详情
 */
export async function getChangelog(id: number) {
  const res = await request.get<ApiResult<Changelog>>(`/changelog/${id}`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 添加更新记录
 */
export async function addChangelog(data: Partial<Changelog>) {
  const res = await request.post<ApiResult<unknown>>('/changelog', data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 修改更新记录
 */
export async function updateChangelog(id: number, data: Partial<Changelog>) {
  const res = await request.put<ApiResult<unknown>>(`/changelog/${id}`, data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 删除更新记录
 */
export async function removeChangelog(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`/changelog/${id}`);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
