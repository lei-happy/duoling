/**
 * AI 数字员工模块 - 类型定义
 */

export interface AiEmployee {
  code: string;
  name: string;
  employeeType: string;
  description?: string;
  avatar?: string;
  welcomeMessage?: string;
  suggestedQuestions?: string[];
}

export interface AiEmployeeTool {
  code: string;
  name: string;
  category?: string;
  description?: string;
  riskLevel: 'low' | 'medium' | 'high';
  confirmRequired: boolean;
}

export interface AiSession {
  id: number;
  sessionNo: string;
  employeeCode: string;
  employeeName?: string;
  title?: string;
  status: number;
  messageCount: number;
  lastMessageAt?: string;
  createdAt?: string;
}

export interface AiMessage {
  id: number;
  role: 'user' | 'assistant' | 'tool' | 'system';
  content?: string;
  toolCalls?: any[];
  toolCallId?: string;
  toolName?: string;
  attachments?: AiAttachment[];
  createdAt?: string;
}

export interface AiAttachment {
  fileId: string;
  name: string;
  size?: number;
  mime?: string;
}

export interface ChatRequestBody {
  employeeCode: string;
  sessionId?: number;
  content: string;
  attachments?: AiAttachment[];
}

export interface ConfirmRequestBody {
  sessionId: number;
  confirmToken: string;
  approved: boolean;
}

/** SSE 事件类型 */
export type AiSseEventType =
  | 'session'
  | 'message'
  | 'delta'
  | 'tool.call'
  | 'tool.result'
  | 'confirm.required'
  | 'usage'
  | 'done'
  | 'error';

export interface AiSseEvent {
  event: AiSseEventType | string;
  data: any;
}

/** 工具调用时间线条目（前端聚合） */
export interface ToolCallEntry {
  toolCallId: string;
  toolCode: string;
  toolName?: string;
  status:
    | 'calling'
    | 'success'
    | 'failed'
    | 'denied'
    | 'cancelled'
    | 'pending_confirm';
  riskLevel?: string;
  params?: any;
  summary?: string;
  error?: string;
  latencyMs?: number;
  confirmToken?: string;
}

/** 前端聚合的会话消息（含 assistant 流式 + 工具调用时间线） */
export interface ChatTurn {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  pending?: boolean;
  toolCalls: ToolCallEntry[];
  attachments?: AiAttachment[];
  createdAt: string;
}
