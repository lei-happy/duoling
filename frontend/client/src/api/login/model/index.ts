import type { User } from '../../system/user/model';

/**
 * 登录参数
 */
export interface LoginParam {
  /** 手机号 */
  phone?: string;
  /** 密码 */
  password?: string;
  /** 租户编码（多企业选择时第二步传入） */
  tenant_code?: string;
  /** 是否记住密码 */
  remember?: boolean;
}

/**
 * 登录用户信息
 */
export interface LoginUserInfo {
  user_id?: number;
  phone?: string;
  real_name?: string;
  avatar?: string;
  user_type?: number;
  tenant_code?: string;
  roles?: string[];
  force_change_pwd?: number;
}

/**
 * 登录返回结果
 */
export interface LoginResult {
  /** token */
  access_token?: string;
  /** refresh token */
  refresh_token?: string;
  /** token类型 */
  token_type?: string;
  /** 过期时间（秒） */
  expires_in?: number;
  /** 用户信息 */
  user?: LoginUserInfo;
  /** 是否需要选择企业 */
  needSelectTenant?: boolean;
  /** 可选企业列表 */
  tenants?: TenantOption[];
}

/**
 * 企业选择项
 */
export interface TenantOption {
  /** 企业编码 */
  tenantCode: string;
  /** 企业名称 */
  tenantName: string;
}

/**
 * 图形验证码返回结果
 */
export interface CaptchaResult {
  /** 图形验证码base64数据 */
  base64: string;
  /** 验证码文本 */
  text: string;
}
