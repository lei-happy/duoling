/**
 * AI 数字员工模块 - 普通 REST API 服务
 */

import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type {
  AiEmployee,
  AiEmployeeTool,
  AiSession,
  AiMessage,
  AiAttachment
} from './model';

export async function listAiEmployees() {
  const res =
    await request.get<ApiResult<{ list: AiEmployee[] }>>('/ai/employee');
  if (res.data.code === 0) return res.data.data?.list ?? [];
  return Promise.reject(new Error(res.data.message));
}

export async function listEmployeeTools(employeeCode: string) {
  const res = await request.get<ApiResult<{ list: AiEmployeeTool[] }>>(
    `/ai/employee/${employeeCode}/tools`
  );
  if (res.data.code === 0) return res.data.data?.list ?? [];
  return Promise.reject(new Error(res.data.message));
}

export async function pageAiSessions(params: {
  page?: number;
  limit?: number;
  employeeCode?: string;
  keyword?: string;
}) {
  const res = await request.get<
    ApiResult<{ list: AiSession[]; total: number }>
  >('/ai/session', { params });
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function listSessionMessages(sessionId: number, limit = 100) {
  const res = await request.get<ApiResult<{ list: AiMessage[] }>>(
    `/ai/session/${sessionId}/messages`,
    { params: { limit } }
  );
  if (res.data.code === 0) return res.data.data?.list ?? [];
  return Promise.reject(new Error(res.data.message));
}

export async function renameAiSession(sessionId: number, title: string) {
  const res = await request.put<ApiResult<unknown>>(
    `/ai/session/${sessionId}`,
    { title }
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function deleteAiSession(sessionId: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/ai/session/${sessionId}`
  );
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function uploadAiAttach(file: File): Promise<AiAttachment> {
  const fd = new FormData();
  fd.append('file', file);
  const res = await request.post<ApiResult<AiAttachment>>(
    '/ai/file/upload',
    fd
  );
  if (res.data.code === 0 && res.data.data) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}
