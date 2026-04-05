/**
 * 地区数据类型定义（平台库 sys_regions）
 */

export interface Region {
  code?: number;
  name?: string;
  shortName?: string;
  pcode?: number | null;
  level?: number;
  sortOrder?: number;
  status?: number;
  createTime?: string;
  hasChildren?: boolean;
}

export interface RegionNavNode {
  code: number;
  name: string;
  pcode?: number | null;
  level: number;
  childCount: number;
  children?: RegionNavNode[];
}

export interface RegionParam {
  pcode?: number;
  name?: string;
  status?: number;
  page?: number;
  limit?: number;
}
