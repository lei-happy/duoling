import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { ClientMenu, ClientMenuParam } from './model';

/**
 * 查询客户端菜单列表
 */
export async function listClientMenus(params?: ClientMenuParam) {
  const res = await request.get<ApiResult<ClientMenu[]>>(
    '/system/client-menu',
    { params }
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 添加客户端菜单
 */
export async function addClientMenu(data: ClientMenu) {
  const res = await request.post<ApiResult<unknown>>(
    '/system/client-menu',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 修改客户端菜单
 */
export async function updateClientMenu(data: ClientMenu) {
  const res = await request.put<ApiResult<unknown>>(
    '/system/client-menu',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 删除客户端菜单
 */
export async function removeClientMenu(id?: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/system/client-menu/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
