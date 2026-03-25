import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { Route, RouteParam } from './model';

export async function pageRoutes(params: RouteParam) {
  const res = await request.get<ApiResult<PageResult<Route>>>(
    '/resource/route',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listRoutes(params?: RouteParam) {
  const res = await request.get<ApiResult<Route[]>>(
    '/resource/route/list',
    { params }
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addRoute(data: Route) {
  const res = await request.post<ApiResult<unknown>>(
    '/resource/route',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateRoute(data: Route) {
  const res = await request.put<ApiResult<unknown>>(
    `/resource/route/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeRoute(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/resource/route/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
