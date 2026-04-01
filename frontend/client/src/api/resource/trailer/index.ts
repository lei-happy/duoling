import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { Trailer, TrailerParam } from './model';

export async function pageTrailers(params: TrailerParam) {
  const res = await request.get<ApiResult<PageResult<Trailer>>>(
    '/resource/trailer',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getTrailer(id: number) {
  const res = await request.get<ApiResult<Trailer>>(
    `/resource/trailer/${id}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addTrailer(data: Trailer) {
  const res = await request.post<ApiResult<unknown>>(
    '/resource/trailer',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateTrailer(data: Trailer) {
  const res = await request.put<ApiResult<unknown>>(
    `/resource/trailer/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeTrailer(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/resource/trailer/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
