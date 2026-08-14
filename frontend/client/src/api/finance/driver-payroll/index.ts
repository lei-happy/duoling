import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  DriverAccount,
  FinanceDocEvent,
  PayrollCandidate,
  PayrollCreatePayload,
  PayrollDetail,
  PayrollItem,
  PayrollItemPayload,
  PayrollItemUpdatePayload,
  PayrollListItem,
  PayrollParam,
  PayrollPayPayload,
  PayrollTaskAdjustPayload,
  PayrollTaskLink,
  PayrollUpdatePayload,
  Payslip
} from './model';

const BASE = '/finance/driver-payroll';

export async function listPayrollCandidates(params: {
  driverId: number;
  periodStart?: string;
  periodEnd?: string;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: PayrollCandidate[]; count: number }>
  >(`${BASE}/candidates`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listDriverAccounts(driverId: number) {
  const res = await request.get<ApiResult<DriverAccount[]>>(
    `${BASE}/accounts`,
    { params: { driverId } }
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function pagePayrolls(params: PayrollParam) {
  const res = await request.get<ApiResult<PageResult<PayrollListItem>>>(BASE, {
    params
  });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getPayroll(payrollId: number) {
  const res = await request.get<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function addPayroll(data: PayrollCreatePayload) {
  const res = await request.post<ApiResult<PayrollDetail>>(BASE, data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updatePayroll(
  payrollId: number,
  data: PayrollUpdatePayload
) {
  const res = await request.put<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removePayroll(payrollId: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${payrollId}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function getPayslip(payrollId: number) {
  const res = await request.get<ApiResult<Payslip>>(
    `${BASE}/${payrollId}/payslip`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listPayrollTasks(payrollId: number) {
  const res = await request.get<ApiResult<PayrollTaskLink[]>>(
    `${BASE}/${payrollId}/tasks`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function addPayrollTasks(
  payrollId: number,
  taskIds: number[],
  unitPrice?: number,
  billingBase?: number
) {
  const res = await request.post<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/tasks`,
    { taskIds, unitPrice, billingBase }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function adjustPayrollTask(
  payrollId: number,
  linkId: number,
  data: PayrollTaskAdjustPayload
) {
  const res = await request.put<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/tasks/${linkId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removePayrollTask(payrollId: number, linkId: number) {
  const res = await request.delete<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/tasks/${linkId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listPayrollItems(payrollId: number) {
  const res = await request.get<ApiResult<PayrollItem[]>>(
    `${BASE}/${payrollId}/items`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function addPayrollItem(
  payrollId: number,
  data: PayrollItemPayload
) {
  const res = await request.post<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/items`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updatePayrollItem(
  payrollId: number,
  itemId: number,
  data: PayrollItemUpdatePayload
) {
  const res = await request.put<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/items/${itemId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removePayrollItem(payrollId: number, itemId: number) {
  const res = await request.delete<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/items/${itemId}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updatePayrollAccount(
  payrollId: number,
  accountId: number
) {
  const res = await request.put<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/account`,
    { accountId }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function approvePayrollAdjust(payrollId: number) {
  const res = await request.post<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/approve-adjust`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function submitPayroll(payrollId: number) {
  const res = await request.post<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/submit`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function approvePayroll(payrollId: number) {
  const res = await request.post<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/approve`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function rejectPayroll(payrollId: number, reason: string) {
  const res = await request.post<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/reject`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function withdrawPayroll(payrollId: number, reason: string) {
  const res = await request.post<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/withdraw`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function payPayroll(payrollId: number, data: PayrollPayPayload) {
  const res = await request.post<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/pay`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelPayrollPay(payrollId: number, reason: string) {
  const res = await request.post<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/cancel-pay`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function cancelPayroll(payrollId: number, reason: string) {
  const res = await request.post<ApiResult<PayrollDetail>>(
    `${BASE}/${payrollId}/cancel`,
    { reason }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listPayrollEvents(payrollId: number) {
  const res = await request.get<ApiResult<FinanceDocEvent[]>>(
    `${BASE}/${payrollId}/events`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}
