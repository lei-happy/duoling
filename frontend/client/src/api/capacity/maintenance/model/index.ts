/** 维保工单 */
export interface WorkOrder {
  id?: number;
  workOrderNo?: string;
  vehicleId?: number;
  plateNumber?: string;
  orderType?: string;
  planId?: number | null;
  title?: string;
  description?: string;
  odometer?: number | null;
  workshop?: string;
  expectFinishDate?: string | null;
  costAmount?: number | null;
  costRemark?: string;
  status?: string;
  startedAt?: string | null;
  finishedAt?: string | null;
  capacityId?: number | null;
  remark?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface WorkOrderParam extends WorkOrder {
  page?: number;
  limit?: number;
  keyword?: string;
}

/** 保养计划 */
export interface MaintainPlan {
  id?: number;
  vehicleId?: number;
  plateNumber?: string;
  name?: string;
  cycleType?: string;
  intervalDays?: number | null;
  intervalMileage?: number | null;
  lastMaintainDate?: string | null;
  lastMaintainMileage?: number | null;
  nextMaintainDate?: string | null;
  nextMaintainMileage?: number | null;
  remindDays?: number;
  enabled?: number;
  dueLevel?: string | null;
  createdAt?: string;
  updatedAt?: string;
}

export interface MaintainPlanParam extends MaintainPlan {
  page?: number;
  limit?: number;
  keyword?: string;
}

export interface MaintenanceBoard {
  duePlans: MaintainPlan[];
  inProgressOrders: WorkOrder[];
  weekSummary: {
    completedCount: number;
    costAmount: number;
  };
}

/** 续期台账 */
export interface FleetRenewal {
  id?: number;
  vehicleId?: number;
  plateNumber?: string;
  renewalType?: string;
  effectiveDate?: string;
  expireDate?: string;
  amount?: number | null;
  policyNo?: string;
  attachmentUrl?: string;
  status?: string;
  effectiveAt?: string | null;
  remark?: string;
  effectNow?: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export interface FleetRenewalParam extends FleetRenewal {
  page?: number;
  limit?: number;
  keyword?: string;
}

/** 资产卡片 */
export interface AssetCard {
  vehicleId?: number;
  plateNumber?: string;
  purchaseDate?: string | null;
  originalValue?: number | null;
  residualValue?: number | null;
  depreciableMonths?: number | null;
  depreciationMethod?: string | null;
  depreciationStartDate?: string | null;
  insuranceExpire?: string | null;
  inspectionExpire?: string | null;
  monthlyDepreciation?: number | null;
  accumulatedDepreciation?: number | null;
  netValue?: number | null;
}

export interface CostSummary {
  dateFrom: string;
  dateTo: string;
  totals: {
    maintenance: number;
    insurance: number;
    inspection: number;
    depreciation: number;
    total: number;
  };
  vehicles: Array<{
    vehicleId: number;
    plateNumber: string;
    maintenance: number;
    insurance: number;
    inspection: number;
    depreciation: number;
    total: number;
  }>;
  disclaimer: string;
}

export interface CostDetail {
  costType: string;
  vehicleId: number;
  plateNumber: string;
  occurDate?: string | null;
  amount: number;
  refType: string;
  refId: number;
  title?: string;
  refNo?: string | null;
}
