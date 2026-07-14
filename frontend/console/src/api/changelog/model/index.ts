import type { PageParam } from '@/api';

/**
 * 产品更新记录
 */
export interface Changelog {
  id?: number;
  version?: string;
  title?: string;
  content?: string;
  release_date?: string;
  sort_order?: number;
  status?: number;
  /** 租户端是否弹框强提醒 0-否 1-是 */
  is_popup?: number;
  created_at?: string;
  updated_at?: string;
}

/**
 * 更新记录搜索条件
 */
export interface ChangelogParam extends PageParam {
  status?: number;
}
