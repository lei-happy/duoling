import type { PageParam } from '@/api';

/** 证照到期预警 */
export interface ComplianceAlert {
  id?: number;
  subjectType?: string;
  subjectTypeLabel?: string;
  subjectId?: number;
  subjectName?: string;
  subjectRef?: string;
  docType?: string;
  docTypeLabel?: string;
  docNo?: string;
  expireDate?: string;
  daysLeft?: number;
  level?: string;
  status?: string;
  dismissedUserId?: number;
  dismissedAt?: string;
  firstAlertedAt?: string;
  lastScanAt?: string;
}

export interface ComplianceAlertParam extends PageParam {
  subjectType?: string;
  docType?: string;
  level?: string;
  status?: string;
  keyword?: string;
}

/** 合规看板汇总 */
export interface ComplianceSummary {
  total: number;
  expired: number;
  critical: number;
  warning: number;
  bySubjectType: Record<string, number>;
  byDocType: Record<string, number>;
}
