import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  DeductSummaryRow,
  FinanceDocEvent,
  InvoiceMatchCandidate,
  InvoiceMatchPayload,
  InvoiceSettleLink,
  PendingInvoiceSettle,
  VendorInvoiceCreatePayload,
  VendorInvoiceDetail,
  VendorInvoiceListItem,
  VendorInvoiceParam,
  VendorInvoiceUpdatePayload
} from './model';

const BASE = '/finance/vendor-invoice';

export async function pageVendorInvoices(params: VendorInvoiceParam) {
  const res = await request.get<ApiResult<PageResult<VendorInvoiceListItem>>>(
    BASE,
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getDeductSummary(params: {
  groupBy?: string;
  buyerEntityId?: number;
  periodFrom?: string;
  periodTo?: string;
}) {
  const res = await request.get<
    ApiResult<{ list: DeductSummaryRow[]; count: number }>
  >(`${BASE}/deduct-summary`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listPendingInvoiceSettles(params: {
  carrierId?: number;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: PendingInvoiceSettle[]; count: number }>
  >(`${BASE}/pending-list`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function registerVendorInvoice(data: VendorInvoiceCreatePayload) {
  const res = await request.post<ApiResult<VendorInvoiceDetail>>(BASE, data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getVendorInvoice(invoiceId: number) {
  const res = await request.get<ApiResult<VendorInvoiceDetail>>(
    `${BASE}/${invoiceId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateVendorInvoice(
  invoiceId: number,
  data: VendorInvoiceUpdatePayload
) {
  const res = await request.put<ApiResult<VendorInvoiceDetail>>(
    `${BASE}/${invoiceId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeVendorInvoice(invoiceId: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${invoiceId}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function listInvoiceCandidates(
  invoiceId: number,
  params?: { keyword?: string; limit?: number }
) {
  const res = await request.get<
    ApiResult<{ list: InvoiceMatchCandidate[]; count: number }>
  >(`${BASE}/${invoiceId}/candidates`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function matchVendorInvoice(
  invoiceId: number,
  data: InvoiceMatchPayload
) {
  const res = await request.post<ApiResult<VendorInvoiceDetail>>(
    `${BASE}/${invoiceId}/match`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listInvoiceMatches(invoiceId: number) {
  const res = await request.get<ApiResult<InvoiceSettleLink[]>>(
    `${BASE}/${invoiceId}/match`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function unmatchVendorInvoice(invoiceId: number, linkId: number) {
  const res = await request.delete<ApiResult<VendorInvoiceDetail>>(
    `${BASE}/${invoiceId}/match/${linkId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function voidVendorInvoice(invoiceId: number, reason: string) {
  const res = await request.post<ApiResult<VendorInvoiceDetail>>(
    `${BASE}/${invoiceId}/void`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelVendorInvoice(invoiceId: number, reason: string) {
  const res = await request.post<ApiResult<VendorInvoiceDetail>>(
    `${BASE}/${invoiceId}/cancel`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listVendorInvoiceEvents(invoiceId: number) {
  const res = await request.get<ApiResult<FinanceDocEvent[]>>(
    `${BASE}/${invoiceId}/events`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}
