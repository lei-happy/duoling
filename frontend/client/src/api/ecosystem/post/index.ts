import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type {
  EcoMyPostPage,
  EcoMyPostParam,
  EcoPost
} from '@/api/ecosystem/hall/model';
import type {
  EcoCapacityForm,
  EcoCapacityPreviewParam,
  EcoCapacityPublishForm,
  EcoCargoForm,
  EcoCargoPublishForm,
  EcoManageResult,
  EcoPublishOptions,
  EcoPublishPreview,
  EcoPublishResult
} from './model';

const PUBLISH = '/ecosystem/publish';
const MINE = '/ecosystem/my-posts';

/**
 * 成功响应里的 message 也要用上
 *
 * 后端对「已提交等审核」「已直接上架」「已停止展示，同时结束了 3 个洽谈」
 * 给的是不同的话术，前端自己写一句固定文案会把这些差别抹平。
 */
interface WithMessage<T> {
  data: T;
  message?: string;
}

async function unwrap<T>(promise: Promise<{ data: ApiResult<T> }>) {
  const res = await promise;
  if (res.data.code === 0) {
    return { data: res.data.data as T, message: res.data.message };
  }
  return Promise.reject(new Error(res.data.message));
}

// ---------------------------------------------------------------------------
// 发布
// ---------------------------------------------------------------------------

/** 发布弹层默认值（联系人、展示天数、可见范围、大厅能力状态） */
export async function getPublishOptions() {
  const res = await request.get<ApiResult<EcoPublishOptions>>(
    `${PUBLISH}/options`
  );
  if (res.data.code === 0) {
    return res.data.data as EcoPublishOptions;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 货源发布前试算 */
export async function previewCargo(taskId: number) {
  const res = await request.post<ApiResult<EcoPublishPreview>>(
    `${PUBLISH}/cargo/preview`,
    { taskId }
  );
  if (res.data.code === 0) {
    return res.data.data as EcoPublishPreview;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 运力发布前试算 */
export async function previewCapacity(data: EcoCapacityPreviewParam) {
  const res = await request.post<ApiResult<EcoPublishPreview>>(
    `${PUBLISH}/capacity/preview`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data as EcoPublishPreview;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 发布货源到货源大厅 */
export function publishCargo(
  data: EcoCargoPublishForm
): Promise<WithMessage<EcoPublishResult>> {
  return unwrap(
    request.post<ApiResult<EcoPublishResult>>(`${PUBLISH}/cargo`, data)
  );
}

/** 发布空闲运力到运力大厅 */
export function publishCapacity(
  data: EcoCapacityPublishForm
): Promise<WithMessage<EcoPublishResult>> {
  return unwrap(
    request.post<ApiResult<EcoPublishResult>>(`${PUBLISH}/capacity`, data)
  );
}

// ---------------------------------------------------------------------------
// 我发布的
// ---------------------------------------------------------------------------

/** 我发布的分页列表（含页签角标计数） */
export async function pageMyPosts(params: EcoMyPostParam) {
  const res = await request.get<ApiResult<EcoMyPostPage>>(MINE, { params });
  if (res.data.code === 0) {
    return res.data.data as EcoMyPostPage;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 自己挂牌的详情：不限状态，带热度反馈 */
export async function getMyPostDetail(postId: number) {
  const res = await request.get<ApiResult<EcoPost>>(`${MINE}/${postId}`);
  if (res.data.code === 0) {
    return res.data.data as EcoPost;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 编辑货源挂牌（源单 ID 取自挂牌本身，不用传） */
export function editCargoPost(
  postId: number,
  data: EcoCargoForm
): Promise<WithMessage<EcoManageResult>> {
  return unwrap(
    request.put<ApiResult<EcoManageResult>>(`${MINE}/cargo/${postId}`, data)
  );
}

/** 编辑运力挂牌 */
export function editCapacityPost(
  postId: number,
  data: EcoCapacityForm
): Promise<WithMessage<EcoManageResult>> {
  return unwrap(
    request.put<ApiResult<EcoManageResult>>(`${MINE}/capacity/${postId}`, data)
  );
}

/** 提交审核（草稿 / 被驳回的挂牌） */
export function submitPost(
  postId: number,
  validDays?: number
): Promise<WithMessage<EcoManageResult>> {
  return unwrap(
    request.post<ApiResult<EcoManageResult>>(`${MINE}/${postId}/submit`, {
      validDays
    })
  );
}

/** 停止展示。正在洽谈的意向会一并失效，条数在结果里 */
export function delistPost(
  postId: number,
  remark?: string
): Promise<WithMessage<EcoManageResult>> {
  return unwrap(
    request.post<ApiResult<EcoManageResult>>(`${MINE}/${postId}/delist`, {
      remark
    })
  );
}

/** 重新上架。一律回待审核，免审白名单在这里不生效 */
export function relistPost(
  postId: number,
  validDays?: number
): Promise<WithMessage<EcoManageResult>> {
  return unwrap(
    request.post<ApiResult<EcoManageResult>>(`${MINE}/${postId}/relist`, {
      validDays
    })
  );
}

/** 延长展示天数（只对展示中的挂牌有效，不触发重审） */
export function extendPost(
  postId: number,
  days: number
): Promise<WithMessage<EcoManageResult>> {
  return unwrap(
    request.post<ApiResult<EcoManageResult>>(`${MINE}/${postId}/extend`, {
      days
    })
  );
}
