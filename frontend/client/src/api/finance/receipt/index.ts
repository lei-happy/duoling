import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  FinanceDocEvent,
  ReceiptAllocation,
  ReceiptClaimCandidate,
  ReceiptDetail,
  ReceiptListItem,
  ReceiptParam,
  ReceiptPayload,
  ReceiptStats
} from './model';

const BASE = '/finance/receipt';

export async function getReceiptStats() {
  const res = await request.get<ApiResult<ReceiptStats>>(`${BASE}/stats`);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function pageReceipts(params: ReceiptParam) {
  const res = await request.get<ApiResult<PageResult<ReceiptListItem>>>(BASE, {
    params
  });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function createReceipt(data: ReceiptPayload) {
  const res = await request.post<ApiResult<ReceiptDetail>>(BASE, data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getReceipt(receiptId: number) {
  const res = await request.get<ApiResult<ReceiptDetail>>(
    `${BASE}/${receiptId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateReceipt(receiptId: number, data: ReceiptPayload) {
  const res = await request.put<ApiResult<ReceiptDetail>>(
    `${BASE}/${receiptId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeReceipt(receiptId: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${receiptId}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function listClaimCandidates(
  receiptId: number,
  params?: { keyword?: string; limit?: number }
) {
  const res = await request.get<
    ApiResult<{ list: ReceiptClaimCandidate[]; count: number }>
  >(`${BASE}/${receiptId}/claim-candidates`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function suggestAllocation(receiptId: number) {
  const res = await request.get<
    ApiResult<{ list: ReceiptAllocation[]; count: number }>
  >(`${BASE}/${receiptId}/suggest-allocation`);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function claimReceipt(
  receiptId: number,
  allocations: ReceiptAllocation[]
) {
  const res = await request.post<ApiResult<ReceiptDetail>>(
    `${BASE}/${receiptId}/claim`,
    { allocations }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function unclaimReceipt(
  receiptId: number,
  data: { settleId: number; reason?: string }
) {
  const res = await request.post<ApiResult<ReceiptDetail>>(
    `${BASE}/${receiptId}/unclaim`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelReceipt(receiptId: number, reason: string) {
  const res = await request.post<ApiResult<ReceiptDetail>>(
    `${BASE}/${receiptId}/cancel`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listReceiptEvents(receiptId: number) {
  const res = await request.get<ApiResult<FinanceDocEvent[]>>(
    `${BASE}/${receiptId}/events`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}
