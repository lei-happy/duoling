import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { DealerSyncJob } from './model';

export async function pageDealerSyncJobs(params: {
  page?: number;
  limit?: number;
}) {
  const res = await request.get<
    ApiResult<{ list: DealerSyncJob[]; count: number }>
  >('/ops/dealer-sync', { params });
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 固定增量模式 */
export async function triggerDealerSync(body: {
  maxCities?: number | null;
  delayMs?: number;
}) {
  const res = await request.post<ApiResult<{ jobId: number }>>(
    '/ops/dealer-sync/trigger',
    {
      maxCities:
        body.maxCities != null && body.maxCities > 0
          ? body.maxCities
          : undefined,
      delayMs: body.delayMs ?? 400
    }
  );
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getDealerSyncJob(jobId: number) {
  const res = await request.get<ApiResult<DealerSyncJob>>(
    `/ops/dealer-sync/${jobId}`
  );
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}
