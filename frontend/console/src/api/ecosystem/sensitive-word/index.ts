import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type {
  ImportResult,
  SensitiveWord,
  SensitiveWordOptions,
  SensitiveWordParam,
  SensitiveWordSave,
  WordTestResult
} from './model';

const BASE = '/system/sensitive-word';

interface PageResult {
  list: SensitiveWord[];
  count: number;
}

/** 分页查询敏感词 */
export async function pageSensitiveWords(params: SensitiveWordParam) {
  const res = await request.get<ApiResult<PageResult>>(`${BASE}/page`, {
    params
  });
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 分类 / 处置 / 范围选项 */
export async function getWordOptions() {
  const res = await request.get<ApiResult<SensitiveWordOptions>>(
    `${BASE}/options`
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 新增敏感词 */
export async function addSensitiveWord(data: SensitiveWordSave) {
  const res = await request.post<ApiResult<unknown>>(BASE, data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 修改敏感词 */
export async function updateSensitiveWord(data: SensitiveWordSave) {
  const res = await request.put<ApiResult<unknown>>(BASE, data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 批量启用 / 停用 */
export async function setSensitiveWordStatus(ids: number[], status: number) {
  const res = await request.put<ApiResult<unknown>>(`${BASE}/status`, {
    ids,
    status
  });
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 批量删除 */
export async function removeSensitiveWords(ids: number[]) {
  const res = await request.post<ApiResult<unknown>>(`${BASE}/delete`, { ids });
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 批量导入 */
export async function importSensitiveWords(data: {
  words: string[];
  category: number;
  action: number;
  scope: string;
}) {
  const res = await request.post<ApiResult<ImportResult>>(
    `${BASE}/batch-import`,
    data
  );
  if (res.data.code === 0) {
    return { result: res.data.data as ImportResult, message: res.data.message };
  }
  return Promise.reject(new Error(res.data.message));
}

/** 试测一段文字会不会被拦下 */
export async function testSensitiveText(text: string, scope: string) {
  const res = await request.post<ApiResult<WordTestResult>>(`${BASE}/test`, {
    text,
    scope
  });
  if (res.data.code === 0 && res.data.data) {
    return { result: res.data.data, message: res.data.message };
  }
  return Promise.reject(new Error(res.data.message));
}
