import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  SocialCapacityApprovalParam,
  SocialCapacityApprovalStats,
  SocialCapacityApproveBody,
  SocialCapacityRejectBody,
  SocialCapacityDetail,
  SocialCapacityListItem
} from './model';

const BASE = '/capacity/social_capacity/approval';

export async function pageApprovals(params: SocialCapacityApprovalParam) {
  const res = await request.get<ApiResult<PageResult<SocialCapacityListItem>>>(
    BASE,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function approvalStats() {
  const res = await request.get<ApiResult<SocialCapacityApprovalStats>>(
    `${BASE}/stats`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getApprovalDetail(id: number) {
  const res = await request.get<ApiResult<SocialCapacityDetail>>(
    `${BASE}/${id}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function approveSocialCapacity(
  id: number,
  data?: SocialCapacityApproveBody
) {
  const res = await request.post<ApiResult<SocialCapacityDetail>>(
    `${BASE}/${id}/approve`,
    data ?? {}
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function rejectSocialCapacity(
  id: number,
  data: SocialCapacityRejectBody
) {
  const res = await request.post<ApiResult<SocialCapacityDetail>>(
    `${BASE}/${id}/reject`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
