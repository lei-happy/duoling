import type { PageParam } from '@/api';

export interface Trailer {
  id?: number;
  plateNumber?: string;
  vehiclePlateNumber?: string;
  status?: number;
  trailerType?: string;
  axleCount?: number;
  loadCapacity?: number;
  volumeCapacity?: number;
  length?: number;
  width?: number;
  height?: number;
  parkingSpots?: number;
  purchaseDate?: string;
  remark?: string;
  createdAt?: string;
}

export interface TrailerParam extends PageParam {
  keyword?: string;
  trailerType?: string;
  status?: number;
}
