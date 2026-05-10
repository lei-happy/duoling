import type { PageParam } from '@/api';

export interface Capacity {
  id?: number;
  driverId?: number;
  driverName?: string;
  driverPhone?: string;
  vehicleId?: number;
  plateNumber?: string;
  status?: number;
  boundAt?: string;
  unboundAt?: string;
  remark?: string;
  createdAt?: string;
}

export interface CapacityParam extends PageParam {
  keyword?: string;
}

export interface CapacityBindData {
  driverId: number;
  vehicleId: number;
  remark?: string;
}

export interface CapacityUnbindData {
  remark?: string;
}
