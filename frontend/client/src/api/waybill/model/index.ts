import type { PageParam } from '@/api';

/** 运单货物明细（一单多车型） */
export interface WaybillCargoLine {
  id?: number;
  vehicleBrand?: string;
  vehicleModel?: string;
  /** 车架号 VIN（创建/新增行必填；与后端一致为去空格后大写字母数字） */
  vin?: string | null;
  quantity?: number;
  sortOrder?: number;
  /** 车系图路径/URL（列表/详情由后端匹配 biz_vehicle_series） */
  seriesImage?: string | null;
}

export interface Waybill {
  id?: number;
  waybillNo?: string;
  customerId?: number;
  customerName?: string;
  origin?: string;
  originCode?: string;
  destination?: string;
  destinationCode?: string;
  vehicleBrand?: string;
  vehicleModel?: string;
  quantity?: number;
  cargoes?: WaybillCargoLine[];
  cargoSummary?: string;
  /** 首条货物或主档对应的车系图 */
  primarySeriesImage?: string | null;
  planIssueTime?: string;
  requiredLoadTime?: string;
  requiredDeliverTime?: string;
  dealerName?: string;
  dealerContact?: string;
  dealerPhone?: string;
  dealerAddress?: string;
  freightAmount?: number;
  freightSource?: number;
  contractId?: number;
  rateId?: number;
  status?: number;
  remark?: string;
  createdBy?: number;
  createdAt?: string;
  originRegionId?: number | null;
  destinationRegionId?: number | null;
  calcStatus?: string;
  isLocked?: number;
  waybillVersion?: number;
  lastCalcAt?: string | null;
  lastResultId?: number | null;
  /** 是否存在未取消/未完结的任务挂接（用于禁用编辑/删除按钮） */
  hasActiveTaskItems?: boolean | null;
  /** 已分配到任务单的总台数（运单聚合视图） */
  allocatedQuantity?: number | null;
}

/** 运单工作台 KPI：与后端 WaybillService.workbench_stats 输出对齐 */
export interface WaybillWorkbenchStats {
  statusCounts: Record<number, number>;
  totals: {
    pendingConfirm: number;
    pendingDispatch: number;
    scheduling: number;
    inTransit: number;
    delivered: number;
    completed: number;
    closed: number;
  };
}

export interface WaybillParam extends PageParam {
  /** 关键词：仅模糊匹配运单号（客户请用 customerId） */
  keyword?: string;
  customerId?: number;
  status?: number;
  /** 出发地模糊 */
  originKeyword?: string;
  /** 目的地模糊 */
  destinationKeyword?: string;
  /** 品牌或车型模糊 */
  vehicleKeyword?: string;
  /** 创建日期起 YYYY-MM-DD（含当日 0 点） */
  createdAtStart?: string;
  /** 创建日期止 YYYY-MM-DD（含当日结束） */
  createdAtEnd?: string;
}
