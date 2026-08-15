import type { PageParam } from '@/api';

/** 官网留资线索 */
export interface WebsiteLead {
  id?: number;
  company_name?: string;
  contact_person?: string;
  contact_phone?: string;

  fleet_size?: string | null;
  pain_point?: string | null;
  profile_answers?: Record<string, string> | null;

  stage_band?: string | null;
  stage_name?: string | null;
  total_score?: number | null;
  dim_a?: number | null;
  dim_b?: number | null;
  dim_c?: number | null;
  dim_d?: number | null;

  source_page?: string | null;
  referrer?: string | null;
  client_ip?: string | null;

  status?: number;
  follow_remark?: string | null;
  handler_id?: number | null;
  handler_name?: string | null;
  contacted_at?: string | null;
  converted_tenant_code?: string | null;
  created_at?: string;
  updated_at?: string;
}

/** 搜索条件 */
export interface WebsiteLeadParam extends PageParam {
  status?: number;
  stage_band?: string;
  fleet_size?: string;
  keyword?: string;
  created_from?: string;
  created_to?: string;
}

/** 跟进入参 */
export interface WebsiteLeadFollowParam {
  status: number;
  follow_remark?: string;
  converted_tenant_code?: string;
}
