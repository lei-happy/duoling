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
  /** 运力运营状态 1-可接单 2-运输中 3-休假 4-停运 5-维修保养 */
  operationStatus?: number;
  /** 驾驶员运营状态（仅参考，与运力状态相互独立） */
  driverOperationStatus?: number;
  vehicleType?: string;
}

export interface CapacityParam extends PageParam {
  keyword?: string;
  operationStatus?: number;
}

export interface CapacityBindData {
  driverId: number;
  vehicleId: number;
  remark?: string;
}

export interface CapacityUnbindData {
  remark?: string;
}

export interface CapacityStatusUpdateData {
  operationStatus: number;
}
