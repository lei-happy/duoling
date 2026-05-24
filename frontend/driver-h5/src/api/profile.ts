import { get, put } from './request';

export interface DriverProfile {
  id: number;
  driverCode: string;
  name: string;
  phone: string;
  gender?: number;
  avatar?: string;
  idCard?: string;
  emergencyContact?: string;
  emergencyPhone?: string;
  homeAddress?: string;
  status: number;
  remark?: string;
}

export interface ProfileUpdate {
  emergencyContact?: string;
  emergencyPhone?: string;
  homeAddress?: string;
  avatar?: string;
}

export function getMyProfile() {
  return get<DriverProfile>('/profile/me');
}

export function updateMyProfile(payload: ProfileUpdate) {
  return put<DriverProfile>('/profile/me', payload);
}
