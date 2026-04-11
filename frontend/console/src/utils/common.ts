import type { Router } from 'vue-router';
import type { Action } from 'element-plus';
import { ElMessageBox } from 'element-plus';
import { LOGIN_PATH } from '@/config/setting';
import { removeToken, removeRefreshToken } from '@/utils/token-util';
import router from '@/router';

export {
  downloadUrl,
  download,
  toURLSearch,
  toFormData,
  transformParams,
  getObjectParamsArray,
  isBlobFile,
  isImageUrl
} from '@zhitu/shared-utils';

/**
 * 跳转到登录界面
 * @param from 登录后跳转的地址
 * @param route 是否使用路由跳转
 */
export function goLogin(from?: string, route?: boolean) {
  removeToken();
  removeRefreshToken();
  if (route) {
    router.push({
      path: LOGIN_PATH,
      query: from ? { from: encodeURIComponent(from) } : void 0
    });
    return;
  }
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
