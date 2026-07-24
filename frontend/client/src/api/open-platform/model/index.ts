import type { PageParam } from '@/api';

/** 能力目录项（读后端注册表，字段与实现始终一致） */
export interface Capability {
  code: string;
  name: string;
  category?: string;
  description?: string;
  channels: string[];
  read_only: boolean;
  risk_level?: string;
  stability?: string;
  version?: string;
  input_schema?: Record<string, any> | null;
  output_fields?: string[] | null;
}

/** 接入应用 */
export interface OpenApp {
  id?: number;
  name?: string;
  description?: string;
  status?: string; // enabled / disabled
  credential_count?: number;
  created_at?: string;
}

export interface OpenAppForm {
  name: string;
  description?: string;
  status?: string;
}

/** API 凭证 */
export interface Credential {
  id: number;
  app_id: number;
  cred_type: string;
  access_key: string;
  scope: string[];
  ip_whitelist?: string;
  status: string; // enabled / revoked
  expires_at?: string | null;
  last_used_at?: string | null;
  created_at?: string;
  /** 仅创建/重置时返回一次的明文密钥 */
  secret?: string;
}

export interface CredentialCreateForm {
  scope: string[];
  ip_whitelist?: string;
  expires_at?: string | null;
}

export interface CredentialScopeForm {
  scope?: string[];
  ip_whitelist?: string;
}

/** MCP 连接配置 */
export interface McpConfig {
  id: number;
  display_name: string;
  server_slug: string;
  enabled_capabilities: string[];
  status: string;
  url: string;
  created_at?: string;
  /** 仅创建时返回一次的 Token 与可复制配置 */
  token?: string;
  config_json?: Record<string, any>;
}

export interface McpCreateForm {
  display_name: string;
  enabled_capabilities: string[];
}

export interface McpUpdateForm {
  display_name?: string;
  enabled_capabilities?: string[];
  status?: string;
}

/** 调用记录 */
export interface CallLog {
  id: number;
  request_id?: string;
  app_id?: number;
  channel?: string;
  capability_code?: string;
  status?: string;
  error_code?: string;
  http_status?: number;
  latency_ms?: number;
  client_ip?: string;
  result_summary?: string;
  created_at?: string;
}

export interface CallLogParam extends PageParam {
  capability_code?: string;
  status?: string;
  channel?: string;
  app_id?: number;
}

/** 调用概览统计 */
export interface CallStats {
  total: number;
  success: number;
  successRate: number;
  avgLatencyMs: number;
  topCapabilities: Array<{ capability_code: string; count: number }>;
}
