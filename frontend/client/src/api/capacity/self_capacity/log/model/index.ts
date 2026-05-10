import type { PageParam } from '@/api';

export interface CapacityLog {
  id?: number;
  capacityId?: number;
  driverId?: number;
  driverName?: string;
  vehicleId?: number;
  plateNumber?: string;
  action?: number;
  actionTime?: string;
  operatorId?: number;
  operatorName?: string;
  remark?: string;
  createdAt?: string;
}

export interface CapacityLogParam extends PageParam {
  keyword?: string;
  action?: number;
}
