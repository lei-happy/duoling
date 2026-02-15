import { defineStore } from 'pinia';
import { cloneDeep } from 'lodash-es';
import type {
  TabItem,
  TabItemEventOption
} from 'ele-admin-plus/es/ele-pro-layout/types';
import {
  getCacheSetting,
  cacheSetting,
  clearSetting,
  RESET_EXCLUDES
} from '@/utils/theme-util';

/**
 * 页签状态数据
 */
export interface TabState {
  tabs: TabItem[];
  fixedHome: boolean;
  tabsCache: boolean;
  pageKeepAlive: boolean;
}

export type TabStateProp = keyof TabState;

/**
 * 关闭页签返回结果
 */
export interface TabRemoveResult {
  /** 关闭后要跳转的地址 */
  path?: string;
  /** 关闭后是否跳转到首页 */
  home?: boolean;
}

export type TabRemoveReturn = Promise<TabRemoveResult>;

/**
 * 默认值
 */
const DEFAULT_STATE: TabState = {
  /** 页签数据 */
  tabs: [],
  /** 固定主页页签 */
  fixedHome: true,
  /** 刷新是否保留已打开页签 */
  tabsCache: false,
  /** 切换路由是否缓存 */
  pageKeepAlive: true
};

/**
 * 页签状态管理
 */
