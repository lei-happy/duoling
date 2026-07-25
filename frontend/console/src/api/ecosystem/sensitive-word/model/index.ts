/** 敏感词 */
export interface SensitiveWord {
  id: number;
  word: string;
  /** 1-政治 2-色情低俗 3-违禁品 4-竞品导流 5-诈骗 9-其他 */
  category: number;
  /** 1-禁止发布 2-转人工审核 */
  action: number;
  /** all-全平台 ecosystem-货源/运力大厅 */
  scope: string;
  /** 0-停用 1-启用 */
  status: number;
  hitCount: number;
  lastHitAt?: string | null;
  remark?: string | null;
  createdAt?: string | null;
  updatedAt?: string | null;
}

/** 分页查询参数 */
export interface SensitiveWordParam {
  page?: number;
  limit?: number;
  keyword?: string;
  category?: number;
  action?: number;
  scope?: string;
  status?: number;
}

/** 新增 / 修改入参 */
export interface SensitiveWordSave {
  id?: number;
  word?: string;
  category?: number;
  action?: number;
  scope?: string;
  status?: number;
  remark?: string | null;
}

/** 下拉选项（由后端下发，避免前后端取值漂移） */
export interface WordOption {
  value: number | string;
  label: string;
  desc?: string;
}

export interface SensitiveWordOptions {
  categories: WordOption[];
  actions: WordOption[];
  scopes: WordOption[];
}

/** 批量导入结果 */
export interface ImportResult {
  added: number;
  revived: number;
  skipped: number;
}

/** 试测结果 */
export interface WordTestResult {
  blocked: boolean;
  contactHits: string[];
  wordHits: { word: string; category: number; action: number }[];
}
