import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  BalanceSummary,
  BankAccountItem,
  BankAccountOption,
  BankAccountParam,
  BankAccountPayload,
  FinanceDocEvent
} from './model';

const BASE = '/finance/bank-account';

export async function pageBankAccounts(params: BankAccountParam) {
  const res = await request.get<ApiResult<PageResult<BankAccountItem>>>(BASE, {
    params
  });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listBankAccountOptions(params?: {
  enterpriseId?: number;
  forPay?: boolean;
}) {
  const res = await request.get<ApiResult<BankAccountOption[]>>(
    `${BASE}/options`,
    { params }
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}

export async function getBalanceSummary(params?: { enterpriseId?: number }) {
  const res = await request.get<ApiResult<BalanceSummary>>(`${BASE}/summary`, {
    params
  });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function createBankAccount(data: BankAccountPayload) {
  const res = await request.post<ApiResult<BankAccountItem>>(BASE, data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateBankAccount(
  accountId: number,
  data: BankAccountPayload
) {
  const res = await request.put<ApiResult<BankAccountItem>>(
    `${BASE}/${accountId}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function setBankAccountStatus(accountId: number, status: number) {
  const res = await request.put<ApiResult<BankAccountItem>>(
    `${BASE}/${accountId}/status`,
    { status }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function calibrateBankAccount(
  accountId: number,
  data: { balance: number; reason: string }
) {
  const res = await request.post<ApiResult<BankAccountItem>>(
    `${BASE}/${accountId}/calibrate`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function removeBankAccount(accountId: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${accountId}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function listBankAccountEvents(accountId: number) {
  const res = await request.get<ApiResult<FinanceDocEvent[]>>(
    `${BASE}/${accountId}/events`
  );
  if (res.data.code === 0) return res.data.data || [];
  return Promise.reject(new Error(res.data.message));
}
