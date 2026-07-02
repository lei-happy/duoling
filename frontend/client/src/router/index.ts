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
import { ElMessage } from 'element-plus';
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

/** 懒加载 chunk 加载失败时的一次性防抖标记 key，避免整页重载后仍失败导致的死循环 */
const CHUNK_RELOAD_FLAG = 'chunk-reload-attempt';

/**
 * 判断错误是否为懒加载 chunk（动态 import）加载失败。
 * 典型场景：前端发版后 chunk 文件名 hash 变化，老标签页引用的旧文件已被删除返回 404，
 * 用户切换菜单触发 import() 时 Promise reject。
 */
function isChunkLoadError(error: unknown): boolean {
  const message = error instanceof Error ? error.message : String(error ?? '');
  return (
    /Failed to fetch dynamically imported module/i.test(message) ||
    /error loading dynamically imported module/i.test(message) ||
    /Importing a module script failed/i.test(message) ||
    /Loading chunk \d+ failed/i.test(message) ||
    /Loading CSS chunk/i.test(message) ||
    /ChunkLoadError/i.test(message)
  );
}

/**
 * 路由错误处理：
 * - 命中 chunk 加载失败：清除卡住的进度条，做一次性防抖后整页重载到用户目标路径，用户无感恢复；
 * - 其它导航错误：仅结束进度条并打印日志，避免顶部 loading 卡死。
 */
router.onError((error, to) => {
  NProgress.done(true);
  if (!isChunkLoadError(error)) {
    console.error('[router] 导航发生错误', error);
    return;
  }
  // 防抖：整页刷新后若仍失败（例如服务端确实缺文件），不再无限重载
  const alreadyTried = sessionStorage.getItem(CHUNK_RELOAD_FLAG);
  const targetPath = to?.fullPath || router.currentRoute.value.fullPath || '/';
  if (alreadyTried) {
    console.error('[router] chunk 加载重载后仍失败，停止自动重载', error);
    ElMessage.error('页面资源加载失败，请稍后重试或联系管理员');
    return;
  }
  sessionStorage.setItem(CHUNK_RELOAD_FLAG, String(Date.now()));
  console.warn('[router] 检测到 chunk 加载失败，整页重载以恢复', error);
  window.location.assign(targetPath);
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
      const query =
        to.path === LAYOUT_PATH
          ? {}
          : { from: encodeURIComponent(to.fullPath) };
      return { path: LOGIN_PATH, query };
    }
    return;
  }
  // 已有菜单时，做轻量版本戳比对（内置 5s 节流），
  // 不一致说明运营后台已变更授权，强制刷新页面以重建动态路由。
  // 跳过 redirect 页面，避免无限跳转。
  if (!to.path.includes(REDIRECT_PATH)) {
    // 版本戳比对增加超时保护：接口变慢时不阻塞跳转，超时按"未过期"处理，
    // 避免放大切换菜单时的卡顿感。
    const outdated = await Promise.race([
      userStore.checkMenuOutdated(),
      new Promise<boolean>((resolve) => setTimeout(() => resolve(false), 3000))
    ]);
    if (outdated) {
      ElMessage.warning('企业版本授权已更新，正在重新加载菜单…');
      userStore.clearData();
      // 整页刷新可彻底重建已通过 router.addRoute 注册的动态路由，
      // 避免新旧菜单合并出现的脏路由
      window.location.replace(to.fullPath);
      return false;
    }
  }
});

router.afterEach((to) => {
  // 导航成功即清理 chunk 重载防抖标记，保证下次发版仍可触发自动恢复
  sessionStorage.removeItem(CHUNK_RELOAD_FLAG);
  if (!to.path.includes(REDIRECT_PATH) && NProgress.isStarted()) {
    setTimeout(() => {
      NProgress.done(true);
    }, 200);
  }
});

export default router;
