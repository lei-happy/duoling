import type { PageParam } from '@/api';
import type { Role } from '../../role/model';
import type { Menu } from '../../menu/model';

/**
 * 用户
 */
export interface User {
  /** 用户id */
  userId?: number;
  /** 手机号 */
  phone?: string;
  /** 昵称 */
  nickname?: string;
  /** 头像 */
  avatar?: string;
  /** 性别(字典) */
  sex?: string;
  /** 邮箱 */
  email?: string;
  /** 出生日期 */
  birthday?: string;
  /** 个人简介 */
  introduction?: string;
  /** 机构id */
  organizationId?: number;
  /** 状态, 0正常, 1冻结 */
  status?: number;
  /** 性别名称 */
  sexName?: string;
  /** 机构名称 */
  organizationName?: string;
  /** 角色列表 */
  roles?: Role[];
  /** 权限列表 */
  authorities?: Menu[];
  /** 创建时间 */
  createTime?: string;
  /** 街道地址 */
  address?: string;
  /** 联系电话前缀 */
  tellPre?: string;
  /** 联系电话 */
  tell?: string;
  /** 企业名称 */
  tenantName?: string;
  /** 系统自定义名称 */
  systemName?: string;
  /** 用户类型 1-管理员 2-用户 3-驾驶员 */
  userType?: number;
  /** 主题配置 */
  themeConfig?: Record<string, any>;
  /** 菜单版本戳：与 /auth/menu-version 比对，不一致需重新拉取菜单 */
  menuVersion?: number;
  /** 当前租户已启用的产品功能码（仅 client 端有值） */
  features?: string[];
}

/**
 * 用户搜索条件
 */
export interface UserParam extends PageParam {
  /** 昵称 */
  nickname?: string;
  /** 性别(字典) */
  sex?: string;
  /** 手机号 */
  phone?: string;
  /** 状态 */
  status?: number;
  /** 机构id */
  organizationId?: number;
  /** 性别名称 */
  sexName?: string;
  /** 机构名称 */
  organizationName?: string;
  /** 邮箱 */
  email?: string;
  /** 创建时间开始时间 */
  createTimeStart?: string;
  /** 创建时间截止时间 */
  createTimeEnd?: string;
}
