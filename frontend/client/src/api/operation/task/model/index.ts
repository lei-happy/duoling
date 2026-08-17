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

/** 任务状态事件（时间流节点） */
export interface TaskStatusEvent {
  id: number;
  /** 1-创建 2-分配承运 3-派车 4-装车 5-出发 6-到达 7-交车 8-关闭 9-取消 11~16 逆向 */
  eventType: number;
  eventTypeLabel: string;
  fromStatus?: number | null;
  toStatus?: number | null;
  toStatusLabel?: string | null;
  /** 1-企业端 2-驾驶员端 3-承运商端 4-系统聚合 5-历史回填 */
  source: number;
  sourceLabel: string;
  operatorId?: number | null;
  operatorName?: string | null;
  reason?: string | null;
  payload?: Record<string, any> | null;
  eventTime: string;
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
  /** 规划后的地点链：起点 → 中转… → 终点 */
  routeNodes?: string[];
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
  /** 分配承运方时间 */
  assignedAt?: string;
  /** 派车时间 */
  dispatchedAt?: string;
  /** 进入当前状态的时间（用于「本阶段停留」列与滞留预警） */
  stageEnteredAt?: string;
  dispatcherId?: number | null;
  dispatcherName?: string;
  remark?: string;
  createdAt?: string;
  updatedAt?: string;
  /** 只读：关联计划状态分布（计划状态机独立于任务，仅供展示） */
  waybillStatusSummary?: WaybillStatusSummary | null;
  /** 预留：关联财务单据状态分布（财务模块接入时填充） */
  financeStatusSummary?: WaybillStatusSummary | null;
  /**
   * 活跃预警最高级别 0-无 1-关注 2-严重。
   * 由后端 biz_task_alert 聚合，前端不再自行判定逾期。
   */
  alertLevel?: TaskAlertLevel;
  /** 命中的预警规则码 */
  alertCodes?: string[];
  /** 最严重一条预警的超时分钟数 */
  alertOverdueMinutes?: number;
  segments?: TaskSegment[];
  waybillItems?: TaskWaybillItem[];
}

/** 预警级别：0-无 1-关注 2-严重 */
export type TaskAlertLevel = 0 | 1 | 2;

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

/**
 * 任务列表/工作台时间筛选维度。
 *
 * `stageEnteredAt` / `createdAt` 对每条任务都有值（稳定维度）；
 * 其余为节点维度，筛选时会排除尚未走到该节点的任务。
 */
export type TaskTimeField =
  | 'stageEnteredAt'
  | 'createdAt'
  | 'assignedAt'
  | 'dispatchedAt'
  | 'actualLoadTime'
  | 'signedAt';

/** 列表预警子集过滤取值 */
export type TaskAlertLevelFilter = 'normal' | 'warn' | 'critical' | 'any';

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
  /**
   * 预警子集过滤：normal(无活跃预警) / warn(仅关注) / critical(存在严重) / any(任意预警)。
   * 取代已废弃的 onlyOverdue / onlyNormal —— 判定口径统一在后端。
   */
  alertLevel?: TaskAlertLevelFilter;
  /** 车牌号精确筛选（主车牌，前后模糊匹配） */
  plateNumber?: string;
  /** 服务端排序字段（白名单外的取值后端会忽略） */
  sortField?: string;
  /** 排序方向 */
  sortOrder?: 'asc' | 'desc';
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
  /**
   * 按阶段的两级预警计数，key 为任务 status 的字符串形式（'-1' ~ '4'）。
   * warn 与 critical 互斥（同一任务按最高级别归类），
   * 因此「常」= totals - warn - critical。
   */
  stageAlerts?: Record<string, { warn: number; critical: number }>;
  /** @deprecated 旧的单级预警计数，等于 warn + critical，仅供灰度期兼容 */
  alerts: {
    overdueAssignment: number;
    overdueDispatch: number;
    overdueDepart?: number;
    overdueArrive: number;
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
