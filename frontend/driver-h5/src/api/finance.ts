import { get } from './request';
import type { PageResult } from './task';

export interface FinanceDocItem {
  id: number;
  docNo: string;
  docType: number;
  isFinal: number;
  taskId: number;
  taskNo?: string;
  payeeName?: string;
  plannedAmount: number;
  actualAmount?: number;
  status: number;
  plannedPayTime?: string;
  actualPayTime?: string;
  payMethod?: number;
  remark?: string;
}

export interface FinanceItem {
  id: number;
  itemType: string;
  itemName?: string;
  quantity?: number;
  unit?: string;
  unitPrice?: number;
  amount: number;
}

export interface FinanceDocDetail extends FinanceDocItem {
  items: FinanceItem[];
  payVoucherUrl?: string;
}

export interface FinanceSummary {
  totalIncome: number;
  prepaidAmount: number;
  supplementAmount: number;
  settledAmount: number;
  byMonth: { month: string; amount: number }[];
}

export interface DriverAccount {
  id: number;
  accountType: number;
  accountName: string;
  accountNo: string;
  balance: number;
  status: number;
}

export interface FinanceListQuery {
  page?: number;
  pageSize?: number;
  docType?: number;
  status?: number;
  yearMonth?: string;
}

export function listMyFinance(params: FinanceListQuery) {
  return get<PageResult<FinanceDocItem>>('/finance/my', params as Record<string, unknown>);
}

export function getFinanceDetail(docId: number) {
  return get<FinanceDocDetail>(`/finance/${docId}`);
}

export function getFinanceSummary(params?: { yearMonth?: string }) {
  return get<FinanceSummary>('/finance/summary', params as Record<string, unknown>);
}

export function listMyAccounts() {
  return get<DriverAccount[]>('/finance/account');
}

/** 资金账户（往来账） */
export interface FundAccount {
  id: number;
  driverId: number;
  balance: number;
  frozenAmount: number;
  totalIn: number;
  totalOut: number;
  status: number;
  lastTxnAt?: string;
}

export interface FundTransaction {
  id: number;
  txnNo: string;
  bizType: number;
  direction: number;
  amount: number;
  delta: number;
  balanceAfter: number;
  operatorName?: string;
  remark?: string;
  createdAt: string;
}

export function getMyFundAccount() {
  return get<FundAccount>('/finance/fund-account');
}

export function listMyFundTransactions(params: {
  page?: number;
  pageSize?: number;
  bizType?: number;
}) {
  return get<PageResult<FundTransaction>>(
    '/finance/fund-account/transactions',
    params as Record<string, unknown>
  );
}
