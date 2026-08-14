import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  FinanceDocEvent,
  ReconCandidate,
  ReconCheckReport,
  ReconCreatePayload,
  ReconDetail,
  ReconDiff,
  ReconDiffRaisePayload,
  ReconDiffResolvePayload,
  ReconLine,
  ReconLineAdjustPayload,
  ReconListItem,
  ReconParam,
  ReconUpdatePayload,
  ReconCustomerSignPayload
} from './model';

const BASE = '/finance/customer-recon';

export async function listReconCandidates(params: {
  customerId: number;
  periodStart?: string;
  periodEnd?: string;
  keyword?: string;
  reconId?: number;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: ReconCandidate[]; count: number }>
  >(`${BASE}/candidates`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function pageRecons(params: ReconParam) {
  const res = await request.get<ApiResult<PageResult<ReconListItem>>>(BASE, {
    params
  });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getRecon(reconId: number) {
  const res = await request.get<ApiResult<ReconDetail>>(`${BASE}/${reconId}`);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function addRecon(data: ReconCreatePayload) {
  const res = await request.post<ApiResult<ReconDetail>>(BASE, data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateRecon(reconId: number, data: ReconUpdatePayload) {
  const res = await request.put<ApiResult<ReconDetail>>(
    `${BASE}/${reconId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeRecon(reconId: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${reconId}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function listReconLines(reconId: number) {
  const res = await request.get<ApiResult<ReconLine[]>>(
    `${BASE}/${reconId}/lines`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function addReconLines(
  reconId: number,
  waybillIds: number[],
  billingBase?: number
) {
  const res = await request.post<ApiResult<ReconDetail>>(
    `${BASE}/${reconId}/lines`,
    { waybillIds, billingBase }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function adjustReconLine(
  reconId: number,
  linkId: number,
  data: ReconLineAdjustPayload
) {
  const res = await request.put<ApiResult<ReconDetail>>(
    `${BASE}/${reconId}/lines/${linkId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeReconLine(reconId: number, linkId: number) {
  const res = await request.delete<ApiResult<ReconDetail>>(
    `${BASE}/${reconId}/lines/${linkId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function checkRecon(reconId: number, persist = true) {
  const res = await request.post<ApiResult<ReconCheckReport>>(
    `${BASE}/${reconId}/check`,
    void 0,
    { params: { persist } }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listReconDiffs(reconId: number, onlyOpen = false) {
  const res = await request.get<ApiResult<ReconDiff[]>>(
    `${BASE}/${reconId}/diffs`,
    { params: { onlyOpen } }
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function raiseReconDiff(
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

export async function resolveReconDiff(
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

export async function recalcRecon(reconId: number, onlyDirty = true) {
  const res = await request.post<ApiResult<ReconDetail>>(
    `${BASE}/${reconId}/recalc`,
    { onlyDirty }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function approveReconAdjust(reconId: number) {
  const res = await request.post<ApiResult<ReconDetail>>(
    `${BASE}/${reconId}/approve-adjust`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function confirmRecon(reconId: number, forceReason?: string) {
  const res = await request.post<ApiResult<ReconDetail>>(
    `${BASE}/${reconId}/confirm`,
    forceReason ? { forceReason } : {}
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function signRecon(
  reconId: number,
  data: ReconCustomerSignPayload
) {
  const res = await request.post<ApiResult<ReconDetail>>(
    `${BASE}/${reconId}/customer-sign`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function withdrawRecon(reconId: number, reason: string) {
  const res = await request.post<ApiResult<ReconDetail>>(
    `${BASE}/${reconId}/withdraw`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelRecon(reconId: number, reason: string) {
  const res = await request.post<ApiResult<ReconDetail>>(
    `${BASE}/${reconId}/cancel`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function unlockSettledRecon(reconId: number, reason: string) {
  const res = await request.post<ApiResult<ReconDetail>>(
    `${BASE}/${reconId}/unlock-settled`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listReconEvents(reconId: number) {
  const res = await request.get<ApiResult<FinanceDocEvent[]>>(
    `${BASE}/${reconId}/events`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}
