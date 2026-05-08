import request from '@/utils/request';
import type { ApiResult, PageResult, PageParam } from '@/api';

export interface CarrierInboundLink {
  id: number;
  sourceTenantCode: string;
  sourceTenantName?: string | null;
  sourceTenantShortName?: string | null;
  sourceContactPerson?: string | null;
  sourceContactPhone?: string | null;
  sourceProvince?: string | null;
  sourceCity?: string | null;
  sourceAddress?: string | null;
  sourceCarrierId: number;
  sourceCarrierName: string;
  cooperationStart?: string | null;
  linkStatus: number;
  createdAt: string;
}

export interface CarrierInboundParam extends PageParam {
  keyword?: string;
  linkStatus?: number;
}

const BASE = '/partner/inbound';

export async function pageInbound(params: CarrierInboundParam) {
  const res = await request.get<ApiResult<PageResult<CarrierInboundLink>>>(
    BASE,
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export const INBOUND_STATUS_TEXT: Record<number, string> = {
  1: '已互联',
  2: 'A 端已删除',
  3: 'B 端已退出'
};
