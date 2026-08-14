import request from '@/utils/request';
import { download } from '@/utils/common';
import type { ApiResult } from '@/api';
import type {
  AccountingKpi,
  DimensionRow,
  DrillDownResult,
  InterEntityResult
} from './model';

const BASE = '/finance/profit';

export async function getAccountingKpi(params: {
  period?: string;
  enterpriseId?: number;
  taxMode?: string;
}) {
  const res = await request.get<ApiResult<AccountingKpi>>(`${BASE}/kpi`, {
    params
  });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listAccountingByDimension(params: {
  dimension: string;
  period?: string;
  enterpriseId?: number;
  taxMode?: string;
}) {
  const res = await request.get<
    ApiResult<{ list: DimensionRow[]; count: number }>
  >(`${BASE}/by-dimension`, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function drillDownAccounting(params: {
  dimension: string;
  dimensionValue: string;
  period?: string;
  enterpriseId?: number;
}) {
  const res = await request.get<ApiResult<DrillDownResult>>(
    `${BASE}/drill-down`,
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getInterEntityTransfer(params: { period?: string }) {
  const res = await request.get<ApiResult<InterEntityResult>>(
    `${BASE}/inter-entity`,
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function exportAccountingWorksheet(params: {
  period?: string;
  enterpriseId?: number;
}): Promise<void> {
  const res = await request.get(`${BASE}/export`, {
    params,
    responseType: 'blob'
  });
  const blob = res.data as Blob;
  if (
    blob.type?.includes('application/json') ||
    blob.type?.includes('text/json')
  ) {
    const text = await blob.text();
    let msg = '导出失败，请稍后重试';
    try {
      const j = JSON.parse(text) as { message?: string };
      msg = j.message || msg;
    } catch {
      // 非 JSON 说明不是业务错误，沿用默认文案
    }
    throw new Error(msg);
  }
  const buf = await blob.arrayBuffer();
  const stamp = params.period || new Date().toISOString().slice(0, 7);
  download(buf, `经营核算底稿-${stamp}.xlsx`);
}
