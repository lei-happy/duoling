import type { PageParam } from '@/api';

/** 意见反馈 */
export interface Feedback {
  id?: number;
  tenant_code?: string | null;
  user_id?: number;
  user_name?: string | null;
  contact_phone?: string | null;
  title?: string;
  content?: string;
  feedback_type?: number;
  status?: number;
  reply?: string | null;
  images?: string[];
  handler_name?: string | null;
  replied_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

/** 提交反馈（title 可选，缺省由服务端按正文生成） */
export interface FeedbackCreateParam {
  feedback_type: number;
  title?: string;
  content: string;
  images?: string[];
  contact_phone?: string;
}

/** 列表查询 */
export interface FeedbackParam extends PageParam {
  status?: number;
  feedback_type?: number;
  keyword?: string;
  created_from?: string;
  created_to?: string;
}
