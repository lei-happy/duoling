import type { PageParam } from '@/api';

export interface Customer {
  id?: number;
  customerCode?: string;
  customerName?: string;
  shortName?: string;
  customerType?: number;
  contactPerson?: string;
  contactPhone?: string;
  address?: string;
  settlementType?: number;
  creditCode?: string;
  status?: number;
  remark?: string;
  createdAt?: string;
  /** 账期天数，null 表示未设置（按 0 天算） */
  paymentDays?: number | null;
  /** 信用额度，null 表示不限额 */
  creditLimit?: number | null;
  /** 0-暂停合作 1-正常 2-重点关注 */
  creditStatus?: number;
  creditStatusLabel?: string;
}

export interface CustomerParam extends PageParam {
  keyword?: string;
  customerType?: number;
  settlementType?: number;
  status?: number;
}

export interface CustomerSelectItem {
  id: number;
  customerName: string;
  shortName?: string;
  customerCode?: string;
}
