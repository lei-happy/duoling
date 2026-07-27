import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { PrototypeTreeNode } from './model/design-module';
import { getToken } from '@/utils/token-util';

const PROTO_COOKIE = 'zt_proto_token';
const PROTO_COOKIE_PATH = '/api/console/doc-center/prototypes';

/**
 * 获取产品原型目录树（仅扫描仓库 prototype/）
 */
export async function getPrototypeTree() {
  const res = await request.get<ApiResult<PrototypeTreeNode[]>>(
    '/doc-center/prototypes/tree'
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 为 iframe 预览写入同源 Cookie（相对资源请求会自动带上）
 */
export function ensurePrototypePreviewAuth() {
  const token = getToken();
  if (!token) return;
  // JWT 字符对 Cookie 安全，勿 encode，避免服务端校验失败
  document.cookie = `${PROTO_COOKIE}=${token}; path=${PROTO_COOKIE_PATH}; SameSite=Lax`;
}

/**
 * 构造原型 HTML 预览地址
 */
export function buildPrototypePreviewUrl(relPath?: string | null): string | null {
  if (!relPath) return null;
  const path = relPath.replace(/\\/g, '/').replace(/^\/+/, '');
  const base = (import.meta.env.VITE_API_URL || '/api/console').replace(/\/$/, '');
  const token = getToken();
  const qs = token ? `?access_token=${encodeURIComponent(token)}` : '';
  return `${base}/doc-center/prototypes/file/${path}${qs}`;
}
