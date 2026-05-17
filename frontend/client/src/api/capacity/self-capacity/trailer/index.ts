import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { Trailer, TrailerParam } from './model';

const BASE = '/capacity/self_capacity/trailer';

export async function pageTrailers(params: TrailerParam) {
  const res = await request.get<ApiResult<PageResult<Trailer>>>(BASE, {
    params
  });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getTrailer(id: number) {
  const res = await request.get<ApiResult<Trailer>>(`${BASE}/${id}`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addTrailer(data: Trailer) {
  const res = await request.post<ApiResult<unknown>>(BASE, data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateTrailer(data: Trailer) {
  const res = await request.put<ApiResult<unknown>>(
    `${BASE}/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeTrailer(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${id}`);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
