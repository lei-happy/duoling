import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  Capability,
  OpenApp,
  OpenAppForm,
  Credential,
  CredentialCreateForm,
  CredentialScopeForm,
  McpConfig,
  McpCreateForm,
  McpUpdateForm,
  CallLog,
  CallLogParam,
  CallStats
} from './model';

const BASE = '/open-platform';

// ============================================================
// 能力目录
// ============================================================

/** 能力目录（channel 可选 api / mcp） */
export async function listCapabilities(channel?: string) {
  const res = await request.get<ApiResult<Capability[]>>(
    `${BASE}/capabilities`,
    {
      params: { channel }
    }
  );
  if (res.data.code === 0) {
    return res.data.data ?? [];
  }
  return Promise.reject(new Error(res.data.message));
}

// ============================================================
// 接入应用
// ============================================================

export async function listApps() {
  const res = await request.get<ApiResult<OpenApp[]>>(`${BASE}/apps`);
  if (res.data.code === 0) {
    return res.data.data ?? [];
  }
  return Promise.reject(new Error(res.data.message));
}

export async function createApp(data: OpenAppForm) {
  const res = await request.post<ApiResult<{ id: number }>>(
    `${BASE}/apps`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateApp(appId: number, data: OpenAppForm) {
  const res = await request.put<ApiResult<unknown>>(
    `${BASE}/apps/${appId}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

// ============================================================
// API 凭证
// ============================================================

export async function listCredentials(appId: number) {
  const res = await request.get<ApiResult<Credential[]>>(
    `${BASE}/apps/${appId}/credentials`
  );
  if (res.data.code === 0) {
    return res.data.data ?? [];
  }
  return Promise.reject(new Error(res.data.message));
}

export async function createCredential(
  appId: number,
  data: CredentialCreateForm
) {
  const res = await request.post<ApiResult<Credential>>(
    `${BASE}/apps/${appId}/credentials`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateCredentialScope(
  credentialId: number,
  data: CredentialScopeForm
) {
  const res = await request.put<ApiResult<Credential>>(
    `${BASE}/credentials/${credentialId}/scope`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function resetCredential(credentialId: number) {
  const res = await request.post<ApiResult<Credential>>(
    `${BASE}/credentials/${credentialId}/reset`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function revokeCredential(credentialId: number) {
  const res = await request.post<ApiResult<unknown>>(
    `${BASE}/credentials/${credentialId}/revoke`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

// ============================================================
// MCP 连接
// ============================================================

export async function listMcpConfigs(appId: number) {
  const res = await request.get<ApiResult<McpConfig[]>>(
    `${BASE}/apps/${appId}/mcp`
  );
  if (res.data.code === 0) {
    return res.data.data ?? [];
  }
  return Promise.reject(new Error(res.data.message));
}

export async function createMcpConfig(appId: number, data: McpCreateForm) {
  const res = await request.post<ApiResult<McpConfig>>(
    `${BASE}/apps/${appId}/mcp`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateMcpConfig(configId: number, data: McpUpdateForm) {
  const res = await request.put<ApiResult<McpConfig>>(
    `${BASE}/mcp/${configId}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function deleteMcpConfig(configId: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `${BASE}/mcp/${configId}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

// ============================================================
// 调用记录
// ============================================================

export async function pageCallLogs(params: CallLogParam) {
  const res = await request.get<ApiResult<PageResult<CallLog>>>(
    `${BASE}/logs`,
    {
      params
    }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getCallStats(days = 1) {
  const res = await request.get<ApiResult<CallStats>>(`${BASE}/logs/stats`, {
    params: { days }
  });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
