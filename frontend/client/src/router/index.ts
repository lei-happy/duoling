/**
 * 路由配置
 */
import NProgress from 'nprogress';
import type { _RouteLocationBase } from 'vue-router';
import { createRouter, createWebHistory } from 'vue-router';
import { LOGIN_PATH, REDIRECT_PATH, LAYOUT_PATH } from '@/config/setting';
import { useUserStore } from '@/store/modules/user';
import { getToken, removeToken, removeRefreshToken } from '@/utils/token-util';
import { setPageTitle } from '@/utils/page-title-util';
import { getRouteTitle } from '@/i18n/use-locale';
import { routes, getMenuRoutes, isWhiteList } from './routes';

NProgress.configure({
  speed: 200,
  minimum: 0.02,
  trickleSpeed: 200,
  showSpinner: false
});

const router = createRouter({
  routes,
  history: createWebHistory(),
  scrollBehavior: () => {
    return { top: 0 };
  }
});

/**
 * 路由守卫
 */
router.beforeEach(async (to) => {
  if (!to.path.includes(REDIRECT_PATH)) {
    NProgress.start();
    setPageTitle(getRouteTitle(to));
  }
  if (!getToken()) {
    // 未登录跳转登录界面
    if (!isWhiteList(to.path)) {
      const query = { from: encodeURIComponent(to.fullPath) };
      return { path: LOGIN_PATH, query: to.path === LAYOUT_PATH ? {} : query };
    }
    return;
  }
  // 注册动态路由
  const userStore = useUserStore();
  if (!userStore.menus) {
    const { menus, homePath } = await userStore.fetchUserInfo(to);
    if (menus) {
      getMenuRoutes(menus, homePath).forEach((r) => {
        router.addRoute(r);
      });
      return { ...to, replace: true };
    }
    // token失效且刷新失败，清除token并跳转登录
    if (getToken()) {
      removeToken();
      removeRefreshToken();
      const query = to.path === LAYOUT_PATH ? {} : { from: encodeURIComponent(to.fullPath) };
      return { path: LOGIN_PATH, query };
    }
  }
});

router.afterEach((to) => {
  if (!to.path.includes(REDIRECT_PATH) && NProgress.isStarted()) {
    setTimeout(() => {
      NProgress.done(true);
    }, 200);
  }
});

export default router;
