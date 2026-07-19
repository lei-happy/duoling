import type { PageParam } from '@/api';

/** 意见反馈 */
export interface Feedback {
  id?: number;
  tenant_code?: string | null;
  tenant_name?: string | null;
  user_id?: number;
  user_name?: string | null;
  contact_phone?: string | null;
  title?: string;
  content?: string;
  feedback_type?: number;
  status?: number;
  reply?: string | null;
  images?: string[];
  handler_id?: number | null;
  handler_name?: string | null;
  replied_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

/** 搜索条件 */
export interface FeedbackParam extends PageParam {
  status?: number;
  feedback_type?: number;
  tenant_code?: string;
  keyword?: string;
  created_from?: string;
  created_to?: string;
}

/** 处理入参 */
export interface FeedbackHandleParam {
  status: number;
  reply?: string;
}
