import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  BatchExecItem,
  CashierOverview,
  FinanceDocEvent,
  FundFlowParam,
  FundFlowRow,
  FundFlowSummary,
  PayableCandidate,
  PayableDocRef,
  PayCalendarDay,
  PaymentBatchCreatePayload,
  PaymentBatchDetail,
  PaymentBatchItem,
  PaymentBatchListItem,
  PaymentBatchParam,
  PaymentBatchUpdatePayload
} from './model';

const BASE = '/finance/payment-batch';

/* ---------------- 出纳台聚合 ---------------- */

export async function getCashierOverview(params?: { enterpriseId?: number }) {
  const res = await request.get<ApiResult<CashierOverview>>(
    `${BASE}/workbench/overview`,
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function pageFundFlow(params: FundFlowParam) {
  const res = await request.get<
    ApiResult<PageResult<FundFlowRow> & { summary: FundFlowSummary }>
  >(`${BASE}/workbench/flow`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getPayCalendar(params?: { days?: number }) {
  const res = await request.get<ApiResult<PayCalendarDay[]>>(
    `${BASE}/workbench/calendar`,
    { params }
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

/* ---------------- 候选与批次 ---------------- */

export async function listPayableCandidates(params?: {
  docKinds?: string;
  keyword?: string;
  dueBefore?: string;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: PayableCandidate[]; count: number }>
  >(`${BASE}/candidates`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function pagePaymentBatches(params: PaymentBatchParam) {
  const res = await request.get<ApiResult<PageResult<PaymentBatchListItem>>>(
    BASE,
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function createPaymentBatch(data: PaymentBatchCreatePayload) {
  const res = await request.post<ApiResult<PaymentBatchDetail>>(BASE, data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getPaymentBatch(batchId: number) {
  const res = await request.get<ApiResult<PaymentBatchDetail>>(
    `${BASE}/${batchId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updatePaymentBatch(
  batchId: number,
  data: PaymentBatchUpdatePayload
) {
  const res = await request.put<ApiResult<PaymentBatchDetail>>(
    `${BASE}/${batchId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removePaymentBatch(batchId: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${batchId}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function listPaymentBatchItems(batchId: number) {
  const res = await request.get<ApiResult<PaymentBatchItem[]>>(
    `${BASE}/${batchId}/items`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function addPaymentBatchItems(
  batchId: number,
  docs: PayableDocRef[]
) {
  const res = await request.post<ApiResult<PaymentBatchDetail>>(
    `${BASE}/${batchId}/items`,
    { docs }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removePaymentBatchItem(batchId: number, itemId: number) {
  const res = await request.delete<ApiResult<PaymentBatchDetail>>(
    `${BASE}/${batchId}/items/${itemId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function submitPaymentBatch(batchId: number) {
  const res = await request.post<ApiResult<PaymentBatchDetail>>(
    `${BASE}/${batchId}/submit`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function approvePaymentBatch(batchId: number) {
  const res = await request.post<ApiResult<PaymentBatchDetail>>(
    `${BASE}/${batchId}/approve`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function rejectPaymentBatch(batchId: number, reason: string) {
  const res = await request.post<ApiResult<PaymentBatchDetail>>(
    `${BASE}/${batchId}/reject`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function executePaymentBatch(
  batchId: number,
  data: { results?: BatchExecItem[]; paidAt?: string }
) {
  const res = await request.post<ApiResult<PaymentBatchDetail>>(
    `${BASE}/${batchId}/execute`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelPaymentBatch(batchId: number, reason: string) {
  const res = await request.post<ApiResult<PaymentBatchDetail>>(
    `${BASE}/${batchId}/cancel`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listPaymentBatchEvents(batchId: number) {
  const res = await request.get<ApiResult<FinanceDocEvent[]>>(
    `${BASE}/${batchId}/events`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}
