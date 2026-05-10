import type { PageParam } from '@/api';

/** 运单货物明细（一单多车型） */
export interface WaybillCargoLine {
  id?: number;
  vehicleBrand?: string;
  vehicleModel?: string;
  quantity?: number;
  sortOrder?: number;
}

export interface Waybill {
  id?: number;
  waybillNo?: string;
  customerId?: number;
  customerName?: string;
  origin?: string;
  originCode?: string;
  destination?: string;
  destinationCode?: string;
  vehicleBrand?: string;
  vehicleModel?: string;
  quantity?: number;
  cargoes?: WaybillCargoLine[];
  cargoSummary?: string;
  planIssueTime?: string;
  requiredLoadTime?: string;
  requiredDeliverTime?: string;
  dealerName?: string;
  dealerContact?: string;
  dealerPhone?: string;
  dealerAddress?: string;
  freightAmount?: number;
  freightSource?: number;
  contractId?: number;
  rateId?: number;
  status?: number;
  remark?: string;
  createdBy?: number;
  createdAt?: string;
}

export interface WaybillParam extends PageParam {
  keyword?: string;
  customerId?: number;
  status?: number;
  /** 出发地模糊 */
  originKeyword?: string;
  /** 目的地模糊 */
  destinationKeyword?: string;
  /** 品牌或车型模糊 */
  vehicleKeyword?: string;
}
