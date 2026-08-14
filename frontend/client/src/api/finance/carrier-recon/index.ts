import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  ReconDiffRaisePayload,
  ReconDiffResolvePayload
} from '@/api/finance/customer-recon/model';
import type {
  CarrierReconCandidate,
  CarrierReconCheckReport,
  CarrierReconCreatePayload,
  CarrierReconDetail,
  CarrierReconLine,
  CarrierReconLineAdjustPayload,
  CarrierReconListItem,
  CarrierReconParam,
  CarrierReconUpdatePayload,
  CarrierSignPayload,
  FinanceDocEvent,
  ReconDiff
} from './model';

const BASE = '/finance/carrier-recon';

export async function listCarrierReconCandidates(params: {
  carrierId: number;
  periodStart?: string;
  periodEnd?: string;
  keyword?: string;
  reconId?: number;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: CarrierReconCandidate[]; count: number }>
  >(`${BASE}/candidates`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listCarrierReconOrphans(params: {
  carrierId: number;
  periodStart?: string;
  periodEnd?: string;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{
      list: { taskId: number; taskNo?: string; carrierCostAmount?: number }[];
      count: number;
    }>
  >(`${BASE}/orphans`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function pageCarrierRecons(params: CarrierReconParam) {
  const res = await request.get<ApiResult<PageResult<CarrierReconListItem>>>(
    BASE,
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getCarrierRecon(reconId: number) {
  const res = await request.get<ApiResult<CarrierReconDetail>>(
    `${BASE}/${reconId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function addCarrierRecon(data: CarrierReconCreatePayload) {
  const res = await request.post<ApiResult<CarrierReconDetail>>(BASE, data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateCarrierRecon(
  reconId: number,
  data: CarrierReconUpdatePayload
) {
  const res = await request.put<ApiResult<CarrierReconDetail>>(
    `${BASE}/${reconId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeCarrierRecon(reconId: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${reconId}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function listCarrierReconLines(reconId: number) {
  const res = await request.get<ApiResult<CarrierReconLine[]>>(
    `${BASE}/${reconId}/lines`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function addCarrierReconLines(
  reconId: number,
  taskIds: number[],
  billingBase?: number
) {
  const res = await request.post<ApiResult<CarrierReconDetail>>(
    `${BASE}/${reconId}/lines`,
    { taskIds, billingBase }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function adjustCarrierReconLine(
  reconId: number,
  linkId: number,
  data: CarrierReconLineAdjustPayload
) {
  const res = await request.put<ApiResult<CarrierReconDetail>>(
    `${BASE}/${reconId}/lines/${linkId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeCarrierReconLine(reconId: number, linkId: number) {
  const res = await request.delete<ApiResult<CarrierReconDetail>>(
    `${BASE}/${reconId}/lines/${linkId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function checkCarrierRecon(reconId: number, persist = true) {
  const res = await request.post<ApiResult<CarrierReconCheckReport>>(
    `${BASE}/${reconId}/check`,
    void 0,
    { params: { persist } }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listCarrierReconDiffs(reconId: number, onlyOpen = false) {
  const res = await request.get<ApiResult<ReconDiff[]>>(
    `${BASE}/${reconId}/diffs`,
    { params: { onlyOpen } }
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function raiseCarrierReconDiff(
  reconId: number,
  data: ReconDiffRaisePayload
) {
  const res = await request.post<ApiResult<ReconDiff>>(
    `${BASE}/${reconId}/diffs`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function resolveCarrierReconDiff(
  diffId: number,
  data: ReconDiffResolvePayload
) {
  const res = await request.post<ApiResult<ReconDiff>>(
    `${BASE}/diffs/${diffId}/resolve`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function recalcCarrierRecon(reconId: number, onlyDirty = true) {
  const res = await request.post<ApiResult<CarrierReconDetail>>(
    `${BASE}/${reconId}/recalc`,
    { onlyDirty }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function approveCarrierReconAdjust(reconId: number) {
  const res = await request.post<ApiResult<CarrierReconDetail>>(
    `${BASE}/${reconId}/approve-adjust`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function confirmCarrierRecon(
  reconId: number,
  forceReason?: string
) {
  const res = await request.post<ApiResult<CarrierReconDetail>>(
    `${BASE}/${reconId}/confirm`,
    forceReason ? { forceReason } : {}
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function signCarrierRecon(
  reconId: number,
  data: CarrierSignPayload
) {
  const res = await request.post<ApiResult<CarrierReconDetail>>(
    `${BASE}/${reconId}/carrier-sign`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function withdrawCarrierRecon(reconId: number, reason: string) {
  const res = await request.post<ApiResult<CarrierReconDetail>>(
    `${BASE}/${reconId}/withdraw`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelCarrierRecon(reconId: number, reason: string) {
  const res = await request.post<ApiResult<CarrierReconDetail>>(
    `${BASE}/${reconId}/cancel`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function unlockSettledCarrierRecon(
  reconId: number,
  reason: string
) {
  const res = await request.post<ApiResult<CarrierReconDetail>>(
    `${BASE}/${reconId}/unlock-settled`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listCarrierReconEvents(reconId: number) {
  const res = await request.get<ApiResult<FinanceDocEvent[]>>(
    `${BASE}/${reconId}/events`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}
