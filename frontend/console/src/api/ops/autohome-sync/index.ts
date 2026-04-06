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

export async function triggerAutohomeFullSync(body: {
  maxBrands?: number | null;
  delayMs?: number;
  includeInactiveBrands?: boolean;
  incrementalOnly?: boolean;
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
      incrementalOnly: body.incrementalOnly ?? false
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
