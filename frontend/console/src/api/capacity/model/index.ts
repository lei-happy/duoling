import type { PageParam } from '@/api';

export interface PlatformCapacity {
  id?: number;
  tenantCode?: string;
  tenantName?: string;
  bizCapacityId?: number;
  driverName?: string;
  driverPhone?: string;
  plateNumber?: string;
  status?: number;
  boundAt?: string;
  unboundAt?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface PlatformCapacityParam extends PageParam {
  keyword?: string;
  tenantCode?: string;
  status?: number;
}
