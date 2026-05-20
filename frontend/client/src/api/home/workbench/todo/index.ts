import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { TodoTask } from './types';

function assertOk<T>(res: { data: ApiResult<T> }) {
  if (res.data.code !== 0) {
    return Promise.reject(new Error(res.data.message || '请求失败'));
  }
  return res;
}

export type TodoTaskListData = {
  items: TodoTask[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export type TodoTaskStatsData = {
  total: number;
  pending: number;
  in_progress: number;
  completed: number;
};

export type AssignableUser = { id: number; display_name: string };

/** 分页任务列表（返回 axios 响应，与 todo-card 解析方式一致） */
export async function getTodoTaskList(params: {
  page?: number;
  page_size?: number;
  status?: number;
  my_tasks?: boolean;
}) {
  const res = await request.get<ApiResult<TodoTaskListData>>(
    '/workbench/todo/tasks',
    { params }
  );
  return assertOk(res);
}

export async function getTodoTaskStats(params?: { my_tasks?: boolean }) {
  const res = await request.get<ApiResult<TodoTaskStatsData>>(
    '/workbench/todo/stats',
    { params }
  );
  return assertOk(res);
}

export async function getUsersForAssignment(keyword?: string) {
  const res = await request.get<ApiResult<AssignableUser[]>>(
    '/workbench/todo/users-for-assign',
    { params: keyword ? { q: keyword } : {} }
  );
  return assertOk(res);
}

export async function createTodoTask(data: Record<string, unknown>) {
  const res = await request.post<ApiResult<TodoTask>>('/workbench/todo', data);
  return assertOk(res);
}

export async function updateTodoTask(
  id: number,
  data: Record<string, unknown>
) {
  const res = await request.put<ApiResult<TodoTask>>(
    `/workbench/todo/${id}`,
    data
  );
  return assertOk(res);
}

export async function deleteTodoTask(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`/workbench/todo/${id}`);
  return assertOk(res);
}

export async function updateTaskStatus(id: number, status: number) {
  const res = await request.patch<ApiResult<TodoTask>>(
    `/workbench/todo/${id}/status`,
    { status }
  );
  return assertOk(res);
}

export type { TodoTask } from './types';
