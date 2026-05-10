import request from '@/utils/request';
import type { ApiResult } from '@/api';

function assertOk<T>(res: { data: ApiResult<T> }) {
  if (res.data.code !== 0) {
    return Promise.reject(new Error(res.data.message || '请求失败'));
  }
  return res;
}

export type CompanyActivityItem = {
  id: number;
  occurred_at: string;
  display_time: string;
  summary: string;
  event_code: string;
  /** 操作人展示名，与摘要配合高亮 */
  actor_display_name?: string | null;
};

export type CompanyActivityListData = {
  items: CompanyActivityItem[];
};

/** 当日企业动态列表 */
export async function getCompanyActivities(params?: { limit?: number }) {
  const res = await request.get<ApiResult<CompanyActivityListData>>(
    '/workbench/activities',
    { params }
  );
  return assertOk(res);
}

/** 开发环境：写入演示数据（当日若已有数据则跳过） */
export async function seedDemoActivities() {
  const res = await request.post<ApiResult<{ inserted: number }>>(
    '/workbench/activities/demo-seed'
  );
  return assertOk(res);
}
