import type { PageParam } from '@/api';

/**
 * 客户（企业）
 */
export interface Customer {
  /** ID */
  id?: number;
  /** 企业编码 */
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
  /** 状态 0-停用 1-正常 3-已过期 */
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
  /** 是否在跟进池 0-否 1-是 */
  inFollowPool?: number;
  /** 跟进备注 */
  followRemark?: string;
  /** 创建时间 */
  createTime?: string;
}

/**
 * 客户搜索条件
 */
export interface CustomerParam extends PageParam {
  /** 关键词（企业名称/编码/联系人） */
  keyword?: string;
  /** 状态 */
  status?: number | string;
  /** 生命周期: new/trial/follow_up/paid/churned/all */
  lifecycle?: string;
  /** 版本编码筛选(付费客户): pro/enterprise */
  versionCode?: string;
  /** 仅显示到期预警客户 */
  expireWarning?: boolean;
}

/**
 * 跟进池操作参数
 */
export interface FollowPoolUpdate {
  /** 客户ID */
  id: number;
  /** 是否加入跟进池 0-移出 1-加入 */
  inFollowPool: number;
  /** 跟进备注 */
  followRemark?: string;
}

/**
 * 生命周期统计
 */
export interface LifecycleStats {
  new: number;
  trial: number;
  followUp: number;
  paid: number;
  churned: number;
  all: number;
}

/**
 * 客户产品授权
 */
export interface CustomerProduct {
  /** 授权ID */
  id?: number;
  /** 客户ID */
  tenantId?: number;
  /** 企业编码 */
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
export interface CustomerProductCreate {
  /** 产品版本ID */
  versionId: number;
  /** 产品版本编码 */
  versionCode: string;
  /** 授权开始时间 */
  startTime?: string;
  /** 授权到期时间 */
  endTime?: string;
}

// 兼容别名，供其他模块平滑迁移
export type Tenant = Customer;
export type TenantParam = CustomerParam;
export type TenantProduct = CustomerProduct;
export type TenantProductCreate = CustomerProductCreate;
