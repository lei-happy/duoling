import type { PageParam } from '@/api';

export interface CapacityLog {
  id?: number;
  capacityId?: number;
  driverId?: number;
  driverName?: string;
  driverCode?: string;
  driverPhone?: string;
  vehicleId?: number;
  plateNumber?: string;
  plateCategory?: string;
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
  operatorName?: string;
  actionTimeStart?: string;
  actionTimeEnd?: string;
}
