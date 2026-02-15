import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { UserFile, UserFileParam } from './model';

/**
 * 分页查询用户文件
 */
export async function pageUserFiles(params: UserFileParam) {
  const res = await request.get<ApiResult<PageResult<UserFile>>>(
    '/system/user-file/page',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 查询用户文件列表
 */
export async function listUserFiles(params: UserFileParam) {
  const res = await request.get<ApiResult<UserFile[]>>('/system/user-file', {
    params
  });
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 添加用户文件
 */
export async function addUserFile(data: UserFile) {
  const res = await request.post<ApiResult<unknown>>('/system/user-file', data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 修改用户文件
 */
export async function updateUserFile(data: UserFile) {
  const res = await request.put<ApiResult<unknown>>('/system/user-file', data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 删除用户文件
 */
export async function removeUserFile(id?: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/system/user-file/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 批量删除用户文件
 */
export async function removeUserFiles(data: (number | undefined)[]) {
  const res = await request.delete<ApiResult<unknown>>(
    '/system/user-file/batch',
    { data }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
