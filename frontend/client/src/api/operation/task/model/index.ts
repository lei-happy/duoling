import type { PageParam } from '@/api';

/** 任务单调令（原"分段"重命名扩展） */
export interface TaskDispatchOrder {
  id?: number;
  taskId?: number;
  /** 调令序号 1..N */
  orderNo: number;
  /** 调令类型 1-重驶 2-空驶 3-年检 4-应急 5-其他 */
  dispatchType?: number;
  fromLocation?: string;
  fromCode?: string;
  fromRegionId?: number | null;
  toLocation?: string;
  toCode?: string;
  toRegionId?: number | null;
  mileage?: number | null;
  plannedLoadTime?: string;
  plannedArriveTime?: string;
  actualLoadTime?: string;
  actualArriveTime?: string;
  acceptedAt?: string;
  startedAt?: string;
  completedAt?: string;
  status?: number;
  remark?: string;
  createdAt?: string;
}

/**
 * 兼容旧引用：前端历史代码以 segmentNo 字段为主键提交分段；本期保留同名类型，
 * 仅作为 ``TaskDispatchOrder`` 的字段超集别名（同步保留 ``segmentNo`` 字段以
 * 避免大面积修改）。新代码请直接使用 ``TaskDispatchOrder``。
 */
export interface TaskSegment extends TaskDispatchOrder {
  /** @deprecated 历史字段，现为 orderNo 的别名 */
  segmentNo: number;
}

/** 装卸事件记录 */
export interface TaskLoadingRecordItem {
  id: number;
  recordId: number;
  itemId: number;
  quantity: number;
  waybillId?: number;
  waybillNo?: string;
  vehicleBrand?: string;
  vehicleModel?: string;
}

export interface TaskLoadingRecord {
  id: number;
  taskId: number;
  dispatchOrderId?: number | null;
  /** 1-装车 2-卸车 */
  eventType: number;
  happenedAt: string;
  location?: string;
  locationCode?: string;
  locationRegionId?: number | null;
  quantity: number;
  photoUrls: string[];
  operatorId?: number | null;
  operatorName?: string;
  remark?: string;
  createdAt: string;
  items: TaskLoadingRecordItem[];
}

export interface TaskLoadingRecordPayload {
  eventType: number;
  dispatchOrderId?: number | null;
  happenedAt: string;
  location?: string;
  locationCode?: string;
  locationRegionId?: number | null;
  items: Array<{ itemId: number; quantity: number }>;
  photoUrls?: string[];
  remark?: string;
}

/** 任务单货物挂接项（M:N 按台数） */
export interface TaskWaybillItem {
  id?: number;
  taskId?: number;
  waybillId: number;
  waybillCargoId: number;
  waybillNo?: string;
  customerId?: number;
  customerName?: string;
  vehicleBrand?: string;
  vehicleModel?: string;
  dealerName?: string;
  /** 车系图（挂接时带入，仅展示；提交 payload 不含此字段） */
  seriesImage?: string | null;
  quantity: number;
  /** 关联调令 ID（原 segmentId 重命名） */
  dispatchOrderId?: number | null;
  /** @deprecated 历史字段，与 dispatchOrderId 等价 */
  segmentId?: number | null;
  status?: number;
  loadedAt?: string;
  unloadedAt?: string;
  signedAt?: string;
  remark?: string;
  createdAt?: string;
}

/** 段表里程联想结果（按起终行政区匹配 biz_route） */
export interface RouteDistanceLookup {
  routeId: number;
  routeName: string;
  origin: string;
  destination: string;
  distance: number | null;
  estimatedHours: number | null;
}

/** 候选挂接行（挂接器左栏） */
export interface CandidateCargo {
  waybillId: number;
  waybillNo: string;
  customerId?: number;
  customerName?: string;
  origin?: string;
  destination?: string;
  dealerName?: string;
  requiredLoadTime?: string;
  waybillCreatedAt?: string;
  waybillStatus: number;
  cargoId: number;
  vehicleBrand?: string;
  vehicleModel?: string;
  /** 车架号 */
  vin?: string | null;
  /** 车系图（与基础数据车系匹配） */
  seriesImage?: string | null;
  quantity: number;
  allocatedQuantity: number;
  remainingQuantity: number;
}

/** 候选挂接列表（含全量统计） */
export interface CandidateCargoListResult {
  items: CandidateCargo[];
  /** 待配计划数（去重计划，对应 UI「条」） */
  waybillCount: number;
  /** cargo 明细行总数（分页用） */
  lineCount: number;
  quantityTotal: number;
  truncated: boolean;
}

/** 承运方信息（三类合一） */
export interface TaskCarrierInfo {
  carrierType: number; // 1-自有车 2-承运商 3-社会运力
  capacityId?: number | null;
  carrierId?: number | null;
  socialDriverId?: number | null;
  mainDriverName?: string;
  mainDriverPhone?: string;
  mainDriverIdCard?: string;
  plateNumber?: string;
  trailerPlateNumber?: string;
  carrierName?: string;
  carrierShortName?: string;
}