export const useTabStore = defineStore('tab', {
  state: (): TabState => {
    const state: TabState = cloneDeep(DEFAULT_STATE);
    // 读取本地缓存
    const cache = getCacheSetting();
    Object.keys(state).forEach((key) => {
      const value = cache[key];
      if (typeof value !== 'undefined') {
        state[key] = value;
      }
    });
    if (!state.tabsCache) {
      state.tabs = [];
    }
    return state;
  },
  getters: {
    /** 需要缓存的路由组件 */
    keepAliveInclude(): string[] {
      if (!this.pageKeepAlive || !this.tabs) {
        return [];
      }
      const components = new Set<string>();
      this.tabs.forEach((t) => {
        if (t.meta?.keepAlive !== false && !t.refresh && t.components) {
          t.components.forEach((c) => {
            if (typeof c === 'string' && c) {
              components.add(c);
            }
          });
        }
      });
      return Array.from(components);
    }
  },
  actions: {
    /**
     * 修改配置
     * @param prop 属性名
     * @param value 值
     */
    setValue(prop: TabStateProp, value?: any) {
      if (prop === 'tabs') {
        this.tabs = (value as TabItem[]).sort(
          (a, b) => Number(!!a.closable) - Number(!!b.closable)
        );
      } else {
        this[prop] = value;
      }
      if (prop !== 'tabs' || this.tabsCache) {
        cacheSetting(prop, value);
      }
      // 页签缓存开关切换后同时更新缓存的页签数据
      if (prop === 'tabsCache') {
        cacheSetting('tabs', value ? this.tabs : void 0);
      }
    },
    /**
     * 重置
     */
    resetSetting() {
      Object.keys(DEFAULT_STATE).forEach((key) => {
        if (!RESET_EXCLUDES.includes(key)) {
          this[key] = cloneDeep(DEFAULT_STATE[key]);
        }
      });
      clearSetting(tabStateProps);
    },
    /**
     * 添加页签或更新页签数据
     * @param data 页签数据
     */
    tabAdd(data: TabItem) {
      const i = this.tabs.findIndex((d) => d.key === data.key);
      if (i === -1) {
        const temps = [...this.tabs, data];
        this.setValue('tabs', temps);
      } else if (data.fullPath !== this.tabs[i].fullPath) {
        const temps = [...this.tabs];
        temps[i] = data;
        this.setValue('tabs', temps);
      }
    },
    /**
     * 关闭页签
     */
    async tabRemove({ key, active }: TabItemEventOption): TabRemoveReturn {
      const i = this.tabs.findIndex((t) => t.key === key || t.fullPath === key);
      if (i === -1) {
        return {};
      }
      const t = this.tabs[i];
      if (
        !t.closable ||
        (t.home && (this.tabs.length === 1 || this.fixedHome))
      ) {
        return Promise.reject();
      }
      const path = this.tabs[i + (i === 0 ? 1 : -1)]?.fullPath;
      this.setValue(
        'tabs',
        this.tabs.filter((_d, j) => j !== i)
      );
      return t.key === active ? { path, home: !path } : {};
    },
    /**
     * 关闭左侧页签
     */
    async tabRemoveLeft({ key, active }: TabItemEventOption): TabRemoveReturn {
      let index = -1; // 选中页签的索引
      for (let i = 0; i < this.tabs.length; i++) {
        if (this.tabs[i].key === active) {
          index = i;
        }
        if (this.tabs[i].key === key) {
          if (i === 0) {
            break;
          }
          const temp = this.tabs.filter((d, j) => !d.closable && j < i);
          if (temp.length === i) {
            break;
          }
          const path = index === -1 ? void 0 : this.tabs[i].fullPath;
          this.setValue('tabs', temp.concat(this.tabs.slice(i)));
          return { path };
        }
      }
      return Promise.reject();
    },
    /**
     * 关闭右侧页签
     */
    async tabRemoveRight({ key, active }: TabItemEventOption): TabRemoveReturn {
      let index = -1; // 选中页签的索引
      for (let i = 0; i < this.tabs.length; i++) {
        if (this.tabs[i].key === active) {
          index = i;
        }
        if (this.tabs[i].key === key) {
          if (i === this.tabs.length - 1) {
            break;
          }
          const temp = this.tabs.filter((d, j) => !d.closable && j > i);
          if (temp.length === this.tabs.length - i - 1) {
            break;
          }
          const path = index === -1 ? this.tabs[i].fullPath : void 0;
          this.setValue('tabs', this.tabs.slice(0, i + 1).concat(temp));
          return { path };
        }
      }
      return Promise.reject();
    },
    /**
     * 关闭其它页签
     */
    async tabRemoveOther({ key, active }: TabItemEventOption): TabRemoveReturn {
      let path: string | undefined; // 关闭后跳转的地址
      const temps = this.tabs.filter((d) => {
        if (d.key === key) {
          path = d.fullPath;
        }
        return !d.closable || d.key === key;
      });
      if (temps.length === this.tabs.length) {
        return Promise.reject();
      }
      this.setValue('tabs', temps);
      return key === active ? {} : { path };
    },
    /**
     * 关闭全部页签
     */
    async tabRemoveAll({ active }: TabItemEventOption): TabRemoveReturn {
      if (this.tabs.length === 1 && this.tabs[0].home) {
        return Promise.reject();
      }
      const temps = this.tabs.filter(
        (t) => !t.closable || (t.home && this.fixedHome)
      );
      if (temps.length === this.tabs.length) {
        return Promise.reject();
      }
      const t = active ? this.tabs.find((d) => d.key === active) : void 0;
      const jump = t != null && t.closable === true; // 关闭后是否跳转
      if (!temps.length) {
        const h = this.tabs.find((d) => d.home);
        if (!h) {
          this.setValue('tabs', []);
          return { home: true };
        }
        this.setValue('tabs', [h]);
        return { home: t?.home ? void 0 : true };
      }
      this.setValue('tabs', temps);
      return { path: jump ? temps[0].fullPath : void 0 };
    },
    /**
     * 修改页签
     * @param data 页签数据
     */
    tabSetItem(data: TabItem) {
      if (!data.key && !data.fullPath) {
        if (!data.path) {
          return;
        }
        this.tabs.forEach((d) => {
          if (data.path === d.path) {
            this.tabSetItem({ ...data, key: d.key });
          }
        });
        return;
      }
      const k = data.key ? 'key' : 'fullPath';
      const i = this.tabs.findIndex((d) => data[k] === d[k]);
      if (i === -1) {
        return;
      }
      const item = { ...this.tabs[i] };
      if (data.title) {
        const title = data.title;
        item.title = title;
        if (item.meta) {
          item.meta.lang = { zh_CN: title, zh_TW: title, en: title };
        }
      }
      if (typeof data.closable === 'boolean') {
        item.closable = data.closable;
      }
      if (typeof data.refresh === 'boolean') {
        item.refresh = data.refresh;
      }
      if (data.components) {
        item.components = data.components;
      }
      const temps = [...this.tabs];
      temps[i] = item;
      this.setValue('tabs', temps);
    }
  }
});

export const tabStateProps = Object.keys(DEFAULT_STATE) as TabStateProp[];
