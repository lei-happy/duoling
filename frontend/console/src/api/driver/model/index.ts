import type { PageParam } from '@/api';

export interface PlatformDriver {
  id?: number;
  tenantCode?: string;
  tenantName?: string;
  bizDriverId?: number;
  driverCode?: string;
  name?: string;
  phone?: string;
  status?: number;
  createdAt?: string;
  updatedAt?: string;
}

export interface PlatformDriverParam extends PageParam {
  keyword?: string;
  tenantCode?: string;
  status?: number;
}
