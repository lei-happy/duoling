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
  created_at?: string;
  updated_at?: string;
}

/**
 * 更新记录搜索条件
 */
export interface ChangelogParam extends PageParam {
  status?: number;
}
