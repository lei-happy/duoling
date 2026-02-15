import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { FileRecord, FileRecordParam } from './model';
import type { AxiosRequestConfig } from 'axios';

/**
 * 上传文件
 * @param file 文件
 * @param config 请求配置
 * @param fileName 文件名称
 */
export async function uploadFile(
  file: File,
  config?: AxiosRequestConfig,
  fileName?: string
) {
  const formData = new FormData();
  formData.append('file', file, fileName);
  const res = await request.post<ApiResult<FileRecord>>(
    '/file/upload',
    formData,
    config
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 上传base64文件
 * @param base64 base64数据
 * @param fileName 文件名称
 */
export async function uploadBase64File(base64: string, fileName?: string) {
  const formData = new FormData();
  formData.append('base64', base64);
  if (fileName) {
    formData.append('fileName', fileName);
  }
  const res = await request.post<ApiResult<FileRecord>>(
    '/file/upload/base64',
    formData
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 分页查询文件上传记录
 */
export async function pageFiles(params: FileRecordParam) {
  const res = await request.get<ApiResult<PageResult<FileRecord>>>(
    '/file/page',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 查询文件上传记录列表
 */
export async function listFiles(params: FileRecordParam) {
  const res = await request.get<ApiResult<FileRecord[]>>('/file/list', {
    params
  });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 删除文件
 */
export async function removeFile(id?: number) {
  const res = await request.delete<ApiResult<unknown>>(`/file/remove/${id}`);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 批量删除文件
 */
export async function removeFiles(data: (number | undefined)[]) {
  const res = await request.delete<ApiResult<unknown>>('/file/remove/batch', {
    data
  });
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
