import type { PageParam } from '@/api';

export interface CarrierCapacityVehicleInfo {
  plateNumber: string;
  plateCategory?: string;
  vehicleType?: string;
  brand?: string;
  model?: string;
  loadCapacity?: number;
  registrationDate?: string;
  inspectionExpire?: string;
  insuranceExpire?: string;
  transportLicenseNo?: string;
  transportLicenseExpire?: string;
}

export interface CarrierCapacityDriverInfo {
  name: string;
  gender?: number;
  phone: string;
  idCard?: string;
  licenseType?: string;
  licenseNo?: string;
  licenseExpire?: string;
  qualificationNo?: string;
  qualificationExpire?: string;
}

export interface CarrierCapacityListItem {
  id: number;
  carrierCapacityCode: string;
  carrierId: number;
  carrierName?: string;
  driverName: string;
  driverPhone: string;
  plateNumber: string;
  vehicleTypeLabel?: string;
  approvalStatus: number;
  status: number;
  createdAt?: string;
}

export interface CarrierCapacityDetail extends CarrierCapacityListItem {
  driverIdCard?: string;
  source?: string;
  sourceRemark?: string;
  statusRemark?: string;
  remark?: string;
  vehicle?: CarrierCapacityVehicleInfo;
  driver?: CarrierCapacityDriverInfo;
}

export interface CarrierCapacitySaveParam {
  carrierId: number;
  source?: string;
  sourceRemark?: string;
  remark?: string;
  vehicle: CarrierCapacityVehicleInfo;
  driver: CarrierCapacityDriverInfo;
}

export interface CarrierCapacityParam extends PageParam {
  keyword?: string;
  carrierId?: number;
  status?: number;
}
