import { get, post } from './request';

export interface TaskListItem {
  id: number;
  taskNo: string;
  taskName?: string;
  status: number;
  origin?: string;
  destination?: string;
  plannedLoadTime?: string;
  plannedArriveTime?: string;
  actualLoadTime?: string;
  actualArriveTime?: string;
  totalQuantity?: number;
  waybillCount?: number;
  customerName?: string;
  mainDriverName?: string;
  plateNumber?: string;
  carrierType?: number;
  prepaidAmount?: number;
  settledAmount?: number;
  carrierCostAmount?: number;
}

export interface TaskSegment {
  id: number;
  segmentNo: number;
  fromLocation?: string;
  toLocation?: string;
  plannedLoadTime?: string;
  plannedArriveTime?: string;
  actualLoadTime?: string;
  actualArriveTime?: string;
  status: number;
  mileage?: number;
}

export interface TaskWaybillItem {
  id: number;
  waybillNo?: string;
  customerName?: string;
  vehicleBrand?: string;
  vehicleModel?: string;
  dealerName?: string;
  quantity: number;
  status: number;
  loadedAt?: string;
  unloadedAt?: string;
  signedAt?: string;
}

export interface TaskDetail extends TaskListItem {
  segments: TaskSegment[];
  items: TaskWaybillItem[];
  remark?: string;
}

export interface TaskListQuery {
  page?: number;
  pageSize?: number;
  status?: number | number[];
  keyword?: string;
}

export interface PageResult<T> {
  list: T[];
  total: number;
  page: number;
  pageSize: number;
}

export function listMyTasks(params: TaskListQuery) {
  return get<PageResult<TaskListItem>>('/task/my', params as Record<string, unknown>);
}

export function getTaskDetail(id: number) {
  return get<TaskDetail>(`/task/${id}`);
}

export function confirmLoad(id: number, payload?: { actualLoadTime?: string; remark?: string }) {
  return post<void>(`/task/${id}/confirm-load`, payload || {});
}

export function depart(id: number, payload?: { remark?: string }) {
  return post<void>(`/task/${id}/depart`, payload || {});
}

export function confirmArrive(id: number, payload?: { actualArriveTime?: string; remark?: string }) {
  return post<void>(`/task/${id}/confirm-arrive`, payload || {});
}

export function signItem(itemId: number, payload?: { signedAt?: string; remark?: string }) {
  return post<void>(`/task/items/${itemId}/sign`, payload || {});
}

export function revertSignItem(itemId: number, payload: { reason: string }) {
  return post<void>(`/task/items/${itemId}/revert-sign`, payload);
}
