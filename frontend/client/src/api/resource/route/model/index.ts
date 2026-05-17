import type { PageParam } from '@/api';

export interface Route {
  id?: number;
  routeName?: string;
  routeCode?: string;
  origin?: string;
  destination?: string;
  originRegionId?: number;
  destinationRegionId?: number;
  originCode?: string;
  destinationCode?: string;
  distance?: number;
  estimatedHours?: number;
  waypoints?: string;
  status?: number;
  remark?: string;
  createdAt?: string;
}

export interface RouteParam extends PageParam {
  /** 起点展示名模糊筛选 */
  originKeyword?: string;
  /** 终点展示名模糊筛选 */
  destinationKeyword?: string;
  status?: number;
  createdAtStart?: string;
  createdAtEnd?: string;
}
