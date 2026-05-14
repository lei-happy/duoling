/**
 * 经营驾驶舱 BI 看板 - API 客户端
 */
import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type {
  CockpitDateRangeParam,
  CustomerRankItem,
  CustomerRankParam,
  CustomerTypeDistItem,
  KpiSummary,
  OperationEfficiency,
  RegionRankItem,
  RegionRankParam,
  RevenueTrendParam,
  RevenueTrendPoint,
  VehicleBrandRankItem,
  VehicleBrandRankParam
} from './model';

const BASE = '/insight/cockpit';

/** 核心 KPI（含环比与 sparkline） */
export async function getKpiSummary(params: CockpitDateRangeParam = {}) {
  const res = await request.get<ApiResult<KpiSummary>>(`${BASE}/kpi-summary`, {
    params
  });
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 收入与单量趋势 */
export async function getRevenueTrend(params: RevenueTrendParam = {}) {
  const res = await request.get<ApiResult<RevenueTrendPoint[]>>(
    `${BASE}/revenue-trend`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data || [];
  }
  return Promise.reject(new Error(res.data.message));
}

/** TopN 客户运费贡献 */
export async function getCustomerRank(params: CustomerRankParam = {}) {
  const res = await request.get<ApiResult<CustomerRankItem[]>>(
    `${BASE}/customer-rank`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data || [];
  }
  return Promise.reject(new Error(res.data.message));
}

/** 客户类型分布 */
export async function getCustomerTypeDist(params: CockpitDateRangeParam = {}) {
  const res = await request.get<ApiResult<CustomerTypeDistItem[]>>(
    `${BASE}/customer-type-dist`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data || [];
  }
  return Promise.reject(new Error(res.data.message));
}

/** 起讫地排行（type: origin | destination） */
export async function getRegionRank(params: RegionRankParam = {}) {
  const res = await request.get<ApiResult<RegionRankItem[]>>(
    `${BASE}/region-rank`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data || [];
  }
  return Promise.reject(new Error(res.data.message));
}

/** 商品车品牌排行 */
export async function getVehicleBrandRank(params: VehicleBrandRankParam = {}) {
  const res = await request.get<ApiResult<VehicleBrandRankItem[]>>(
    `${BASE}/vehicle-brand-rank`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data || [];
  }
  return Promise.reject(new Error(res.data.message));
}

/** 运营效率（状态分布 + 异常率） */
export async function getOperationEfficiency(
  params: CockpitDateRangeParam = {}
) {
  const res = await request.get<ApiResult<OperationEfficiency>>(
    `${BASE}/operation-efficiency`,
    { params }
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
