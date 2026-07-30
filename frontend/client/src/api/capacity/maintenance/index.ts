import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  AssetCard,
  CostDetail,
  CostSummary,
  FleetRenewal,
  FleetRenewalParam,
  MaintainPlan,
  MaintainPlanParam,
  MaintenanceBoard,
  WorkOrder,
  WorkOrderParam
} from './model';

const BASE = '/capacity/maintenance';

export async function getMaintenanceBoard() {
  const res = await request.get<ApiResult<MaintenanceBoard>>(`${BASE}/board`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function pageWorkOrders(params: WorkOrderParam) {
  const res = await request.get<ApiResult<PageResult<WorkOrder>>>(
    `${BASE}/work-orders`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function createWorkOrder(data: WorkOrder) {
  const res = await request.post<ApiResult<WorkOrder>>(
    `${BASE}/work-orders`,
    data
  );
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateWorkOrder(id: number, data: WorkOrder) {
  const res = await request.put<ApiResult<WorkOrder>>(
    `${BASE}/work-orders/${id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function startWorkOrder(id: number) {
  const res = await request.post<ApiResult<WorkOrder>>(
    `${BASE}/work-orders/${id}/start`
  );
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function completeWorkOrder(
  id: number,
  data?: Pick<WorkOrder, 'costAmount' | 'costRemark' | 'odometer' | 'remark'>
) {
  const res = await request.post<ApiResult<WorkOrder>>(
    `${BASE}/work-orders/${id}/complete`,
    data || {}
  );
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function cancelWorkOrder(id: number) {
  const res = await request.post<ApiResult<WorkOrder>>(
    `${BASE}/work-orders/${id}/cancel`
  );
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function pageMaintainPlans(params: MaintainPlanParam) {
  const res = await request.get<ApiResult<PageResult<MaintainPlan>>>(
    `${BASE}/plans`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function createMaintainPlan(data: MaintainPlan) {
  const res = await request.post<ApiResult<MaintainPlan>>(
    `${BASE}/plans`,
    data
  );
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateMaintainPlan(id: number, data: MaintainPlan) {
  const res = await request.put<ApiResult<MaintainPlan>>(
    `${BASE}/plans/${id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function deleteMaintainPlan(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/plans/${id}`);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function generateWorkOrderFromPlan(planId: number) {
  const res = await request.post<ApiResult<WorkOrder>>(
    `${BASE}/plans/${planId}/generate-work-order`
  );
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function pageRenewals(params: FleetRenewalParam) {
  const res = await request.get<ApiResult<PageResult<FleetRenewal>>>(
    `${BASE}/renewals`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function createRenewal(data: FleetRenewal) {
  const res = await request.post<ApiResult<FleetRenewal>>(
    `${BASE}/renewals`,
    data
  );
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function effectRenewal(id: number) {
  const res = await request.post<ApiResult<FleetRenewal>>(
    `${BASE}/renewals/${id}/effect`
  );
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function cancelRenewal(id: number) {
  const res = await request.post<ApiResult<FleetRenewal>>(
    `${BASE}/renewals/${id}/cancel`
  );
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getAssetCard(vehicleId: number) {
  const res = await request.get<ApiResult<AssetCard>>(
    `${BASE}/vehicles/${vehicleId}/asset-card`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateAssetCard(vehicleId: number, data: AssetCard) {
  const res = await request.put<ApiResult<AssetCard>>(
    `${BASE}/vehicles/${vehicleId}/asset-card`,
    data
  );
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getCostSummary(params: {
  dateFrom: string;
  dateTo: string;
  vehicleId?: number;
}) {
  const res = await request.get<ApiResult<CostSummary>>(
    `${BASE}/cost/summary`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getCostDetails(params: {
  dateFrom: string;
  dateTo: string;
  vehicleId?: number;
  costType?: string;
}) {
  const res = await request.get<
    ApiResult<{ list: CostDetail[]; total: number; disclaimer: string }>
  >(`${BASE}/cost/details`, { params });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
