import axios from 'axios';

const request = axios.create({
  baseURL: '/api/open',
  timeout: 15000
});

interface ApiResult<T> {
  code: number;
  message?: string;
  data?: T;
}

/** 获取产品版本列表 */
export function getProductVersions() {
  return request.get('/product/versions');
}

/** 获取产品更新记录列表（分页） */
export function getChangelog(params?: { page?: number; page_size?: number }) {
  return request.get('/changelog', { params });
}

export interface LeadPayload {
  company_name: string;
  contact_person: string;
  contact_phone: string;
  fleet_size?: string;
  pain_point?: string;
  /** 自测画像题 P1–P3 */
  profile_answers?: Record<string, string>;
  stage_band?: string;
  stage_name?: string;
  total_score?: number;
  dim_a?: number;
  dim_b?: number;
  dim_c?: number;
  dim_d?: number;
  source_page?: string;
  /** 蜜罐字段，真人不会填 */
  website?: string;
}

/** 提交留资，成功后由顾问跟进 */
export async function submitLead(data: LeadPayload) {
  const res = await request.post<ApiResult<{ accepted: boolean }>>('/lead', data);
  if (res.data.code === 0) {
    return res.data.message || '已收到你的信息，顾问会在 1 个工作日内联系你';
  }
  return Promise.reject(new Error(res.data.message || '提交失败'));
}
