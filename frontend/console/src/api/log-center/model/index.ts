import { PageParam } from '@/api';

/**
 * 租户操作日志
 */
export interface TenantOperationLog {
  /** 日志ID */
  id?: number;
  /** 用户ID */
  userId?: number;
  /** 操作用户名（一般为登录手机号） */
  username?: string;
  /** 关联租户 biz_user 的真实姓名 */
  realName?: string;
  /** 租户编码 */
  tenantCode?: string;
  /** 关联 sys_tenant.short_name，列表展示优先 */
  tenantShortName?: string;
  /** 操作模块 */
  module?: string;
  /** 操作类型 */
  action?: string;
  /** 操作描述 */
  description?: string;
  /** 请求方式 */
  requestMethod?: string;
  /** 请求URL */
  requestUrl?: string;
  /** 请求参数 */
  requestBody?: string;
  /** 响应结果 */
  responseBody?: string;
  /** IP地址 */
  ip?: string;
  /** 耗时（毫秒） */
  elapsedTime?: number;
  /** 状态 0-失败 1-成功 */
  status?: number;
  /** 操作时间 */
  createdAt?: string;
}

/**
 * 租户操作日志搜索条件
 */
export interface TenantOperationLogParam extends PageParam {
  /** 租户编码 */
  tenantCode?: string;
  /** 操作用户名 */
  username?: string;
  /** 操作模块 */
  module?: string;
  /** 操作类型 */
  action?: string;
  /** 状态 */
  status?: number;
  /** 开始时间 */
  createTimeStart?: string;
  /** 截至时间 */
  createTimeEnd?: string;
}
