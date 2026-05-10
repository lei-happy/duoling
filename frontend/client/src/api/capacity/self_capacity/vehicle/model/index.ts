import type { PageParam } from '@/api';

export interface Vehicle {
  id?: number;
  plateNumber?: string;
  trailerId?: number | null;
  trailerPlateNumber?: string;
  status?: number;
  statusSource?: string;
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
  remark?: string;
  createdAt?: string;
}

export interface VehicleParam extends PageParam {
  keyword?: string;
  vehicleType?: string;
  status?: number;
}

export interface TrailerOption {
  id: number;
  plateNumber: string;
}
