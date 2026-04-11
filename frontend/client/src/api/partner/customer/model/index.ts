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
