import type { PageParam } from '@/api';
import type { FinanceDocEvent } from '@/api/finance/customer-recon/model';

export type { FinanceDocEvent };

export interface BankAccountItem {
  id: number;
  enterpriseId: number;
  accountName: string;
  accountNo: string;
  accountNoMasked?: string;
  bankName?: string;
  bankBranch?: string;
  accountType: number;
  accountTypeLabel?: string;
  currency: string;
  balance: number;
  usageScope: number;
  usageScopeLabel?: string;
  isDefaultReceive: number;
  isDefaultPay: number;
  status: number;
  sortOrder: number;
  displayLabel?: string;
  remark?: string;
  createdAt?: string;
}

export interface BankAccountOption {
  id: number;
  accountName: string;
  accountNoMasked?: string;
  bankName?: string;
  displayLabel?: string;
  balance: number;
  usageScope: number;
  isDefaultReceive: number;
  isDefaultPay: number;
}

export interface BankAccountParam extends PageParam {
  keyword?: string;
  enterpriseId?: number;
  accountType?: number;
  usageScope?: number;
  status?: number;
}

export interface BankAccountPayload {
  enterpriseId?: number;
  accountName?: string;
  accountNo?: string;
  bankName?: string;
  bankBranch?: string;
  accountType?: number;
  currency?: string;
  usageScope?: number;
  balance?: number;
  isDefaultReceive?: number;
  isDefaultPay?: number;
  sortOrder?: number;
  remark?: string;
}

export interface BalanceSummary {
  accountCount: number;
  balanceTotal: number;
}
