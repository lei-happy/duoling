/**
 * 用户分布数据
 */
export interface UserCount {
  /** 省份 */
  name: string;
  /** 用户数量 */
  value: number;
  /** 百分比 */
  percent?: number;
}

/**
 * 浏览器分布数据
 */
export interface BrowserCount {
  /** 浏览器 */
  name: string;
  /** 用户数量 */
  value: number;
}
