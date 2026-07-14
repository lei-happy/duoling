import request from '@/utils/request';
import type { ApiResult } from '@/api';

export type WorkbenchBanner = {
  id: number;
  image_url: string;
  title: string;
  /** none-只看不跳 external-外链 internal-站内路由 */
  link_type: 'none' | 'external' | 'internal';
  link_url?: string | null;
  open_in_new_tab: number;
};

type BannerListData = {
  items: WorkbenchBanner[];
};

/** 当前用户可见的推广位 Banner 列表 */
export async function getWorkbenchBanners() {
  const res = await request.get<ApiResult<BannerListData>>('/workbench/banner');
  if (res.data.code === 0 && res.data.data) {
    return res.data.data.items || [];
  }
  return Promise.reject(new Error(res.data.message || '请求失败'));
}

/** 上报 Banner 曝光/点击埋点（best-effort） */
export async function reportBannerEvent(
  bannerId: number,
  eventType: 'view' | 'click'
) {
  return request.post<ApiResult<unknown>>('/workbench/banner/event', {
    banner_id: bannerId,
    event_type: eventType
  });
}
