import { onBeforeUnmount, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/store/modules/user';

/**
 * 菜单版本戳监听
 *
 * 背景：
 * - 仅靠 router.beforeEach 检查 menuVersion 只能覆盖"用户切换路由"场景，
 *   如果用户停留在某个页面不动，运营在后台改了授权（assign_product/remove_product/
 *   assign_features 等），客户端永远不会感知。
 *
 * 本工具在 Layout 挂载时启动两路触发器：
 * 1. 定时轮询：默认 60 秒一次（轻量接口 /auth/menu-version）；
 * 2. 标签页可视性 / 窗口 focus 事件：用户切回标签页时立即检查一次，覆盖
 *    "运营改完后，用户切回客户端 tab" 这种最常见的场景；
 *
 * 检测到 menuVersion 不一致时，复用 store.checkMenuOutdated 的判断结果，弹提示
 * 并执行整页刷新，让动态路由彻底重建。
 *
 * 节流机制：复用 store 内部 5 秒节流，避免短时间内多次事件叠加重复请求。
 */

const DEFAULT_POLL_INTERVAL = 60_000;

export function useMenuVersionWatcher(options: { intervalMs?: number } = {}) {
  const userStore = useUserStore();
  const intervalMs = options.intervalMs ?? DEFAULT_POLL_INTERVAL;

  let timer: ReturnType<typeof setInterval> | null = null;

  const reloadIfOutdated = async () => {
    if (!userStore.menus) return;
    try {
      const outdated = await userStore.checkMenuOutdated();
      if (outdated) {
        ElMessage.warning('企业版本授权已更新，正在重新加载菜单…');
        userStore.clearData();
        window.location.reload();
      }
    } catch (e) {
      console.warn('[menu-version-watcher] 检查失败，忽略本次轮询', e);
    }
  };

  const handleVisibilityChange = () => {
    if (document.visibilityState === 'visible') {
      reloadIfOutdated();
    }
  };

  const handleFocus = () => {
    reloadIfOutdated();
  };

  onMounted(() => {
    timer = setInterval(reloadIfOutdated, intervalMs);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);
  });

  onBeforeUnmount(() => {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
    document.removeEventListener('visibilitychange', handleVisibilityChange);
    window.removeEventListener('focus', handleFocus);
  });
}
