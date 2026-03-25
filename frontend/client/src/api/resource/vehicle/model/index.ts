import type { PageParam } from '@/api';

export interface Vehicle {
  id?: number;
  plateNumber?: string;
  vehicleType?: string;
  brand?: string;
  model?: string;
  color?: string;
  vin?: string;
  engineNo?: string;
  loadCapacity?: number;
  volumeCapacity?: number;
  purchaseDate?: string;
  insuranceExpire?: string;
  inspectionExpire?: string;
  gpsDeviceId?: string;
  status?: number;
  remark?: string;
  createdAt?: string;
}

export interface VehicleParam extends PageParam {
  keyword?: string;
  vehicleType?: string;
  status?: number;
}
