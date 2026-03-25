import type { PageParam } from '@/api';

export interface Driver {
  id?: number;
  userId?: number;
  name?: string;
  phone?: string;
  idCard?: string;
  gender?: number;
  licenseType?: string;
  licenseNo?: string;
  licenseExpire?: string;
  qualificationNo?: string;
  qualificationExpire?: string;
  emergencyContact?: string;
  emergencyPhone?: string;
  avatar?: string;
  status?: number;
  remark?: string;
  createdAt?: string;
}

export interface DriverParam extends PageParam {
  keyword?: string;
  licenseType?: string;
  status?: number;
}
