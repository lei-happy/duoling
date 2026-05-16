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
  activeRateCount?: number;
  totalRateCount?: number;
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
  originRegionId?: number | null;
  destination?: string;
  destinationCode?: string;
  destinationRegionId?: number | null;
  vehicleBrand?: string | null;
  vehicleModel?: string | null;
  brandId?: number | null;
  seriesId?: number | null;
  matchType?: string;
  billingMode?: number;
  distanceKm?: number;
  unitPrice?: number;
  minAmount?: number | null;
  priceType?: number;
  isBidirectional?: number;
  priority?: number;
  effectiveDate?: string;
  expiryDate?: string;
  status?: number;
  ruleVersion?: number;
}

/** 合同详情页运价明细本地筛选 */
export interface FreightRateFilterParam {
  keyword?: string;
  billingMode?: number;
  priceType?: number;
  status?: number;
}

export interface FreightCalcRequest {
  customerId: number;
  originCode: string;
  destinationCode: string;
  vehicleBrand?: string;
  vehicleModel?: string;
  /** 台数，默认 1 */
  quantity?: number;
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
