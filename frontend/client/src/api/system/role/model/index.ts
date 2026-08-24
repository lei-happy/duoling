import type { PageParam } from '@/api';

/** 小程序岗位视图。只决定首页先看什么，不参与鉴权。 */
export const ROLE_PERSONAS = [
  { value: 'dispatch', label: '调度' },
  { value: 'boss', label: '老板' },
  { value: 'finance', label: '财务' },
  { value: 'captain', label: '车队长' }
] as const;

export type RolePersona = (typeof ROLE_PERSONAS)[number]['value'];

export function personaLabel(value?: string | null): string {
  const hit = ROLE_PERSONAS.find((item) => item.value === value);
  return hit?.label || '';
}

export function formatPersonaLabels(values?: string[] | null): string[] {
  if (!values?.length) {
    return [];
  }
  const set = new Set(values);
  return ROLE_PERSONAS.filter((item) => set.has(item.value)).map((item) => item.label);
}

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
  /** 小程序岗位视图（可多选） */
  personas?: RolePersona[] | string[];
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
