import type { PageParam } from '@/api';

/**
 * 企业（租户）
 */
export interface Tenant {
  /** 租户ID */
  id?: number;
  /** 租户编码 */
  tenantCode?: string;
  /** 企业名称 */
  tenantName?: string;
  /** 企业简称 */
  shortName?: string;
  /** 联系人 */
  contactPerson?: string;
  /** 联系电话 */
  contactPhone?: string;
  /** 联系邮箱 */
  contactEmail?: string;
  /** 省份 */
  province?: string;
  /** 城市 */
  city?: string;
  /** 详细地址 */
  address?: string;
  /** 企业Logo */
  logo?: string;
  /** 营业执照号 */
  licenseNo?: string;
  /** 状态 0-停用 1-正常 2-待审核 3-已过期 */
  status?: number;
  /** 数据库名称 */
  dbName?: string;
  /** 数据库是否已初始化 */
  dbInitialized?: number;
  /** 到期时间 */
  expireTime?: string;
  /** 备注 */
  remark?: string;
  /** 来源渠道: website-官网注册 console-后台录入 referral-企业推荐 */
  sourceChannel?: string;
  /** 推荐人企业编码 */
  referrerCode?: string;
  /** 创建时间 */
  createTime?: string;
}

/**
 * 企业搜索条件
 */
export interface TenantParam extends PageParam {
  /** 关键词（企业名称/编码/联系人） */
  keyword?: string;
  /** 状态 */
  status?: number | string;
}

/**
 * 租户产品授权
 */
export interface TenantProduct {
  /** 授权ID */
  id?: number;
  /** 租户ID */
  tenantId?: number;
  /** 租户编码 */
  tenantCode?: string;
  /** 产品版本ID */
  versionId?: number;
  /** 产品版本编码 */
  versionCode?: string;
  /** 授权开始时间 */
  startTime?: string;
  /** 授权到期时间 */
  endTime?: string;
  /** 状态 */
  status?: number;
  /** 创建时间 */
  createTime?: string;
}

/**
 * 开通产品授权请求参数
 */
export interface TenantProductCreate {
  /** 产品版本ID */
  versionId: number;
  /** 产品版本编码 */
  versionCode: string;
  /** 授权开始时间 */
  startTime?: string;
  /** 授权到期时间 */
  endTime?: string;
}
