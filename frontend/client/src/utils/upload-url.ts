/**
 * 将后端返回的静态资源相对路径转为浏览器可请求的完整地址。
 * - 开发环境：通常配合 Vite 将 /uploads 代理到后端，保持相对路径即可。
 * - 前后端不同源且未把 /uploads 挂到同域时：配置 VITE_UPLOAD_BASE_URL（后端根地址，无尾斜杠）。
 */
export function resolveUploadUrl(path: string | undefined | null): string {
  if (path == null || !String(path).trim()) {
    return '';
  }
  const p = String(path).trim();
  if (/^https?:\/\//i.test(p)) {
    return p;
  }
  const base = (
    import.meta.env.VITE_UPLOAD_BASE_URL as string | undefined
  )?.trim();
  if (base && p.startsWith('/uploads')) {
    return `${base.replace(/\/$/, '')}${p}`;
  }
  return p;
}
