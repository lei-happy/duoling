/**
 * 利润总览（老板视角收入成本 BI）- API 客户端
 */
import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type {
  CarrierStructureItem,
  CostStructureItem,
  ProfitCustomerRankItem,
  ProfitCustomerRankParam,
  ProfitDateRangeParam,
  ProfitKpiSummary,
  ProfitTrendParam,
  ProfitTrendPoint
} from './model';

const BASE = '/insight/cockpit/profit';

/** 核心 KPI：收入 / 成本 / 毛利 / 毛利率 */
export async function getProfitKpiSummary(params: ProfitDateRangeParam = {}) {
  const res = await request.get<ApiResult<ProfitKpiSummary>>(
    `${BASE}/kpi-summary`,
    { params }
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 收入 / 成本 / 毛利 / 毛利率趋势 */
export async function getProfitTrend(params: ProfitTrendParam = {}) {
  const res = await request.get<ApiResult<ProfitTrendPoint[]>>(
    `${BASE}/trend`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data || [];
  }
  return Promise.reject(new Error(res.data.message));
}

/** 承运结构（自有 / 承运商 / 社会运力） */
export async function getCarrierStructure(params: ProfitDateRangeParam = {}) {
  const res = await request.get<ApiResult<CarrierStructureItem[]>>(
    `${BASE}/carrier-structure`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data || [];
  }
  return Promise.reject(new Error(res.data.message));
}

/** 成本构成（按费用类型） */
export async function getCostStructure(params: ProfitDateRangeParam = {}) {
  const res = await request.get<ApiResult<CostStructureItem[]>>(
    `${BASE}/cost-structure`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data || [];
  }
  return Promise.reject(new Error(res.data.message));
}

/** 客户毛利排行 */
export async function getProfitCustomerRank(
  params: ProfitCustomerRankParam = {}
) {
  const res = await request.get<ApiResult<ProfitCustomerRankItem[]>>(
    `${BASE}/customer-rank`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data || [];
  }
  return Promise.reject(new Error(res.data.message));
}
