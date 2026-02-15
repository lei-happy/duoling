/**
 * 支付笔数数据
 */
export interface PayNumData {
  /** 日期 */
  date?: string;
  /** 支付笔数 */
  value?: number;
}

/**
 * 销售量数据
 */
export interface SaleroomData {
  /** 月份 */
  month?: string;
  /** 销售量 */
  value?: number;
}

/**
 * 销售量和访问量数据
 */
export interface SaleroomResult {
  /** 销售量 */
  list1: SaleroomData[];
  /** 访问量 */
  list2: SaleroomData[];
}

/**
 * 访问情况数据
 */
export interface VisitData {
  /** 时间 */
  time?: string;
  /** 访问量 */
  visits?: number;
  /** 浏览量 */
  views?: number;
}

/**
 * 词云数据
 */
export interface CloudData {
  /** 标题 */
  name: string;
  /** 数量 */
  value: number;
}
