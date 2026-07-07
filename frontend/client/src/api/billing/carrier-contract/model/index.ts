import type { PageParam } from '@/api';

export interface CarrierContract {
  id?: number;
  contractNo?: string;
  contractName?: string;
  carrierId?: number;
  carrierName?: string;
  effectiveDate?: string;
  expiryDate?: string;
  status?: number;
  remark?: string;
  activeRateCount?: number;
  totalRateCount?: number;
  createdAt?: string;
}

export interface CarrierContractParam extends PageParam {
  keyword?: string;
  carrierId?: number;
  status?: number;
}

export interface CarrierRate {
  id?: number;
  contractId?: number;
  carrierId?: number;
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

/** 合同详情页承运价明细本地筛选 */
export interface CarrierRateFilterParam {
  keyword?: string;
  billingMode?: number;
  priceType?: number;
  status?: number;
}

export interface CarrierFreightPreviewVehicle {
  brandId?: number | null;
  seriesId?: number | null;
  vehicleBrand?: string | null;
  vehicleModel?: string | null;
  quantity?: number;
}

export interface CarrierFreightPreviewRequest {
  taskId?: number;
  carrierId?: number;
  originRegionId?: number | null;
  destinationRegionId?: number | null;
  totalQuantity?: number;
  vehicles?: CarrierFreightPreviewVehicle[];
  transportDate?: string;
}

export interface CarrierFreightItem {
  brandId?: number | null;
  seriesId?: number | null;
  vehicleBrand?: string | null;
  vehicleModel?: string | null;
  quantity?: number;
  matchedContractId?: number | null;
  matchedRuleId?: number | null;
  matchedRuleVersion?: number | null;
  direction?: string | null;
  modelMatchType?: string | null;
  originMatchLevel?: string | null;
  destinationMatchLevel?: string | null;
  unitPrice?: number | null;
  billingMode?: number | null;
  distanceKm?: number | null;
  amount?: number;
  matchScore?: number | null;
  calcStatus?: string;
  errorType?: string | null;
  errorMessage?: string | null;
}

export interface CarrierFreightResult {
  taskId?: number;
  totalAmount?: number;
  calcStatus?: string;
  carrierId?: number | null;
  carrierName?: string | null;
  matchedContractId?: number | null;
  errorMessage?: string | null;
  items?: CarrierFreightItem[];
  calcTime?: string | null;
  calcEngineVersion?: string | null;
}
