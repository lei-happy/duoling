import type { PageParam } from '@/api';

export interface Customer {
  id?: number;
  customerName?: string;
  shortName?: string;
  customerType?: number;
  contactPerson?: string;
  contactPhone?: string;
  address?: string;
  status?: number;
  remark?: string;
  createdAt?: string;
}

export interface CustomerParam extends PageParam {
  keyword?: string;
  customerType?: number;
  status?: number;
}
