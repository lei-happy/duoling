import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { ReconDiff } from '@/api/finance/customer-recon/model';

const BASE = '/finance/recon-workbench';

/** KPI 卡与 Tab 角标，一次取全 */
export interface ReconWorkbenchSummary {
  pendingWaybillCount: number;
  pendingWaybillAmount: number;
  pendingCustomerCount: number;
  dirtyReconCount: number;
  openDiffCount: number;
  openDiffAmount: number;
  blockingDiffCount: number;
  pendingSignCount: number;
  pendingSignAmount: number;
  confirmedThisMonthCount: number;
  confirmedThisMonthAmount: number;
  monthStart: string;
}

/** 候选池：待对账运单按客户归堆 */
export interface PendingWaybillGroup {
  customerId: number;
  customerName?: string;
  waybillCount: number;
  freightAmount: number;
  enterpriseId?: number;
}

export async function getReconWorkbenchSummary(enterpriseId?: number) {
  const res = await request.get<ApiResult<ReconWorkbenchSummary>>(
    `${BASE}/summary`,
    { params: { enterpriseId } }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listPendingWaybillGroups(params: {
  keyword?: string;
  enterpriseId?: number;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: PendingWaybillGroup[]; count: number }>
  >(`${BASE}/pending-waybills`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listWorkbenchDiffs(params: {
  onlyBlocking?: boolean;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: ReconDiff[]; count: number }>
  >(`${BASE}/diffs`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}
