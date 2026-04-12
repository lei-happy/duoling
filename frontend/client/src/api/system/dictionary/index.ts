import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { Dictionary, DictionaryParam } from './model';

/**
 * 分页查询字典列表
 */
export async function pageDictionaries(params: DictionaryParam) {
  const res = await request.get<ApiResult<Dictionary[]>>(
    '/system/dictionary/page',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 查询字典列表
 */
export async function listDictionaries(params?: DictionaryParam) {
  const res = await request.get<ApiResult<Dictionary[]>>('/system/dictionary', {
    params
  });
  if (res.data.code === 0) {
    return res.data.data ?? [];
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 添加字典（请求体字段与企业端 BizDictCreate 对齐）
 */
export async function addDictionary(data: Dictionary) {
  const res = await request.post<ApiResult<unknown>>('/system/dictionary', {
    dictCode: data.dictCode,
    dictName: data.dictName,
    sortOrder: data.sortNumber ?? 0,
    remark: data.comments
  });
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 修改字典（PUT /system/dictionary/{dictId}）
 */
export async function updateDictionary(data: Dictionary) {
  const id = data.dictId;
  if (id == null) {
    return Promise.reject(new Error('缺少字典 ID'));
  }
  const res = await request.put<ApiResult<unknown>>(
    `/system/dictionary/${id}`,
    {
      dictName: data.dictName,
      sortOrder: data.sortNumber,
      remark: data.comments
    }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 删除字典
 */
export async function removeDictionary(id?: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/system/dictionary/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
