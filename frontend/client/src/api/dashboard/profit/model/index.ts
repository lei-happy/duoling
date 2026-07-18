/**
 * 利润总览（老板视角收入成本 BI）- 接口类型定义
 */

/** 时间范围查询参数 */
export interface ProfitDateRangeParam {
  /** 起始时间（ISO 字符串） */
  start?: string;
  /** 截止时间（ISO 字符串） */
  end?: string;
}

/** Sparkline 单个数据点（value 可为 null，如毛利率无收入时） */
export interface ProfitSparklinePoint {
  date: string;
  value: number | null;
}

/**
 * 单个金额型 KPI 指标（收入/成本/毛利）：
 * 当日累计 + 周同比 + 日同比 + 近 30 个自然日趋势
 */
export interface ProfitKpiMetric {
  /** 当日 0 点至今累计（元） */
  todayValue: number;
  /** 周同比增长率（小数）；null 表示对照为 0 无法计算 */
  weekOverWeekRate: number | null;
  /** 日同比增长率（小数）；null 表示对照为 0 无法计算 */
  dayOverDayRate: number | null;
  /** 近 30 个自然日趋势 */
  trend30d: ProfitSparklinePoint[];
}

/**
 * 毛利率 KPI 指标：
 * todayValue 为当日毛利率（0-1，null 表示无收入）；
 * weekOverWeekRate / dayOverDayRate 为「百分点差」（当期 - 上期）。
 */
export interface ProfitMarginMetric {
  todayValue: number | null;
  /** 周环比百分点差（当期毛利率 - 上期毛利率） */
  weekOverWeekRate: number | null;
  /** 日环比百分点差 */
  dayOverDayRate: number | null;
  trend30d: ProfitSparklinePoint[];
}

/** KPI 总览 */
export interface ProfitKpiSummary {
  /** 收入（引擎结果口径） */
  revenue: ProfitKpiMetric;
  /** 成本（分摊到计划） */
  cost: ProfitKpiMetric;
  /** 毛利 = 收入 - 成本 */
  grossProfit: ProfitKpiMetric;
  /** 毛利率 = 毛利 / 收入 */
  grossMargin: ProfitMarginMetric;
  /** 成本覆盖率 = 有成本计划收入 / 总收入（null 表示无收入） */
  costCoverageRate: number | null;
}

/** 收入/成本/毛利趋势点 */
export interface ProfitTrendPoint {
  /** 时间桶（如 '2026-05-01' 或 '2026-05'） */
  date: string;
  revenue: number;
  cost: number;
  grossProfit: number;
  /** 毛利率（小数）；null 表示该桶无收入 */
  grossMargin: number | null;
}

/** 趋势查询参数 */
export interface ProfitTrendParam extends ProfitDateRangeParam {
  granularity?: 'day' | 'week' | 'month';
}

/** 承运结构项 */
export interface CarrierStructureItem {
  /** 承运类型：1 自有车 / 2 承运商 / 3 社会运力 / -1 未知 */
  carrierType: number;
  label: string;
  revenue: number;
  cost: number;
  grossProfit: number;
  grossMargin: number | null;
  vehicleQuantity: number;
}

/** 成本构成项（按费用类型） */
export interface CostStructureItem {
  feeType: string;
  feeName: string;
  /** 分摊后的费用净额（元） */
  amount: number;
  /** 占总成本比例 */
  share: number;
}

/** 客户毛利排行项 */
export interface ProfitCustomerRankItem {
  customerId: number | null;
  customerName: string;
  revenue: number;
  cost: number;
  grossProfit: number;
  grossMargin: number | null;
  waybillCount: number;
  vehicleQuantity: number;
}

/** 客户毛利排行参数 */
export interface ProfitCustomerRankParam extends ProfitDateRangeParam {
  /** 返回条数上限，最大 5000 */
  limit?: number;
  /** 排序：profit 毛利 | revenue 收入 | margin 毛利率 */
  sort_by?: 'profit' | 'revenue' | 'margin';
}
