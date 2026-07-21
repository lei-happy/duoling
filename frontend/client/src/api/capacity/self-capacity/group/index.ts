import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  CapacityGroup,
  CapacityGroupParam,
  CapacityGroupOption,
  CapacityGroupMember,
  CapacityGroupMemberParam
} from './model';

const BASE = '/capacity/self_capacity/group';

/** 分组分页列表 */
export async function pageCapacityGroups(params: CapacityGroupParam) {
  const res = await request.get<ApiResult<PageResult<CapacityGroup>>>(BASE, {
    params
  });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 启用状态分组精简列表 */
export async function listCapacityGroupOptions(enterpriseId?: number) {
  const res = await request.get<ApiResult<CapacityGroupOption[]>>(
    `${BASE}/options`,
    { params: { enterpriseId } }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 新建分组 */
export async function addCapacityGroup(data: CapacityGroup) {
  const res = await request.post<ApiResult<CapacityGroup>>(BASE, data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 编辑分组 */
export async function updateCapacityGroup(data: CapacityGroup) {
  const res = await request.put<ApiResult<CapacityGroup>>(
    `${BASE}/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 启用/停用 */
export async function updateCapacityGroupStatus(id: number, status: number) {
  const res = await request.put<ApiResult<unknown>>(`${BASE}/${id}/status`, {
    status
  });
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 删除分组 */
export async function removeCapacityGroup(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${id}`);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 分组成员分页 */
export async function pageGroupMembers(
  groupId: number,
  params: CapacityGroupMemberParam
) {
  const res = await request.get<ApiResult<PageResult<CapacityGroupMember>>>(
    `${BASE}/${groupId}/members`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 批量添加成员（传运力ID列表） */
export async function addGroupMembers(groupId: number, capacityIds: number[]) {
  const res = await request.post<ApiResult<{ added: number; skipped: number }>>(
    `${BASE}/${groupId}/members`,
    { capacityIds }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 批量移出成员 */
export async function removeGroupMembers(
  groupId: number,
  payload: { memberIds?: number[]; driverIds?: number[] }
) {
  const res = await request.delete<ApiResult<{ removed: number }>>(
    `${BASE}/${groupId}/members`,
    { data: payload }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
