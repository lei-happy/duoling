import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  CustomerInvoiceCreatePayload,
  CustomerInvoiceDetail,
  CustomerInvoiceItemPayload,
  CustomerInvoiceListItem,
  CustomerInvoiceParam,
  CustomerInvoiceUpdatePayload,
  FinanceDocEvent,
  InvoiceAllocation,
  InvoiceIssuePayload,
  InvoiceSettleCandidate,
  InvoiceSettleLink,
  PendingInvoiceSettle
} from './model';

const BASE = '/finance/customer-invoice';

export async function pageCustomerInvoices(params: CustomerInvoiceParam) {
  const res = await request.get<ApiResult<PageResult<CustomerInvoiceListItem>>>(
    BASE,
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listPendingInvoicePool(params?: {
  customerId?: number;
  onlyRequired?: boolean;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: PendingInvoiceSettle[]; count: number }>
  >(`${BASE}/pending-list`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listInvoiceSettleCandidates(params: {
  customerId: number;
  keyword?: string;
  invoiceId?: number;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: InvoiceSettleCandidate[]; count: number }>
  >(`${BASE}/candidates`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function createCustomerInvoice(
  data: CustomerInvoiceCreatePayload
) {
  const res = await request.post<ApiResult<CustomerInvoiceDetail>>(BASE, data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getCustomerInvoice(invoiceId: number) {
  const res = await request.get<ApiResult<CustomerInvoiceDetail>>(
    `${BASE}/${invoiceId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateCustomerInvoice(
  invoiceId: number,
  data: CustomerInvoiceUpdatePayload
) {
  const res = await request.put<ApiResult<CustomerInvoiceDetail>>(
    `${BASE}/${invoiceId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeCustomerInvoice(invoiceId: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${invoiceId}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function listInvoiceSettles(invoiceId: number) {
  const res = await request.get<ApiResult<InvoiceSettleLink[]>>(
    `${BASE}/${invoiceId}/settles`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function linkInvoiceSettles(
  invoiceId: number,
  allocations: InvoiceAllocation[]
) {
  const res = await request.post<ApiResult<CustomerInvoiceDetail>>(
    `${BASE}/${invoiceId}/settles`,
    { allocations }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function unlinkInvoiceSettle(invoiceId: number, linkId: number) {
  const res = await request.delete<ApiResult<CustomerInvoiceDetail>>(
    `${BASE}/${invoiceId}/settles/${linkId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function replaceInvoiceItems(
  invoiceId: number,
  items: CustomerInvoiceItemPayload[]
) {
  const res = await request.put<ApiResult<CustomerInvoiceDetail>>(
    `${BASE}/${invoiceId}/items`,
    { items }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function submitCustomerInvoice(invoiceId: number) {
  const res = await request.post<ApiResult<CustomerInvoiceDetail>>(
    `${BASE}/${invoiceId}/submit`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function withdrawCustomerInvoice(
  invoiceId: number,
  reason: string
) {
  const res = await request.post<ApiResult<CustomerInvoiceDetail>>(
    `${BASE}/${invoiceId}/withdraw`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function issueCustomerInvoice(
  invoiceId: number,
  data: InvoiceIssuePayload
) {
  const res = await request.post<ApiResult<CustomerInvoiceDetail>>(
    `${BASE}/${invoiceId}/issue`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function voidCustomerInvoice(invoiceId: number, reason: string) {
  const res = await request.post<ApiResult<CustomerInvoiceDetail>>(
    `${BASE}/${invoiceId}/void`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function redFlushCustomerInvoice(
  invoiceId: number,
  reason: string
) {
  const res = await request.post<ApiResult<CustomerInvoiceDetail>>(
    `${BASE}/${invoiceId}/red-flush`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelCustomerInvoice(invoiceId: number, reason: string) {
  const res = await request.post<ApiResult<CustomerInvoiceDetail>>(
    `${BASE}/${invoiceId}/cancel`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listCustomerInvoiceEvents(invoiceId: number) {
  const res = await request.get<ApiResult<FinanceDocEvent[]>>(
    `${BASE}/${invoiceId}/events`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}
