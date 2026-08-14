import request from '@/utils/request';
import { download } from '@/utils/common';
import type { ApiResult } from '@/api';
import type {
  AgingDetailResult,
  AgingPageResult,
  AgingParam,
  AgingSummary,
  CustomerCreditBrief
} from './model';

const BASE = '/finance/ar-aging';

export async function pageAging(params: AgingParam) {
  const res = await request.get<ApiResult<AgingPageResult>>(BASE, { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getAgingSummary(params: {
  enterpriseId?: number;
  creditStatus?: number;
  keyword?: string;
  baseDate?: string;
}) {
  const res = await request.get<ApiResult<AgingSummary>>(`${BASE}/summary`, {
    params
  });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getAgingDetail(params: {
  customerId: number;
  bucket?: number;
  baseDate?: string;
}) {
  const res = await request.get<ApiResult<AgingDetailResult>>(
    `${BASE}/detail`,
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/**
 * 单客户预警摘要。业务页面（运单录入、派车、对账确认、结算提交）传 scene，
 * 表示提示确实展示给人看了，高危等级会在后端留痕。
 */
export async function getCustomerCreditBrief(
  customerId: number,
  scene?: 'waybill_create' | 'task_dispatch' | 'recon_confirm' | 'settle_submit'
) {
  const res = await request.get<ApiResult<CustomerCreditBrief>>(
    `${BASE}/customer-brief`,
    { params: { customerId, scene } }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

/** 导出客户汇总 + 结算单明细两张表页 */
export async function exportAging(params: {
  enterpriseId?: number;
  creditStatus?: number;
  keyword?: string;
  bucket?: number;
  baseDate?: string;
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
  const stamp = params.baseDate || new Date().toISOString().slice(0, 10);
  download(buf, `应收账龄-${stamp}.xlsx`);
}
