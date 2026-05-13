import request from '@/utils/request';
import type { ApiResult, PageParam, PageResult } from '@/api';

// ============== 异常中心 ==============

export interface FreightCalcException {
  id: number;
  waybillId?: number | null;
  waybillCargoId?: number | null;
  batchId?: number | null;
  importRowId?: number | null;
  exceptionType: string;
  exceptionMessage: string;
  contextJson?: Record<string, unknown> | null;
  status: string;
  processedBy?: number | null;
  processedAt?: string | null;
  processRemark?: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ExceptionPageParam extends PageParam {
  status?: string;
  exceptionType?: string;
  waybillId?: number;
  batchId?: number;
}

export async function pageExceptions(params: ExceptionPageParam) {
  const res = await request.get<ApiResult<PageResult<FreightCalcException>>>(
    '/billing/freight-calc/exceptions',
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export interface ExceptionStats {
  pendingByType: Record<string, number>;
  byStatus: Record<string, number>;
}

export async function statsExceptions() {
  const res = await request.get<ApiResult<ExceptionStats>>(
    '/billing/freight-calc/exceptions/stats'
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function resolveException(id: number, remark?: string) {
  const res = await request.post<ApiResult<unknown>>(
    `/billing/freight-calc/exceptions/${id}/resolve`,
    { remark }
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function ignoreException(id: number, remark?: string) {
  const res = await request.post<ApiResult<unknown>>(
    `/billing/freight-calc/exceptions/${id}/ignore`,
    { remark }
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function batchRecalcExceptions(exceptionIds: number[]) {
  const res = await request.post<ApiResult<{
    recalcCount: number;
    waybillCount: number;
  }>>(
    '/billing/freight-calc/exceptions/batch-recalc',
    { exceptionIds }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

// ============== 任务 ==============

export interface FreightCalcTask {
  id: number;
  taskType: string;
  targetType: string;
  targetId: number;
  waybillId?: number | null;
  status: string;
  priority: number;
  retryCount: number;
  maxRetryCount: number;
  errorMessage?: string | null;
  triggeredByUserId?: number | null;
  startedAt?: string | null;
  finishedAt?: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface TaskPageParam extends PageParam {
  status?: string;
  taskType?: string;
  waybillId?: number;
}

export async function pageTasks(params: TaskPageParam) {
  const res = await request.get<ApiResult<PageResult<FreightCalcTask>>>(
    '/billing/freight-calc/tasks',
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function retryTask(id: number) {
  const res = await request.post<ApiResult<unknown>>(
    `/billing/freight-calc/tasks/${id}/retry`
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

// ============== 别名 ==============

export interface RegionAlias {
  id: number;
  aliasName: string;
  regionId: number;
  status: number;
  createdAt: string;
}

export async function pageRegionAlias(
  params: PageParam & { keyword?: string }
) {
  const res = await request.get<ApiResult<PageResult<RegionAlias>>>(
    '/basic-data/region-alias',
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function upsertRegionAlias(aliasName: string, regionId: number) {
  const res = await request.post<ApiResult<{ id: number }>>(
    '/basic-data/region-alias',
    { aliasName, regionId }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function deleteRegionAlias(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/basic-data/region-alias/${id}`
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export interface VehicleAlias {
  id: number;
  aliasName: string;
  aliasKind: 'brand' | 'series';
  brandId?: number | null;
  seriesId?: number | null;
  status: number;
  createdAt: string;
}

export async function pageVehicleAlias(
  params: PageParam & { keyword?: string; kind?: string }
) {
  const res = await request.get<ApiResult<PageResult<VehicleAlias>>>(
    '/basic-data/vehicle-alias',
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export interface VehicleAliasUpsert {
  aliasKind: 'brand' | 'series';
  rawBrand?: string | null;
  rawModel?: string | null;
  brandId?: number | null;
  seriesId?: number | null;
}

export async function upsertVehicleAlias(payload: VehicleAliasUpsert) {
  const res = await request.post<ApiResult<{ id: number }>>(
    '/basic-data/vehicle-alias',
    payload
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function deleteVehicleAlias(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/basic-data/vehicle-alias/${id}`
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}
