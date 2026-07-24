/** 开放平台前端共享常量与展示映射 */

/** 应用/凭证/MCP 状态 → Tag 颜色 */
export function statusTagType(status?: string): 'success' | 'danger' | 'info' {
  switch (status) {
    case 'enabled':
      return 'success';
    case 'disabled':
    case 'revoked':
      return 'danger';
    default:
      return 'info';
  }
}

export function statusText(status?: string): string {
  switch (status) {
    case 'enabled':
      return '已启用';
    case 'disabled':
      return '已停用';
    case 'revoked':
      return '已停用';
    default:
      return status || '—';
  }
}

/** 调用结果状态 → Tag 颜色 */
export function callStatusTagType(
  status?: string
): 'success' | 'danger' | 'warning' | 'info' {
  switch (status) {
    case 'success':
      return 'success';
    case 'failed':
      return 'danger';
    case 'denied':
      return 'warning';
    default:
      return 'info';
  }
}

export function callStatusText(status?: string): string {
  switch (status) {
    case 'success':
      return '成功';
    case 'failed':
      return '失败';
    case 'denied':
      return '被拒绝';
    default:
      return status || '—';
  }
}

/** 调用通道文案 */
export function channelText(channel?: string): string {
  switch (channel) {
    case 'api':
      return 'API 接口';
    case 'mcp':
      return 'MCP 工具';
    default:
      return channel || '—';
  }
}

/** 风险等级文案 */
export function riskText(level?: string): string {
  switch (level) {
    case 'low':
      return '低';
    case 'medium':
      return '中';
    case 'high':
      return '高';
    default:
      return level || '—';
  }
}

export const CHANNEL_OPTIONS = [
  { label: 'API 接口', value: 'api' },
  { label: 'MCP 工具', value: 'mcp' }
];

export const CALL_STATUS_OPTIONS = [
  { label: '成功', value: 'success' },
  { label: '失败', value: 'failed' },
  { label: '被拒绝', value: 'denied' }
];

/** 复制文本到剪贴板，返回是否成功 */
export async function copyText(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(textarea);
    return ok;
  } catch {
    return false;
  }
}
