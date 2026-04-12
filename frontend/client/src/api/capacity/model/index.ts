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
  status?: number;
}

export interface CapacityBindData {
  driverId: number;
  vehicleId: number;
  remark?: string;
}

export interface CapacityUnbindData {
  remark?: string;
}

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

export interface DriverOption {
  id: number;
  name: string;
  phone: string;
  driverCode: string;
}

export interface VehicleOption {
  id: number;
  plateNumber: string;
}
