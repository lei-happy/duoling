/**
 * AI 数字员工模块 - Console 端类型
 */

export interface AiEmployeeDetail {
  id: number;
  code: string;
  name: string;
  employeeType: string;
  description?: string;
  avatar?: string;
  systemPrompt?: string;
  welcomeMessage?: string;
  suggestedQuestions?: string[];
  modelConfig?: Record<string, any>;
  featureCode?: string;
  sortOrder: number;
  status: number;
  toolIds: number[];
  createdAt?: string;
  updatedAt?: string;
}

export interface AiEmployeeFormPayload {
  code?: string;
  name: string;
  employeeType: string;
  description?: string;
  avatar?: string;
  systemPrompt?: string;
  welcomeMessage?: string;
  suggestedQuestions?: string[];
  modelConfig?: Record<string, any>;
  featureCode?: string;
  sortOrder?: number;
  status?: number;
  toolIds?: number[];
}

export interface AiTool {
  id: number;
  code: string;
  name: string;
  category?: string;
  description?: string;
  paramsSchema?: Record<string, any>;
  requiredPermission?: string;
  riskLevel: 'low' | 'medium' | 'high';
  confirmRequired: boolean;
  isBuiltin: boolean;
  status: number;
}

export interface AiPromptTemplate {
  id: number;
  code: string;
  name: string;
  scene: string;
  content: string;
  description?: string;
  version: number;
  status: number;
}

export interface AiProvider {
  id: number;
  code: string;
  name: string;
  providerType: string;
  baseUrl?: string;
  apiKeyMasked?: string;
  modelName: string;
  extraParams?: Record<string, any>;
  timeoutSeconds: number;
  isDefault: boolean;
  status: number;
}

export interface AiToolLog {
  id: number;
  sessionId: number;
  messageId?: number;
  toolCallId?: string;
  toolCode: string;
  toolName?: string;
  userId: number;
  params?: Record<string, any>;
  resultSummary?: string;
  status: string;
  errorMessage?: string;
  latencyMs: number;
  createdAt?: string;
}

export interface AiStatsItem {
  tool_code: string;
  total: number;
  success: number;
  failed: number;
  denied: number;
  avg_latency_ms: number;
}

export interface AiStats {
  since: string;
  tool_stats: AiStatsItem[];
  total_prompt_tokens: number;
  total_completion_tokens: number;
}

export interface AiSessionRow {
  id: number;
  sessionNo: string;
  userId: number;
  employeeCode: string;
  employeeName?: string;
  title?: string;
  status: number;
  lastMessageAt?: string;
  messageCount: number;
  totalPromptTokens: number;
  totalCompletionTokens: number;
  createdAt?: string;
}

export interface AiMessageRow {
  id: number;
  sessionId: number;
  role: 'user' | 'assistant' | 'tool' | 'system';
  content?: string;
  toolCalls?: any[];
  toolCallId?: string;
  toolName?: string;
  attachments?: any[];
  modelUsed?: string;
  promptTokens: number;
  completionTokens: number;
  finishReason?: string;
  status: number;
  errorMessage?: string;
  createdAt?: string;
}
