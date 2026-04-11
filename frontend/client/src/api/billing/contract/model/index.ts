import type { PageParam } from '@/api';

export interface FreightContract {
  id?: number;
  contractNo?: string;
  contractName?: string;
  customerId?: number;
  customerName?: string;
  effectiveDate?: string;
  expiryDate?: string;
  status?: number;
  remark?: string;
  rateCount?: number;
  createdAt?: string;
}

export interface FreightContractParam extends PageParam {
  keyword?: string;
  status?: number;
}

export interface FreightRate {
  id?: number;
  contractId?: number;
  customerId?: number;
  origin?: string;
  originCode?: string;
  destination?: string;
  destinationCode?: string;
  vehicleBrand?: string;
  vehicleModel?: string;
  billingMode?: number;
  distanceKm?: number;
  unitPrice?: number;
  priceType?: number;
  effectiveDate?: string;
  expiryDate?: string;
  status?: number;
}

export interface FreightCalcRequest {
  customerId: number;
  originCode: string;
  destinationCode: string;
  vehicleBrand?: string;
  vehicleModel?: string;
}

export interface FreightCalcResult {
  unitPrice: number;
  billingMode?: number;
  distanceKm?: number;
  totalAmount?: number;
  contractId: number;
  contractNo: string;
  rateId: number;
  matchLevel: string;
  priceType?: number;
}
