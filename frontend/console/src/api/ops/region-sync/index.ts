import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { RegionSyncJob } from './model';

export async function pageRegionSyncJobs(params: {
  page?: number;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: RegionSyncJob[]; count: number }>
  >('/ops/region-sync', { params });
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function triggerRegionSync(body?: {
  maxConcurrent?: number;
  requestDelayMs?: number;
}) {
  const res = await request.post<ApiResult<{ jobId: number }>>(
    '/ops/region-sync/trigger',
    body ?? {}
  );
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getRegionSyncJob(jobId: number) {
  const res = await request.get<ApiResult<RegionSyncJob>>(
    `/ops/region-sync/${jobId}`
  );
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}
