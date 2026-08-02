import type { PageParam } from '@/api';

/**
 * 角色
 */
export interface Role {
  /** 角色id */
  roleId?: number;
  /** 角色标识 */
  roleCode?: string;
  /** 角色名称 */
  roleName?: string;
  /** 备注 */
  comments?: string;
  /** 创建时间 */
  createTime?: string;
  /** 关联用户数 */
  userCount?: number;
  /** 已授权菜单数 */
  menuCount?: number;
}

/**
 * 角色搜索条件
 */
export interface RoleParam extends PageParam {
  /** 角色名称 */
  roleName?: string;
  /** 角色标识 */
  roleCode?: string;
  /** 备注 */
  comments?: string;
}
