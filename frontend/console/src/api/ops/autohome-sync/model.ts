export interface AutohomeSyncJob {
  jobId: number;
  jobType: string;
  status: string;
  progressPct: number;
  payloadJson?: string | null;
  logText?: string | null;
  errorMessage?: string | null;
  createTime?: string | null;
  lastUpdateTime?: string | null;
}
