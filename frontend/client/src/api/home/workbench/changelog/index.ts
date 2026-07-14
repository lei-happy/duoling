import request from '@/utils/request';
import type { ApiResult } from '@/api';

/** 版本升级说明（租户端展示字段） */
export type WorkbenchChangelog = {
  id: number;
  version: string;
  title: string;
  content?: string | null;
  release_date: string;
  /** 是否弹框强提醒 0-否 1-是 */
  is_popup: number;
};

type ChangelogListData = {
  list: WorkbenchChangelog[];
  total: number;
  page: number;
  limit: number;
};

type ChangelogPopupData = {
  items: WorkbenchChangelog[];
};

/** 已发布的版本升级说明列表（供查看历史更新） */
export async function getWorkbenchChangelogs(params?: {
  page?: number;
  limit?: number;
}) {
  const res = await request.get<ApiResult<ChangelogListData>>(
    '/workbench/changelog',
    { params: { page: params?.page ?? 1, limit: params?.limit ?? 20 } }
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message || '请求失败'));
}

/** 当前用户尚未读过、需要强制弹框的版本升级说明 */
export async function getWorkbenchChangelogPopups() {
  const res = await request.get<ApiResult<ChangelogPopupData>>(
    '/workbench/changelog/popup'
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data.items || [];
  }
  return Promise.reject(new Error(res.data.message || '请求失败'));
}

/** 标记版本升级说明为已读（下次不再强制弹框，best-effort） */
export async function markWorkbenchChangelogsRead(changelogIds: number[]) {
  return request.post<ApiResult<unknown>>('/workbench/changelog/read', {
    changelog_ids: changelogIds
  });
}
