import type { PageParam } from '@/api';

export interface Order {
  id?: number;
  orderNo?: string;
  customerId?: number;
  customerName?: string;
  vehicleId?: number;
  plateNumber?: string;
  driverId?: number;
  driverName?: string;
  routeId?: number;
  origin?: string;
  destination?: string;
  cargoName?: string;
  cargoWeight?: number;
  cargoVolume?: number;
  freightAmount?: number;
  planDepartTime?: string;
  actualDepartTime?: string;
  planArriveTime?: string;
  actualArriveTime?: string;
  status?: number;
  remark?: string;
  createdAt?: string;
}

export interface OrderParam extends PageParam {
  keyword?: string;
  status?: number;
}
