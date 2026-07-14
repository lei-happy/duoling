import type { PageParam } from '@/api';

export type BannerLinkType = 'none' | 'external' | 'internal';
export type BannerTargetType = 'all' | 'version' | 'tenant';
export type BannerStatus = 'draft' | 'published' | 'offline';

/** 推广位 Banner */
export interface Banner {
  id?: number;
  title?: string;
  image_url?: string;
  link_type?: BannerLinkType;
  link_url?: string | null;
  open_in_new_tab?: number;
  target_type?: BannerTargetType;
  target_values?: string[] | null;
  sort_order?: number;
  status?: BannerStatus;
  start_at?: string | null;
  end_at?: string | null;
  remark?: string | null;
  created_by?: number;
  created_at?: string;
  updated_at?: string;
}

/** Banner 搜索条件 */
export interface BannerParam extends PageParam {
  keyword?: string;
  status?: BannerStatus;
  target_type?: BannerTargetType;
}

export interface BannerOption {
  value: string;
  label: string;
}

export interface BannerStatsSummary {
  view_pv: number;
  view_uv: number;
  click_pv: number;
  click_uv: number;
  ctr: number;
}

export interface BannerTenantStat {
  tenant_code: string;
  tenant_name?: string | null;
  view_pv: number;
  view_uv: number;
  click_pv: number;
  click_uv: number;
}

export interface BannerStats {
  summary: BannerStatsSummary;
  by_tenant: BannerTenantStat[];
}

export interface BannerEvent {
  id: number;
  tenant_code: string;
  tenant_name?: string | null;
  user_id: number;
  user_phone?: string | null;
  event_type: 'view' | 'click';
  occurred_at: string;
}
