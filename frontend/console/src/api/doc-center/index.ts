import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { DocTreeNode, DocContent } from './model';

/**
 * 获取文档目录树
 */
export async function getDocTree() {
  const res = await request.get<ApiResult<DocTreeNode[]>>('/doc-center/tree');
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 获取文档内容
 */
export async function getDocContent(path: string) {
  const res = await request.get<ApiResult<DocContent>>('/doc-center/content', {
    params: { path }
  });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
