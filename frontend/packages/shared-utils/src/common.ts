/**
 * 通用工具函数（与框架无关的纯函数）
 */

/**
 * 下载文件
 * @param url 文件地址
 * @param name 文件名
 */
export function downloadUrl(url: string, name: string) {
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.style.display = 'none';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/**
 * 下载文件
 * @param data 二进制数据
 * @param name 文件名
 * @param type 文件类型
 */
export function download(
  data: Blob | ArrayBuffer | string,
  name: string,
  type?: string
) {
  const blob = new Blob([data], { type: type || 'application/octet-stream' });
  const url = URL.createObjectURL(blob);
  downloadUrl(url, name);
  URL.revokeObjectURL(url);
}

/**
 * 参数转url字符串
 */
export function toURLSearch(
  params?: Record<keyof any, any> | null,
  url?: string
): string {
  if (typeof params !== 'object' || params == null) {
    return '';
  }
  const result = transformParams(params)
    .map((d) => `${encodeURIComponent(d[0])}=${encodeURIComponent(d[1])}`)
    .join('&');
  if (!url) {
    return result;
  }
  return (url.includes('?') ? `${url}&` : `${url}?`) + result;
}

/**
 * 参数转表单数据
 */
export function toFormData(params?: Record<keyof any, any> | null): FormData {
  const formData = new FormData();
  if (typeof params !== 'object' || params == null) {
    return formData;
  }
  transformParams(params).forEach((d) => {
    formData.append(d[0], d[1]);
  });
  return formData;
}

/**
 * get请求处理数组和对象类型参数
 */
export function transformParams(params?: Record<string, any> | null) {
  const result: [string, string][] = [];
  if (params != null && typeof params === 'object') {
    Object.keys(params).forEach((key) => {
      const value = params[key];
      if (value != null && value !== '') {
        if (Array.isArray(value) && value.length && isBlobFile(value[0])) {
          value.forEach((file) => {
            result.push([key, file]);
          });
        } else if (typeof value === 'object' && !isBlobFile(value)) {
          getObjectParamsArray(value).forEach((item) => {
            result.push([`${key}${item[0]}`, item[1]]);
          });
        } else {
          result.push([key, value]);
        }
      }
    });
  }
  return result;
}

/**
 * 对象转参数数组
 */
export function getObjectParamsArray(obj: Record<string, any>) {
  const result: [string, string][] = [];
  Object.keys(obj).forEach((key) => {
    const value = obj[key];
    if (value != null && value !== '') {
      const name = `[${key}]`;
      if (typeof value === 'object' && !isBlobFile(value)) {
        getObjectParamsArray(value).forEach((item) => {
          result.push([`${name}${item[0]}`, item[1]]);
        });
      } else {
        result.push([name, value]);
      }
    }
  });
  return result;
}

/**
 * 判断是否是文件
 */
export function isBlobFile(obj: any) {
  return obj != null && (obj instanceof Blob || obj instanceof File);
}

/**
 * 判断是否是图片地址
 */
export function isImageUrl(url?: string) {
  if (!url) {
    return false;
  }
  const parts = url.split('.');
  const suffix = parts[parts.length - 1];
  if (!suffix) {
    return false;
  }
  return ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp', 'tiff'].includes(
    suffix.toLowerCase()
  );
}
