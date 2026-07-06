import type { PageParam } from '@/api';
import type { PlateCategory } from '@/constants/plate-category';

export interface Vehicle {
  id?: number;
  plateNumber?: string;
  plateCategory?: PlateCategory;
  /** 所属经营主体ID */
  enterpriseId?: number | null;
  trailerId?: number | null;
  trailerPlateNumber?: string;
  trailerPlateCategory?: PlateCategory;
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
  enterpriseId?: number;
}

export interface TrailerOption {
  id: number;
  plateNumber: string;
  plateCategory?: PlateCategory;
}
