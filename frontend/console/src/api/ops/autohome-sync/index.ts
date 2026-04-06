import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { AutohomeSyncJob } from './model';

export async function pageAutohomeSyncJobs(params: {
  page?: number;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: AutohomeSyncJob[]; count: number }>
  >('/ops/autohome-sync', { params });
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function triggerAutohomeProbe(body: {
  autohomeSeriesId?: number;
}) {
  const res = await request.post<ApiResult<{ jobId: number }>>(
    '/ops/autohome-sync/trigger',
    {
      jobType: 'probe',
      autohomeSeriesId: body.autohomeSeriesId ?? 4851
    }
  );
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 固定增量模式，避免误触全量导致已有 Logo/车系图路径被 UUID 覆盖。 */
export async function triggerAutohomeFullSync(body: {
  maxBrands?: number | null;
  delayMs?: number;
  includeInactiveBrands?: boolean;
}) {
  const res = await request.post<ApiResult<{ jobId: number }>>(
    '/ops/autohome-sync/trigger',
    {
      jobType: 'full',
      maxBrands:
        body.maxBrands != null && body.maxBrands > 0
          ? body.maxBrands
          : undefined,
      delayMs: body.delayMs ?? 400,
      includeInactiveBrands: body.includeInactiveBrands ?? false,
      incrementalOnly: true
    }
  );
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getAutohomeSyncJob(jobId: number) {
  const res = await request.get<ApiResult<AutohomeSyncJob>>(
    `/ops/autohome-sync/${jobId}`
  );
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}
