import { useUserStore } from '@/store/modules/user';

const DEFAULT_NAME = import.meta.env.VITE_APP_NAME;

/**
 * 修改浏览器标题
 * @param title 标题
 */
export function setPageTitle(title?: string) {
  const names: string[] = [];
  if (title) {
    names.push(title);
  }
  let appName: string | undefined;
  try {
    const userStore = useUserStore();
    appName = userStore.displayName;
  } catch {
    // pinia 尚未初始化时 fallback
  }
  const projectName = appName || DEFAULT_NAME;
  if (projectName) {
    names.push(projectName);
  }
  document.title = names.join(' - ');
}
