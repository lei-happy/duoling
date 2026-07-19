import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { Feedback, FeedbackHandleParam, FeedbackParam } from './model';

interface FeedbackPageResult {
  list: Feedback[];
  total: number;
  page: number;
  limit: number;
}

/** 分页查询意见反馈 */
export async function pageFeedbacks(params: FeedbackParam) {
  const res = await request.get<ApiResult<FeedbackPageResult>>('/feedback', {
    params: {
      page: params.page,
      limit: params.limit,
      status: params.status,
      feedback_type: params.feedback_type,
      tenant_code: params.tenant_code,
      keyword: params.keyword,
      created_from: params.created_from,
      created_to: params.created_to
    }
  });
  if (res.data.code === 0 && res.data.data) {
    const d = res.data.data;
    return { list: d.list, count: d.total };
  }
  return Promise.reject(new Error(res.data.message));
}

/** 获取反馈详情 */
export async function getFeedback(id: number) {
  const res = await request.get<ApiResult<Feedback>>(`/feedback/${id}`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 处理反馈 */
export async function handleFeedback(id: number, data: FeedbackHandleParam) {
  const res = await request.put<ApiResult<Feedback>>(
    `/feedback/${id}/handle`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message || '已更新处理结果';
  }
  return Promise.reject(new Error(res.data.message));
}
