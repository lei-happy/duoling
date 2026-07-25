import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type {
  AuditBacklog,
  AuditBatchResult,
  AuditDetail,
  AuditActionResult,
  AuditOptions,
  AuditPostParam,
  AuditQueueRow
} from './model';

const BASE = '/ecosystem/posts';

interface QueuePageResult {
  list: AuditQueueRow[];
  count: number;
  total: number;
  page: number;
  pageSize: number;
}

/**
 * 拼查询串
 *
 * 不能直接用 `request.get(url, { params })`：请求工具把数组序列化成
 * `statuses[0]=1`，而后端收的是可重复的 `statuses=1&statuses=2`，
 * 参数会被静默丢掉——筛了状态却没生效，界面上完全看不出来。
 */
function toQuery(params: Record<string, any>) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === void 0 || value === null || value === '') {
      return;
    }
    if (Array.isArray(value)) {
      value.forEach((item) => search.append(key, String(item)));
    } else {
      search.append(key, String(value));
    }
  });
  return search.toString();
}

async function pageQueue(path: string, params: AuditPostParam) {
  const query = toQuery(params);
  const res = await request.get<ApiResult<QueuePageResult>>(
    query ? `${path}?${query}` : path
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 待人工审核队列（按进队时间正序） */
export function pagePendingPosts(params: AuditPostParam) {
  return pageQueue(`${BASE}/pending`, params);
}

/** 免审直通待抽检队列（按上架时间正序） */
export function pageSpotCheckPosts(params: AuditPostParam) {
  return pageQueue(`${BASE}/spot-check`, params);
}

/** 全量检索（按进队时间倒序） */
export function pageAllPosts(params: AuditPostParam) {
  return pageQueue(BASE, params);
}

/** 下拉元数据：驳回原因、状态、类型、预检标记 */
export async function getAuditOptions() {
  const res = await request.get<ApiResult<AuditOptions>>(`${BASE}/options`);
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 积压统计 */
export async function getAuditBacklog() {
  const res = await request.get<ApiResult<AuditBacklog>>(`${BASE}/backlog`);
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 审核详情：挂牌全字段 + 预检 + 源单核验 + 发布方档案 + 流水 + 资格 */
export async function getAuditDetail(postId: number) {
  const res = await request.get<ApiResult<AuditDetail>>(`${BASE}/${postId}`);
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

async function doAction(path: string, data?: Record<string, any>) {
  const res = await request.post<ApiResult<AuditActionResult>>(
    path,
    data ?? {}
  );
  if (res.data.code === 0) {
    return {
      result: res.data.data as AuditActionResult,
      message: res.data.message
    };
  }
  return Promise.reject(new Error(res.data.message));
}

/** 审核通过 */
export function approvePost(postId: number, remark?: string) {
  return doAction(`${BASE}/${postId}/approve`, { remark });
}

/** 驳回。reason 留空时套用原因模板 */
export function rejectPost(
  postId: number,
  data: { reasonCode: number; reason?: string }
) {
  return doAction(`${BASE}/${postId}/reject`, data);
}

/** 强制下架 */
export function forceDelistPost(
  postId: number,
  data: { reason: string; reasonCode?: number; revokeWhitelist?: boolean }
) {
  return doAction(`${BASE}/${postId}/force-delist`, data);
}

/** 抽检通过：只改审核状态，租户端无感知 */
export function spotCheckPass(postId: number, remark?: string) {
  return doAction(`${BASE}/${postId}/spot-check-pass`, { remark });
}

/** 抽检不通过：下架 + 移出免审白名单 */
export function spotCheckFail(
  postId: number,
  data: { reason: string; reasonCode?: number }
) {
  return doAction(`${BASE}/${postId}/spot-check-fail`, data);
}

/** 批量通过。部分失败仍是成功响应，按 failed 是否为空区分提示 */
export async function batchApprovePosts(postIds: number[]) {
  const res = await request.post<ApiResult<AuditBatchResult>>(
    `${BASE}/batch-approve`,
    { postIds }
  );
  if (res.data.code === 0) {
    return {
      result: res.data.data as AuditBatchResult,
      message: res.data.message
    };
  }
  return Promise.reject(new Error(res.data.message));
}
