import type { PageParam } from '@/api';

/** 计划货物明细（一单多车型） */
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
  /** 回单确认时间（交车回单返还货主；status=6 已回单时有值） */
  receiptAt?: string | null;
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
  /** 已分配到任务单的总台数（计划聚合视图） */
  allocatedQuantity?: number | null;
}

/** 计划在某任务下的挂接明细行 */
export interface WaybillLinkedTaskItem {
  id: number;
  quantity: number;
  vehicleBrand?: string | null;
  vehicleModel?: string | null;
  itemStatus: number;
}

/** 计划关联的单个任务（按任务聚合） */
export interface WaybillLinkedTask {
  taskId: number;
  taskNo: string;
  taskStatus: number;
  mainDriverName?: string | null;
  mainDriverPhone?: string | null;
  plateNumber?: string | null;
  allocatedQuantity: number;
  items: WaybillLinkedTaskItem[];
}

/** 计划关联任务列表 */
export interface WaybillLinkedTasks {
  waybillId: number;
  waybillNo: string;
  tasks: WaybillLinkedTask[];
}

/** 计划工作台 KPI：与后端 WaybillService.workbench_stats 输出对齐 */
export interface WaybillWorkbenchStats {
  statusCounts: Record<number, number>;
  totals: {
    pendingConfirm: number;
    pendingDispatch: number;
    scheduling: number;
    inTransit: number;
    delivered: number;
    completed: number;
    receipted: number;
    closed: number;
  };
}

/** 计划回单凭证（交车回单返还货主） */
export interface WaybillReceipt {
  id: number;
  waybillId: number;
  fileUrls: string[];
  /** 1-图片 2-PDF */
  fileType: number;
  receivedAt: string;
  uploadedBy?: number | null;
  operatorName?: string | null;
  remark?: string | null;
  createdAt: string;
}

/** 确认回单入参（计划 5 已交车 → 6 已回单） */
export interface WaybillReceiptConfirmPayload {
  fileUrls: string[];
  fileType?: number;
  receivedAt?: string;
  remark?: string;
}

export interface WaybillParam extends PageParam {
  /** 关键词：仅模糊匹配计划号（客户请用 customerId） */
  keyword?: string;
  customerId?: number;
  status?: number;
  /** 出发地模糊 */
  originKeyword?: string;
  /** 目的地模糊 */
  destinationKeyword?: string;
  /** 品牌或车型模糊 */
  vehicleKeyword?: string;
  /** VIN / 车架号模糊（匹配货物明细） */
  vinKeyword?: string;
  /** 创建日期起 YYYY-MM-DD（含当日 0 点） */
  createdAtStart?: string;
  /** 创建日期止 YYYY-MM-DD（含当日结束） */
  createdAtEnd?: string;
}
