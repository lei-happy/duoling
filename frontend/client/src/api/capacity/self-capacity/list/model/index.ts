import type { PageParam } from '@/api';
import type { PlateCategory } from '@/constants/plate-category';

export interface Capacity {
  id?: number;
  driverId?: number;
  driverName?: string;
  driverPhone?: string;
  vehicleId?: number;
  plateNumber?: string;
  plateCategory?: PlateCategory;
  trailerPlateNumber?: string;
  trailerPlateCategory?: PlateCategory;
  status?: number;
  boundAt?: string;
  unboundAt?: string;
  remark?: string;
  createdAt?: string;
  driverAvatar?: string;
  departmentName?: string;
  operationStatus?: number;
  vehicleType?: string;
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
