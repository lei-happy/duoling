import { createRouter, createWebHistory } from 'vue-router';
import { routes } from './routes';
import { useUserStore } from '@/store/user';
import { showToast } from 'vant';

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  }
});

router.beforeEach(async (to) => {
  const appName = import.meta.env.VITE_APP_NAME || '智途司机端';
  document.title = to.meta?.title ? `${to.meta.title} · ${appName}` : appName;

  const user = useUserStore();

  // 无需登录的路由：login / sms-login / 404
  if (to.meta?.noAuth) {
    return true;
  }

  if (!user.isLoggedIn) {
    return { name: 'Login', query: { redirect: to.fullPath } };
  }

  // 仅需 token、未选企业时允许通过（如 /tenant-select）
  if (to.meta?.requireTokenOnly) {
    return true;
  }

  // 已登录但未选择企业 → 跳企业选择
  if (!user.currentTenantCode) {
    return { name: 'TenantSelect', query: { redirect: to.fullPath } };
  }

  // 首次登录强制修改密码
  if (user.needForceChangePwd && to.name !== 'ChangePassword') {
    showToast('首次登录请先修改密码');
    return { name: 'ChangePassword' };
  }

  return true;
});

router.onError((err) => {
  if (err?.message?.includes('Failed to fetch dynamically imported module')) {
    showToast('版本已更新，正在重载');
    setTimeout(() => window.location.reload(), 800);
  }
});

export default router;
