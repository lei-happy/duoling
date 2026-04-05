/**
 * 地区数据类型定义
 */

export interface Region {
  regionId?: number;
  code?: string;
  name?: string;
  parentCode?: string | null;
  level?: number;
  sortOrder?: number;
  status?: number;
  source?: number;
  createdBy?: number | null;
  createTime?: string;
  hasChildren?: boolean;
  longitude?: number | null;
  latitude?: number | null;
}

export interface RegionNavNode {
  regionId: number;
  code: string;
  name: string;
  parentCode?: string | null;
  level: number;
  childCount: number;
  children?: RegionNavNode[];
}

export interface RegionParam {
  parentCode?: string;
  name?: string;
  source?: number;
  page?: number;
  limit?: number;
}
