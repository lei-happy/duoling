import { useRouter, useRoute } from 'vue-router';
import { EleMessage } from 'ele-admin-plus';
import type {
  TabItem,
  TabItemEventOption
} from 'ele-admin-plus/es/ele-pro-layout/types';
import { useTabStore } from '@/store/modules/tab';
import type { TabRemoveResult } from '@/store/modules/tab';
import { HOME_PATH, LAYOUT_PATH, REDIRECT_PATH } from '@/config/setting';

/**
 * 页签操作hook
 */
export function usePageTab() {
  const route = useRoute();
  const { push, replace } = useRouter();
  const tabStore = useTabStore();

  /**
   * 获取主页路由地址
   */
  const getHomeRoutePath = () => {
    return HOME_PATH || LAYOUT_PATH;
  };

  /**
   * 获取当前路由对应的页签key
   */
  const getRouteTabKey = () => {
    const { path, fullPath, meta } = route;
    return meta.tabUnique === false ? fullPath : path;
  };

  /**
   * 当前路由对应的页签key
   */
  const routeTabKey = getRouteTabKey();

  /**
   * 刷新当前路由
   */
  const reloadPageTab = (option?: TabReloadOptions) => {
    if (route.path.includes(REDIRECT_PATH)) {
      return;
    }
    if (!option || !option.fullPath) {
      // 刷新当前路由
      setPageTab({ fullPath: route.fullPath, refresh: true });
      replace({ path: REDIRECT_PATH + route.path, query: route.query });
    } else {
      // 刷新指定页签
      setPageTab({ fullPath: option.fullPath, refresh: true });
      replace(REDIRECT_PATH + option.fullPath);
    }
  };

  /**
   * 关闭当前页签
   */
  const finishPageTab = () => {
    removePageTab({ key: routeTabKey, active: getRouteTabKey() });
  };

  /**
   * 关闭指定页签
   */
  const removePageTab = (option: TabItemEventOption, tip?: boolean) => {
    tabStore
      .tabRemove(option)
      .then((result) => {
        handleRemoveDone(result);
      })
      .catch(() => {
        if (tip !== false) {
          EleMessage.error({ message: '当前页签不可关闭', plain: true });
        }
      });
  };

  /**
   * 关闭左侧页签
   */
  const removeLeftPageTab = (option: TabItemEventOption, tip?: boolean) => {
    tabStore
      .tabRemoveLeft(option)
      .then((result) => {
        handleRemoveDone(result);
      })
      .catch(() => {
        if (tip !== false) {
          EleMessage.error({ message: '左侧没有可关闭的页签', plain: true });
        }
      });
  };

  /**
   * 关闭右侧页签
   */
  const removeRightPageTab = (option: TabItemEventOption, tip?: boolean) => {
    tabStore
      .tabRemoveRight(option)
      .then((result) => {
        handleRemoveDone(result);
      })
      .catch(() => {
        if (tip !== false) {
          EleMessage.error({ message: '右侧没有可关闭的页签', plain: true });
        }
      });
  };

  /**
   * 关闭其它页签
   */
  const removeOtherPageTab = (option: TabItemEventOption, tip?: boolean) => {
    tabStore
      .tabRemoveOther(option)
      .then((result) => {
        handleRemoveDone(result);
      })
      .catch(() => {
        if (tip !== false) {
          EleMessage.error({ message: '没有可关闭的页签', plain: true });
        }
      });
  };

  /**
   * 关闭全部页签
   */
  const removeAllPageTab = (option: TabItemEventOption, tip?: boolean) => {
    tabStore
      .tabRemoveAll(option)
      .then((result) => {
        handleRemoveDone(result);
      })
      .catch(() => {
        if (tip !== false) {
          EleMessage.error({ message: '没有可关闭的页签', plain: true });
        }
      });
  };

  /**
   * 页签移除方法完成操作
   */
  const handleRemoveDone = ({ path, home }: TabRemoveResult) => {
    if (path) {
      if (route.fullPath !== path) {
        push(path);
      }
    } else if (home) {
      push(getHomeRoutePath());
    }
  };

  /**
   * 更新页签数据
   * @param data 页签数据
   */
  const setPageTabs = (data: TabItem[]) => {
    tabStore.setValue('tabs', data);
  };

  /**
   * 登录成功后清空页签
   */
  const cleanPageTabs = () => {
    setPageTabs([]);
  };

  /**
   * 添加页签
   * @param data 页签数据
   */
  const addPageTab = (data: TabItem) => {
    tabStore.tabAdd(data);
  };

  /**
   * 修改页签
   * @param data 页签数据
   */
  const setPageTab = (data: TabItem) => {
    tabStore.tabSetItem(data);
  };

  /**
   * 修改当前页签标题
   * @param title 标题
   */
  const setPageTabTitle = (title: string) => {
    setPageTab({ key: routeTabKey, title });
  };

  /**
   * 登录成功后跳转首页
   * @param from 登录前的地址, 有则跳转到此地址, 没有则跳转到默认首页
   */
  const goHomeRoute = (from?: string | null) => {
    replace(from ? decodeURIComponent(from) : getHomeRoutePath());
  };

  return {
    reloadPageTab,
    finishPageTab,
    removePageTab,
    removeLeftPageTab,
    removeRightPageTab,
    removeOtherPageTab,
    removeAllPageTab,
    setPageTabs,
    cleanPageTabs,
    addPageTab,
    setPageTab,
    setPageTabTitle,
    getRouteTabKey,
    getHomeRoutePath,
    goHomeRoute,
    routeTabKey
  };
}

/**
 * 刷新页签参数类型
 */
export interface TabReloadOptions {
  /** 路由地址 */
  fullPath?: string;
}
