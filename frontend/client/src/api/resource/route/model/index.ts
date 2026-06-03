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
  /** 已保存的路线折线 [[lng, lat], ...] */
  polylinePath?: number[][];
  routePolyline?: number[][];
  clearRoutePolyline?: boolean;
  status?: number;
  remark?: string;
  createdAt?: string;
}

export interface RouteRegionPoint {
  regionId: number;
  name: string;
  longitude: number;
  latitude: number;
}

export interface RouteDrivingMetrics {
  distanceKm: number;
  estimatedHours: number;
  origin: RouteRegionPoint;
  destination: RouteRegionPoint;
  /** 路线折线 [[lng, lat], ...] */
  polylinePath?: number[][];
  /** 驾车算路策略，默认 34 高速优先 */
  strategy?: number;
  source?: string;
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
