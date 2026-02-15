import { debounce } from 'lodash-es';
import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { User } from '@/api/system/user/model';
import type { UpdatePasswordParam } from './model';

/**
 * 获取当前登录用户的个人信息/菜单/权限/角色
 * @param toRoute 路由守卫中要进入的路由
 */
export async function getUserInfo(toRoute: any): Promise<User> {
  const res = await request.get<ApiResult<User>>('/auth/user-info', {
    toRoute
  } as any);
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 修改当前登录用户的密码
 */
export async function updatePassword(
  data: UpdatePasswordParam
): Promise<string> {
  const res = await request.put<ApiResult<unknown>>('/user/me/password', data);
  if (res.data.code === 0) {
    return res.data.message ?? '修改成功';
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 修改当前登录用户的个人信息
 */
export async function updateUserInfo(data: User): Promise<User> {
  const res = await request.put<ApiResult<User>>('/auth/user', data);
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 保存当前登录用户的主题配置到服务端
 */
async function _saveThemeConfig(
  themeConfig: Record<string, any> | null
): Promise<void> {
  try {
    await request.put<ApiResult<unknown>>('/auth/user-theme', { themeConfig });
  } catch (e) {
    console.error('保存主题配置失败', e);
  }
}

/**
 * 保存主题配置（防抖，避免频繁请求）
 */
export const saveThemeConfig = debounce(_saveThemeConfig, 1500);
