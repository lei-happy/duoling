import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type {
  AuditTenantProfile,
  WhitelistMember,
  WhitelistParam,
  WhitelistResult
} from '@/api/ecosystem/audit/model';

const BASE = '/ecosystem/audit-whitelist';

interface MemberPageResult {
  list: WhitelistMember[];
  count: number;
  total: number;
  page: number;
  pageSize: number;
}

/** 白名单成员列表 */
export async function pageWhitelist(params: WhitelistParam) {
  const res = await request.get<ApiResult<MemberPageResult>>(BASE, { params });
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 资格判定 + 该企业在服务平台的完整档案 */
export async function getTenantProfile(tenantCode: string) {
  const res = await request.get<ApiResult<AuditTenantProfile>>(
    `${BASE}/${encodeURIComponent(tenantCode)}/eligibility`
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 人工授予免审 */
export async function grantWhitelist(tenantCode: string) {
  const res = await request.post<ApiResult<WhitelistResult>>(BASE, {
    tenantCode
  });
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 移出免审，原因必填（同时作为冷静期起点） */
export async function revokeWhitelist(tenantCode: string, reason: string) {
  const res = await request.post<ApiResult<WhitelistResult>>(
    `${BASE}/${encodeURIComponent(tenantCode)}/revoke`,
    { reason }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
