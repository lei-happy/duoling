import { PageParam } from '@/api';

/**
 * 机构
 */
export interface Organization {
  /** 机构id */
  organizationId?: number;
  /** 上级id, 0是顶级 */
  parentId?: number;
  /** 机构名称 */
  organizationName?: string;
  /** 机构全称 */
  organizationFullName?: string;
  /** 机构代码 */
  organizationCode?: string;
  /** 机构类型(字典) */
  organizationType?: string;
  /** 排序号 */
  sortNumber?: number;
  /** 备注 */
  comments?: string;
  /** 创建时间 */
  createTime?: string;
  /** 机构类型名称 */
  organizationTypeName?: string;
  /** 子级 */
  children?: Organization[];
}

/**
 * 机构搜索条件
 */
export interface OrganizationParam extends PageParam {
  /** 机构名称 */
  organizationName?: string;
  /** 机构全称 */
  organizationFullName?: string;
  /** 机构类型(字典) */
  organizationType?: string;
}
