/**
 * AI 对话 SSE 流式客户端
 *
 * 浏览器原生 EventSource 不支持 POST + 自定义 Header（需要带 Token），
 * 故改用 fetch + ReadableStream 自行解析 SSE。
 */

import { TOKEN_HEADER_NAME } from '@/config/setting';
import { getToken } from '@/utils/token-util';
import type {
  ChatRequestBody,
  ConfirmRequestBody,
  AiSseEvent,
  AiSseEventType
} from './model';

const BASE_URL = (import.meta.env.VITE_API_URL as string) || '';

export interface SseStreamHandlers {
  onEvent?: (evt: AiSseEvent) => void;
  onError?: (err: Error) => void;
  onDone?: () => void;
  signal?: AbortSignal;
}

async function _streamSse(
  url: string,
  body: any,
  handlers: SseStreamHandlers
): Promise<void> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'text/event-stream'
  };
  if (token) headers[TOKEN_HEADER_NAME] = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${url}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      signal: handlers.signal
    });
  } catch (e: any) {
    handlers.onError?.(e instanceof Error ? e : new Error(String(e)));
    return;
  }

  if (!res.ok || !res.body) {
    handlers.onError?.(new Error(`HTTP ${res.status} ${res.statusText}`));
    return;
  }

  // 后端在前置校验失败时（无可用 Provider、限流、配额超限等）会被全局
  // 异常处理改写成 200 + JSON {code, message}，与 SSE 不同。这里检测一下
  // Content-Type，遇到 JSON 就当成业务错误冒泡。
  const contentType = res.headers.get('content-type') || '';
  if (!contentType.includes('text/event-stream')) {
    try {
      const txt = await res.text();
      let msg = txt;
      try {
        const json = JSON.parse(txt);
        msg = json?.message || json?.detail || txt;
      } catch {
        /* keep raw text */
      }
      handlers.onError?.(new Error(msg || '后端未返回 SSE 流'));
    } catch (e: any) {
      handlers.onError?.(e instanceof Error ? e : new Error(String(e)));
    }
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let sepIdx: number;
      while ((sepIdx = buffer.indexOf('\n\n')) !== -1) {
        const rawEvent = buffer.slice(0, sepIdx);
        buffer = buffer.slice(sepIdx + 2);
        const parsed = parseSseChunk(rawEvent);
        if (parsed) handlers.onEvent?.(parsed);
      }
    }
    handlers.onDone?.();
  } catch (e: any) {
    if (e?.name !== 'AbortError') {
      handlers.onError?.(e instanceof Error ? e : new Error(String(e)));
    }
  }
}

function parseSseChunk(raw: string): AiSseEvent | null {
  let event: string | null = null;
  const dataLines: string[] = [];
  for (const line of raw.split(/\r?\n/)) {
    if (!line || line.startsWith(':')) continue;
    if (line.startsWith('event:')) {
      event = line.slice(6).trim();
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trim());
    }
  }
  if (!event) return null;
  const dataStr = dataLines.join('\n');
  let data: any = dataStr;
  try {
    data = JSON.parse(dataStr || '{}');
  } catch {
    /* 保留为字符串 */
  }
  return { event: event as AiSseEventType, data };
}

export async function postChatStream(
  body: ChatRequestBody,
  handlers: SseStreamHandlers
): Promise<void> {
  return _streamSse('/ai/chat', body, handlers);
}

export async function postChatConfirm(
  body: ConfirmRequestBody,
  handlers: SseStreamHandlers
): Promise<void> {
  return _streamSse('/ai/chat/confirm', body, handlers);
}
