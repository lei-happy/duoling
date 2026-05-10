import type { PageParam } from '@/api';

export interface Driver {
  id?: number;
  driverCode?: string;
  userId?: number;
  name?: string;
  gender?: number;
  phone?: string;
  idCard?: string;
  avatar?: string;
  emergencyContact?: string;
  emergencyPhone?: string;
  homeAddress?: string;
  status?: number;
  remark?: string;
  licenseType?: string;
  licenseNo?: string;
  licenseExpire?: string;
  qualificationNo?: string;
  qualificationExpire?: string;
  licensePhoto?: string;
  qualificationPhoto?: string;
  idCardFrontPhoto?: string;
  idCardBackPhoto?: string;
  departmentId?: number;
  departmentName?: string;
  driverType?: string;
  residentAreas?: ResidentArea[];
  commonRoutes?: string;
  operationStatus?: number;
  createdAt?: string;
}

export interface ResidentArea {
  province?: string;
  city?: string;
}

export interface DriverParam extends PageParam {
  keyword?: string;
  status?: number;
  driverType?: string;
  operationStatus?: number;
  departmentId?: number;
}

export interface DriverAccount {
  id?: number;
  driverId?: number;
  enterpriseId?: number;
  accountType?: number;
  accountName?: string;
  accountNo?: string;
  balance?: number;
  status?: number;
  createdAt?: string;
  updatedAt?: string;
}

export interface DriverRoute {
  id?: number;
  driverId?: number;
  originCode?: string;
  originName?: string;
  destCode?: string;
  destName?: string;
  status?: number;
}