export interface Task {
  id?: number;
  taskNo?: string;
  taskName?: string;
  source?: number;
  carrierType?: number;
  capacityId?: number | null;
  carrierId?: number | null;
  socialDriverId?: number | null;
  mainDriverName?: string;
  mainDriverPhone?: string;
  mainDriverIdCard?: string;
  plateNumber?: string;
  trailerPlateNumber?: string;
  carrierName?: string;
  carrierShortName?: string;
  origin?: string;
  originCode?: string;
  originRegionId?: number | null;
  destination?: string;
  destinationCode?: string;
  destinationRegionId?: number | null;
  segmentCount?: number;
  totalQuantity?: number;
  /** 已装车台数（聚合 item.status>=1） */
  loadedQuantity?: number;
  /** 已卸车台数（聚合 item.status>=2） */
  unloadedQuantity?: number;
  waybillCount?: number;
  plannedLoadTime?: string;
  plannedArriveTime?: string;
  actualLoadTime?: string;
  actualArriveTime?: string;
  carrierCostAmount?: number | null;
  carrierCostType?: number | null;
  costRemark?: string;
  prepaidAmount?: number;
  supplementAmount?: number;
  settledAmount?: number;
  financeDocCount?: number;
  status?: number;
  dispatcherId?: number | null;
  dispatcherName?: string;
  remark?: string;
  createdAt?: string;
  updatedAt?: string;
  /** 只读：关联计划状态分布（计划状态机独立于任务，仅供展示） */
  waybillStatusSummary?: WaybillStatusSummary | null;
  /** 预留：关联财务单据状态分布（财务模块接入时填充） */
  financeStatusSummary?: WaybillStatusSummary | null;
  segments?: TaskSegment[];
  waybillItems?: TaskWaybillItem[];
}

/** 单个计划状态计数 */
export interface WaybillStatusCount {
  status: number;
  count: number;
}

/** 任务关联计划的状态分布（只读视图） */
export interface WaybillStatusSummary {
  total: number;
  items: WaybillStatusCount[];
}

export interface TaskCreatePayload {
  taskNo?: string;
  taskName?: string;
  source?: number;
  plannedLoadTime?: string;
  plannedArriveTime?: string;
  carrierCostType?: number | null;
  carrierCostAmount?: number | null;
  costRemark?: string;
  remark?: string;
  carrier?: TaskCarrierInfo;
  segments: TaskSegment[];
  waybillItems: Array<{
    waybillId: number;
    waybillCargoId: number;
    quantity: number;
    dispatchOrderId?: number | null;
    /** @deprecated 历史字段，与 dispatchOrderId 等价 */
    segmentId?: number | null;
    remark?: string;
  }>;
}

export type TaskUpdatePayload = Partial<TaskCreatePayload>;

/** 任务列表/工作台时间筛选维度 */
export type TaskTimeField =
  | 'createdAt'
  | 'assignedAt'
  | 'dispatchedAt'
  | 'actualLoadTime'
  | 'signedAt';

export interface TaskParam extends PageParam {
  keyword?: string;
  carrierType?: number;
  /** 承运商 ID（用于待派车池筛选） */
  carrierId?: number;
  /** 自有运力 ID（待装车池/在途池筛选具体车辆） */
  capacityId?: number;
  status?: number;
  customerId?: number;
  originKeyword?: string;
  destinationKeyword?: string;
  createdAtStart?: string;
  createdAtEnd?: string;
  /** 时间筛选维度（与 timeStart/timeEnd 配合；工作台优先使用） */
  timeField?: TaskTimeField;
  timeStart?: string;
  timeEnd?: string;
  /** 工作台：仅计划装车已逾期（待分配/待派车，配合 status=-1|0） */
  onlyOverdue?: boolean;
  /** 工作台：仅「正常」子集（与 onlyOverdue 互斥；待分配/待派车为计划装车未逾期） */
  onlyNormal?: boolean;
  /** 工作台：在途逾期（已装车/在途且计划到货已过，勿传 status 或与后端约定忽略） */
  inTransitOverdue?: boolean;
  /** 工作台：在途正常（status∈{2,3} 且计划到货未触发逾期） */
  inTransitOnlyNormal?: boolean;
}

export interface TaskFinanceSummaryItem {
  id: number;
  docNo: string;
  docType: number;
  isFinal: number;
  payeeType: number;
  payeeName?: string;
  plannedAmount: number;
  actualAmount?: number;
  status: number;
  createdAt: string;
  plannedPayTime?: string;
  actualPayTime?: string;
}

/** 调度工作台 KPI 聚合
 *
 * 注：原 `pendingSettle / settled / pendingSettleAlert` 字段已在后端下线
 * （财务结算与 task.status 解耦），前端类型不再保留对应字段。
 */
export interface TaskWorkbenchStats {
  statusCounts: Record<number, number>;
  totals: {
    pendingAssign: number;
    pendingDispatch: number;
    pendingLoad: number;
    loading: number;
    onWay: number;
    arrived: number;
    pendingSign: number;
    signed: number;
    closed: number;
    cancelled: number;
  };
  alerts: {
    overdueAssignment: number;
    overdueDispatch: number;
    overdueArrive: number;
    /** 待装车 / 待签收 预警数（占位，规则接入后由后端统计） */
    pendingLoadAlert?: number;
    pendingSignAlert?: number;
  };
}

/** 批量状态推进请求 */
export interface TaskBatchStatusPayload {
  ids: number[];
  status: number;
  actualLoadTime?: string;
  actualArriveTime?: string;
  remark?: string;
}

/** 批量动作结果 */
export interface BatchActionResult {
  success: number;
  failed: number;
  failures: Array<{ id: number; error: string }>;
}

/** 待分配：批量确认承运分配 */
export interface TaskBatchCarrierAssignmentPayload {
  ids: number[];
  carrier: TaskCarrierInfo;
}
