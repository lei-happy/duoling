const PROJECT_NAME = import.meta.env.VITE_APP_NAME;

/**
 * 修改浏览器标题
 * @param title 标题
 */
export function setPageTitle(title?: string) {
  const names: string[] = [];
  if (title) {
    names.push(title);
  }
  if (PROJECT_NAME) {
    names.push(PROJECT_NAME);
  }
  document.title = names.join(' - ');
}
