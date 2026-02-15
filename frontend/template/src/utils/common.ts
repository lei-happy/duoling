import type { Router } from 'vue-router';
import type { Action } from 'element-plus';
import { ElMessageBox } from 'element-plus';
import { LOGIN_PATH } from '@/config/setting';
import { removeToken } from '@/utils/token-util';
import router from '@/router';

/**
 * 跳转到登录界面
 * @param from 登录后跳转的地址
 * @param route 是否使用路由跳转
 */
export function goLogin(from?: string, route?: boolean) {
  removeToken();
  if (route) {
    router.push({
      path: LOGIN_PATH,
      query: from ? { from: encodeURIComponent(from) } : void 0
    });
    return;
  }
  // 使用页面跳转避免再次登录重复注册路由
  const url = import.meta.env.BASE_URL + 'login';
  location.replace(from ? `${url}?from=${encodeURIComponent(from)}` : url);
}

/**
 * 显示登录过期弹窗
 * @param from 登录后跳转的地址
 * @param route 是否使用路由跳转
 */
export function showExpiredLogout(from?: string, route?: boolean) {
  ElMessageBox.close();
  ElMessageBox.alert('登录状态已过期, 请退出重新登录!', '系统提示', {
    confirmButtonText: '重新登录',
    callback: (action: Action) => {
      if (action === 'confirm') {
        goLogin(from, route);
      }
    },
    type: 'warning',
    draggable: true
  });
}
/** 兼容旧版 */
export function logout(route?: boolean, from?: string, _push?: Router['push']) {
  goLogin(from, route);
}
export function showLogoutConfirm(from: string, push?: Router['push']) {
  showExpiredLogout(from, !!push);
}

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
 * @param params 参数
 * @param url 需要拼接参数的地址
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
 * @param params 参数
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
 * @param params 参数
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
 * @param obj 对象
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
 * @param obj 对象
 */
export function isBlobFile(obj: any) {
  return obj != null && (obj instanceof Blob || obj instanceof File);
}

/**
 * 判断是否是图片地址
 * @param url 图片地址
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
  return ['png', 'jpg', 'jpeg', 'gif', '.bmp', 'svg', 'webp', 'tiff'].includes(
    suffix.toLowerCase()
  );
}

/**
 * 判断是否是合法的组件名
 * @param name 组件名
 */
export function isValidComponentName(name: unknown) {
  if (typeof name !== 'string' || !name.length || /^\d/.test(name)) {
    return false;
  }
  // eslint-disable-next-line no-useless-escape
  return /^[a-zA-Z_][a-zA-Z0-9\-\.\_]*$/.test(name);
}

/**
 * 切换主题过渡动画
 * @param callback 执行的方法
 * @param el 过渡动画触发元素
 * @param isOut 是否是退出方向
 * @param isBody 是否在 body 上执行动画
 * @param customAnim 自定义动画
 */
export function doWithTransition(
  callback: () => Promise<any>,
  el?: HTMLElement | null,
  isOut?: boolean,
  isBody?: boolean,
  customAnim?: (clipPath: string[]) => Promise<any>
) {
  // @ts-ignore
  if (typeof document.startViewTransition !== 'function') {
    callback().catch((e) => console.error(e));
    return;
  }
  document.documentElement.classList.add('disabled-transition');
  if (el) {
    el.classList.add('view-transition-trigger');
    el.style.setProperty('view-transition-name', 'view-transition-trigger');
  }
  if (isBody) {
    document.body.style.setProperty('view-transition-name', 'body');
  }
  const rect = el
    ? el.getBoundingClientRect()
    : { left: 0, top: 0, width: innerWidth, height: innerHeight };
  const x = rect.left + rect.width / 2;
  const y = rect.top + rect.height / 2;
  const endRadius = Math.hypot(
    Math.max(x, innerWidth - x),
    Math.max(y, innerHeight - y)
  );
  // @ts-ignore
  document.startViewTransition(callback).ready.then(() => {
    const clipPath = [
      `circle(0px at ${x}px ${y}px)`,
      `circle(${endRadius}px at ${x}px ${y}px)`
    ];
    const finishAnim = () => {
      document.body.style.removeProperty('view-transition-name');
      if (el) {
        el.style.removeProperty('view-transition-name');
        el.classList.remove('view-transition-trigger');
      }
      document.documentElement.classList.remove('disabled-transition');
    };
    if (customAnim) {
      customAnim(clipPath).then(finishAnim);
      return;
    }
    const anim = document.documentElement.animate(
      { clipPath: isOut ? [...clipPath].reverse() : clipPath },
      {
        duration: 400,
        easing: 'ease-in',
        fill: 'forwards',
        pseudoElement: isOut
          ? `::view-transition-old(${isBody ? 'body' : 'root'})`
          : `::view-transition-new(${isBody ? 'body' : 'root'})`
      }
    );
    anim.onfinish = finishAnim;
  });
}
