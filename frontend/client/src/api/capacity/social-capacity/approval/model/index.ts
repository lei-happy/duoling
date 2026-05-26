import type { PageParam } from '@/api';

export type {
  SocialCapacityListItem,
  SocialCapacityDetail,
  SocialCapacityAudit
} from '../../list/model';

export interface SocialCapacityApprovalParam extends PageParam {
  keyword?: string;
  approvalStatus?: number;
}

export interface SocialCapacityApproveBody {
  remark?: string;
}

export interface SocialCapacityRejectBody {
  remark: string;
}

export interface SocialCapacityApprovalStats {
  pendingCount: number;
  approvedCount: number;
  rejectedCount: number;
  totalCount: number;
}
