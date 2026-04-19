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
  /** 创建时间 */
  createTime?: string;
  /** 当前生效版本编码（按 sys_tenant_product 实时计算） */
  currentVersionCode?: string;
  /** 当前生效版本名称 */
  currentVersionName?: string;
  /** 当前有效授权数量（≥2 表示存在叠加） */
  activeProductCount?: number;
}

/**
 * 客户搜索条件
 */
export interface CustomerParam extends PageParam {
  /** 关键词（企业名称/编码/联系人） */
  keyword?: string;
  /** 状态 */
  status?: number | string;
  /** 生命周期: trial/paid/churned */
  lifecycle?: string;
  /** 版本编码筛选(付费客户): standard/pro/enterprise */
  versionCode?: string;
  /** 仅显示到期预警客户 */
  expireWarning?: boolean;
}

/**
 * 生命周期统计
 */
export interface LifecycleStats {
  trial: number;
  paid: number;
  churned: number;
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
  /** 产品版本名称 */
  versionName?: string;
  /** 授权开始时间 */
  startTime?: string;
  /** 授权到期时间 */
  endTime?: string;
  /** 开通类型(数据字典 grant_type) */
  grantType?: string;
  /** 开通备注 */
  grantRemark?: string;
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
  /** 开通类型(数据字典 grant_type) */
  grantType?: string;
  /** 开通备注 */
  grantRemark?: string;
  /**
   * 替换语义：true 时先取消其他生效授权再开通本次授权
   * 用于"切换版本"场景，避免新旧版本菜单叠加
   */
  replaceActive?: boolean;
}

// 兼容别名，供其他模块平滑迁移
export type Tenant = Customer;
export type TenantParam = CustomerParam;
export type TenantProduct = CustomerProduct;
export type TenantProductCreate = CustomerProductCreate;
