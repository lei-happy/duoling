import { PageParam } from '@/api';

/**
 * 操作日志
 */
export interface OperationRecord {
  /** 操作日志id */
  id?: number;
  /** 用户id */
  userId?: number;
  /** 操作用户名（一般为登录手机号） */
  username?: string;
  /** 关联 biz_user 的真实姓名，展示时优先于 username */
  realName?: string;
  /** 操作模块 */
  module?: string;
  /** 操作类型 */
  action?: string;
  /** 操作描述 */
  description?: string;
  /** 请求方式 */
  requestMethod?: string;
  /** 请求地址 */
  requestUrl?: string;
  /** 请求参数 */
  requestBody?: string;
  /** 响应结果 */
  responseBody?: string;
  /** ip地址 */
  ip?: string;
  /** 消耗时间, 单位毫秒 */
  elapsedTime?: number;
  /** 状态, 1成功, 0失败 */
  status?: number;
  /** 操作时间 */
  createdAt?: string;
}

/**
 * 操作日志搜索条件
 */
export interface OperationRecordParam extends PageParam {
  /** 操作用户名 */
  username?: string;
  /** 操作模块 */
  module?: string;
  /** 开始时间 */
  createTimeStart?: string;
  /** 截至时间 */
  createTimeEnd?: string;
  /** 状态 */
  status?: number;
}
