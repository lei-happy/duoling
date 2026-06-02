export interface RegionSyncJob {
  jobId: number;
  status: string;
  progressPct: number;
  payloadJson?: string | null;
  logText?: string | null;
  errorMessage?: string | null;
  totalCount?: number | null;
  createTime?: string | null;
  lastUpdateTime?: string | null;
}
