import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type {
  WebsiteLead,
  WebsiteLeadFollowParam,
  WebsiteLeadParam
} from './model';

interface WebsiteLeadPageResult {
  list: WebsiteLead[];
  total: number;
  page: number;
  limit: number;
}

/** 分页查询官网线索 */
export async function pageWebsiteLeads(params: WebsiteLeadParam) {
  const res = await request.get<ApiResult<WebsiteLeadPageResult>>(
    '/website-lead',
    {
      params: {
        page: params.page,
        limit: params.limit,
        status: params.status,
        stage_band: params.stage_band,
        fleet_size: params.fleet_size,
        keyword: params.keyword,
        created_from: params.created_from,
        created_to: params.created_to
      }
    }
  );
  if (res.data.code === 0 && res.data.data) {
    const d = res.data.data;
    return { list: d.list, count: d.total };
  }
  return Promise.reject(new Error(res.data.message));
}

/** 获取线索详情 */
export async function getWebsiteLead(id: number) {
  const res = await request.get<ApiResult<WebsiteLead>>(`/website-lead/${id}`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 更新跟进状态 */
export async function followWebsiteLead(
  id: number,
  data: WebsiteLeadFollowParam
) {
  const res = await request.put<ApiResult<WebsiteLead>>(
    `/website-lead/${id}/follow`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message || '已更新跟进记录';
  }
  return Promise.reject(new Error(res.data.message));
}
