import type { PageParam } from '@/api';

export interface Route {
  id?: number;
  routeName?: string;
  routeCode?: string;
  origin?: string;
  destination?: string;
  distance?: number;
  estimatedHours?: number;
  waypoints?: string;
  status?: number;
  remark?: string;
  createdAt?: string;
}

export interface RouteParam extends PageParam {
  keyword?: string;
  status?: number;
}
