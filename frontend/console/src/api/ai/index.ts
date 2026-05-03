/**
 * Console 端 AI 数字员工管理 API
 */

import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  AiEmployeeDetail,
  AiEmployeeFormPayload,
  AiTool,
  AiPromptTemplate,
  AiProvider,
  AiToolLog,
  AiStats,
  AiSessionRow,
  AiMessageRow
} from './model';

// ---------- 数字员工 ----------

export async function pageEmployees(params: {
  page?: number;
  limit?: number;
  keyword?: string;
  status?: number;
  employeeType?: string;
}) {
  const res = await request.get<ApiResult<PageResult<AiEmployeeDetail>>>(
    '/ai/employee',
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getEmployee(id: number) {
  const res = await request.get<ApiResult<AiEmployeeDetail>>(`/ai/employee/${id}`);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function addEmployee(data: AiEmployeeFormPayload) {
  const res = await request.post<ApiResult<{ id: number }>>(
    '/ai/employee',
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateEmployee(id: number, data: AiEmployeeFormPayload) {
  const res = await request.put<ApiResult<unknown>>(`/ai/employee/${id}`, data);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function deleteEmployee(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`/ai/employee/${id}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

// ---------- 工具 ----------

export async function pageTools(params: {
  page?: number;
  limit?: number;
  keyword?: string;
  category?: string;
  status?: number;
}) {
  const res = await request.get<ApiResult<PageResult<AiTool>>>('/ai/tool', {
    params
  });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listToolCategories() {
  const res = await request.get<ApiResult<{ list: string[] }>>(
    '/ai/tool/categories'
  );
  if (res.data.code === 0) return res.data.data?.list ?? [];
  return Promise.reject(new Error(res.data.message));
}

export async function updateToolStatus(id: number, status: number) {
  const res = await request.put<ApiResult<unknown>>(`/ai/tool/${id}/status`, {
    status
  });
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function syncTools() {
  const res = await request.post<
    ApiResult<{ inserted: number; updated: number; orphan: number }>
  >('/ai/tool/sync');
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

// ---------- 提示词模板 ----------

export async function pagePrompts(params: {
  page?: number;
  limit?: number;
  keyword?: string;
  scene?: string;
  status?: number;
}) {
  const res = await request.get<ApiResult<PageResult<AiPromptTemplate>>>(
    '/ai/prompt',
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function addPrompt(data: Partial<AiPromptTemplate>) {
  const res = await request.post<ApiResult<{ id: number }>>('/ai/prompt', data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updatePrompt(id: number, data: Partial<AiPromptTemplate>) {
  const res = await request.put<ApiResult<unknown>>(`/ai/prompt/${id}`, data);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function deletePrompt(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`/ai/prompt/${id}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

// ---------- LLM Provider ----------

export async function pageProviders(params: {
  page?: number;
  limit?: number;
  keyword?: string;
  status?: number;
}) {
  const res = await request.get<ApiResult<PageResult<AiProvider>>>(
    '/ai/provider',
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function addProvider(
  data: Partial<AiProvider> & { apiKey?: string }
) {
  const res = await request.post<ApiResult<{ id: number }>>(
    '/ai/provider',
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateProvider(
  id: number,
  data: Partial<AiProvider> & { apiKey?: string }
) {
  const res = await request.put<ApiResult<unknown>>(`/ai/provider/${id}`, data);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function deleteProvider(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`/ai/provider/${id}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function setDefaultProvider(id: number) {
  const res = await request.put<ApiResult<unknown>>(
    `/ai/provider/${id}/default`
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

// ---------- 调用观测 ----------

export async function listAuditTenants() {
  const res = await request.get<ApiResult<{ list: string[] }>>(
    '/ai/observe/tenants'
  );
  if (res.data.code === 0) return res.data.data?.list ?? [];
  return Promise.reject(new Error(res.data.message));
}

export async function pageToolLogs(params: {
  tenantCode: string;
  page?: number;
  limit?: number;
  sessionId?: number;
  toolCode?: string;
  status?: string;
  userId?: number;
}) {
  const res = await request.get<ApiResult<PageResult<AiToolLog>>>(
    '/ai/observe/tool-logs',
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getTenantStats(tenantCode: string, days = 7) {
  const res = await request.get<ApiResult<AiStats>>('/ai/observe/stats', {
    params: { tenantCode, days }
  });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

// ---------- 会话浏览 ----------

export async function pageObserveSessions(params: {
  tenantCode: string;
  page?: number;
  limit?: number;
  keyword?: string;
  employeeCode?: string;
  userId?: number;
  status?: number;
}) {
  const res = await request.get<ApiResult<PageResult<AiSessionRow>>>(
    '/ai/observe/sessions',
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getObserveSessionMessages(
  sessionId: number,
  tenantCode: string,
  limit = 200
) {
  const res = await request.get<
    ApiResult<{ session: AiSessionRow | null; messages: AiMessageRow[] }>
  >(`/ai/observe/sessions/${sessionId}/messages`, {
    params: { tenantCode, limit }
  });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}
