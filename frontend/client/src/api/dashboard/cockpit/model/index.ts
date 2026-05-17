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

/** 单个 KPI 指标：当日累计 + 周同比 + 日同比 + 近 30 个自然日趋势 */
export interface KpiMetric {
  /** 当日 0 点至今累计（自然日，与服务器日历一致） */
  todayValue: number;
  /**
   * 周同比（本周一 0 点至今 vs 上周一 0 点起相同时长）：
   *  - null 表示对照为 0、无法计算
   */
  weekOverWeekRate: number | null;
  /**
   * 日同比（今天 0 点至今 vs 昨天 0 点至昨天与当前同一时刻）：
   *  - null 表示对照为 0、无法计算
   */
  dayOverDayRate: number | null;
  /** 近 30 个自然日（含当日）按日序列；运费为「元」 */
  trend30d: SparklinePoint[];
}

/** KPI 总览 */
export interface KpiSummary {
  /** 运单应收运费合计（结算口径，非扣成本后的收入） */
  revenue: KpiMetric;
  /** 总运单数 */
  waybillCount: KpiMetric;
  /** 总发运台数 */
  vehicleQuantity: KpiMetric;
  /** 服务客户数 */
  customerCount: KpiMetric;
}

/** 运费与单量趋势点 */
export interface RevenueTrendPoint {
  /** 时间桶（如 '2026-05-01' 或 '2026-05'） */
  date: string;
  /** 运单应收运费（元，结算口径） */
  revenue: number;
  /** 运单数 */
  waybillCount: number;
  /** 发运台数 */
  vehicleQuantity: number;
}

/** 运费趋势查询参数 */
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
  /** 该客户运费占本期总运费的比例 */
  share: number;
}

/** TopN 客户查询参数 */
export interface CustomerRankParam extends CockpitDateRangeParam {
  /** 返回条数上限，最大 5000（服务端约束） */
  limit?: number;
  /** 排序：revenue 按运单运费；vehicle_quantity 按商品车台数 */
  sort_by?: 'revenue' | 'vehicle_quantity';
  /**
   * 按客户类型筛选（与类型分布一致，NULL 为 -1 未知）；不传表示全部
   */
  customer_type?: number;
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
  /** 按运单 calc_status 的分布（待计算/已计算/计算异常等） */
  calcStatusDist: Array<{
    calcStatus: string;
    label: string;
    count: number;
  }>;
  /** 计算异常率（小数，= 计算异常单数 / 本期总单数，与 calcStatusDist 一致） */
  calcExceptionRate: number;
  /** 计算异常单数（calc_status === exception） */
  calcExceptionCount: number;
  /** 锁定运单数 */
  lockedCount: number;
  /** 本期总单数 */
  totalCount: number;
}
