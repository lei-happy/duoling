/**
 * 经营驾驶舱 BI 看板 - 接口类型定义
 */

/** 时间范围查询参数 */
export interface CockpitDateRangeParam {
  /** 起始时间（ISO 字符串） */
  start?: string;
  /** 截止时间（ISO 字符串） */
  end?: string;
}

/** Sparkline 单个数据点 */
export interface SparklinePoint {
  date: string;
  value: number;
}

/** 单个 KPI 指标的本期值 + 环比 + sparkline */
export interface KpiMetric {
  /** 本期值 */
  value: number;
  /** 对照期值 */
  previous: number;
  /**
   * 环比增长率：
   *  - null 表示对照期为 0、无法计算
   *  - 否则为小数（如 0.123 → +12.3%）
   */
  growthRate: number | null;
  /** 迷你趋势点序列（按日） */
  sparkline: SparklinePoint[];
}

/** KPI 总览 */
export interface KpiSummary {
  /** 运费总收入 */
  revenue: KpiMetric;
  /** 总运单数 */
  waybillCount: KpiMetric;
  /** 总发运台数 */
  vehicleQuantity: KpiMetric;
  /** 服务客户数 */
  customerCount: KpiMetric;
}

/** 收入与单量趋势点 */
export interface RevenueTrendPoint {
  /** 时间桶（如 '2026-05-01' 或 '2026-05'） */
  date: string;
  /** 运费收入 */
  revenue: number;
  /** 运单数 */
  waybillCount: number;
  /** 发运台数 */
  vehicleQuantity: number;
}

/** 收入趋势查询参数 */
export interface RevenueTrendParam extends CockpitDateRangeParam {
  /** 聚合粒度：day | week | month */
  granularity?: 'day' | 'week' | 'month';
}

/** 客户排行项 */
export interface CustomerRankItem {
  customerId: number | null;
  customerName: string;
  revenue: number;
  waybillCount: number;
  vehicleQuantity: number;
  /** 该客户运费占本期总收入的比例 */
  share: number;
}

/** TopN 客户查询参数 */
export interface CustomerRankParam extends CockpitDateRangeParam {
  limit?: number;
}

/** 客户类型分布项 */
export interface CustomerTypeDistItem {
  /**
   * 客户类型代码：
   *  - 0 主机厂
   *  - 1 贸易商
   *  - 2 经销商
   *  - 3 个人
   *  - 4 其他
   *  - -1 未知（NULL）
   */
  customerType: number;
  /** 中文标签 */
  label: string;
  revenue: number;
  waybillCount: number;
  vehicleQuantity: number;
}

/** 起讫地排行项 */
export interface RegionRankItem {
  regionName: string;
  regionCode: string | null;
  regionLevel: number | null;
  revenue: number;
  waybillCount: number;
  vehicleQuantity: number;
}

/** 区域排行查询参数 */
export interface RegionRankParam extends CockpitDateRangeParam {
  /** origin: 出发地; destination: 目的地 */
  type?: 'origin' | 'destination';
  limit?: number;
}

/** 品牌排行项 */
export interface VehicleBrandRankItem {
  brandId: number | null;
  brandName: string;
  vehicleQuantity: number;
  waybillCount: number;
  /** 该品牌台数占 TopN 总和的比例 */
  share: number;
}

/** 品牌排行参数 */
export interface VehicleBrandRankParam extends CockpitDateRangeParam {
  limit?: number;
}

/** 运营效率响应 */
export interface OperationEfficiency {
  /** 运单状态分布 */
  statusDist: Array<{
    status: number;
    label: string;
    count: number;
  }>;
  /** 计算异常率（小数） */
  calcExceptionRate: number;
  /** 计算异常单数 */
  calcExceptionCount: number;
  /** 锁定运单数 */
  lockedCount: number;
  /** 本期总单数 */
  totalCount: number;
}
