import type { PageParam } from '@/api';

/** 任务单运输分段 */
export interface TaskSegment {
  id?: number;
  taskId?: number;
  segmentNo: number;
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
  status?: number;
  remark?: string;
  createdAt?: string;
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
  quantity: number;
  segmentId?: number | null;
  status?: number;
  loadedAt?: string;
  unloadedAt?: string;
  signedAt?: string;
  remark?: string;
  createdAt?: string;
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
  waybillStatus: number;
  cargoId: number;
  vehicleBrand?: string;
  vehicleModel?: string;
  quantity: number;
  allocatedQuantity: number;
  remainingQuantity: number;
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
  segments?: TaskSegment[];
  waybillItems?: TaskWaybillItem[];
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
    segmentId?: number | null;
    remark?: string;
  }>;
}

export type TaskUpdatePayload = Partial<TaskCreatePayload>;

export interface TaskParam extends PageParam {
  keyword?: string;
  carrierType?: number;
  status?: number;
  customerId?: number;
  originKeyword?: string;
  destinationKeyword?: string;
  createdAtStart?: string;
  createdAtEnd?: string;
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
