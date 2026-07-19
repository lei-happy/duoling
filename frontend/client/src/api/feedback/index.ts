import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type {
  Feedback,
  FeedbackCreateParam,
  FeedbackParam
} from './model';

interface FeedbackPageResult {
  list: Feedback[];
  total: number;
  page: number;
  limit: number;
}

/** 提交意见反馈 */
export async function createFeedback(data: FeedbackCreateParam) {
  const res = await request.post<ApiResult<Feedback>>('/feedback', data);
  if (res.data.code === 0) {
    return res.data;
  }
  return Promise.reject(new Error(res.data.message || '提交失败，请稍后重试'));
}

/** 分页查询我的反馈 */
export async function pageFeedbacks(params: FeedbackParam) {
  const res = await request.get<ApiResult<FeedbackPageResult>>('/feedback', {
    params: {
      page: params.page,
      limit: params.limit,
      status: params.status,
      feedback_type: params.feedback_type,
      keyword: params.keyword,
      created_from: params.created_from,
      created_to: params.created_to
    }
  });
  if (res.data.code === 0 && res.data.data) {
    const d = res.data.data;
    return { list: d.list, count: d.total };
  }
  return Promise.reject(new Error(res.data.message || '加载失败，请重试'));
}

/** 反馈详情 */
export async function getFeedback(id: number) {
  const res = await request.get<ApiResult<Feedback>>(`/feedback/${id}`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message || '加载失败，请重试'));
}
