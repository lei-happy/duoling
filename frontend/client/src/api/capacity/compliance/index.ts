import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  ComplianceAlert,
  ComplianceAlertParam,
  ComplianceSummary
} from './model';

const BASE = '/capacity/compliance/alerts';

/** 分页查询证照到期预警 */
export async function pageComplianceAlerts(params: ComplianceAlertParam) {
  const res = await request.get<ApiResult<PageResult<ComplianceAlert>>>(BASE, {
    params
  });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 合规看板汇总 */
export async function getComplianceSummary() {
  const res = await request.get<ApiResult<ComplianceSummary>>(
    `${BASE}/summary`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 忽略一条预警 */
export async function dismissComplianceAlert(id: number) {
  const res = await request.put<ApiResult<ComplianceAlert>>(
    `${BASE}/${id}/dismiss`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
