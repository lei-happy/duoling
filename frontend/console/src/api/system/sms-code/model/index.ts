import { PageParam } from '@/api';

/** 短信验证码记录 */
export interface SmsCode {
  id: number;
  phone: string;
  code: string;
  /** 用途 1-验证码登录 2-重置密码 */
  purpose: number;
  /** 状态 0-未使用 1-已使用 2-已过期 */
  status: number;
  expireAt: string;
  clientIp?: string;
  createdAt: string;
}

export interface SmsCodeParam extends PageParam {
  phone?: string;
  purpose?: number;
  status?: number;
  createTimeStart?: string;
  createTimeEnd?: string;
}
