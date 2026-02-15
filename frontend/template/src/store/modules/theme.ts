import type { CSSProperties } from 'vue';
import { defineStore } from 'pinia';
import { cloneDeep } from 'lodash-es';
import type {
  Layout,
  SidebarLayout,
  HeaderStyle,
  SidebarStyle,
  TabStyle,
  MenuItemTrigger
} from 'ele-admin-plus/es/ele-pro-layout/types';
import type {
  SkinConfig,
  PredefinedLayout
} from 'ele-admin-plus/es/utils/theme-util';
import {
  getCacheSetting,
  cacheSetting,
  clearSetting,
  RESET_EXCLUDES,
  changeRoundedTheme,
  changeWeakMode,
  changeResponsive,
  cacheSkinBg,
  storeWallpaperFile,
  getCacheSkinConfig,
  getSkinConfig,
  releaseSkinBgCache,
  SKIN_THEME_CONFIG_EXCLUDES,
  changeTheme
} from '@/utils/theme-util';
import { tabStateProps } from './tab';

/**
 * 主题状态数据
 */
export interface ThemeState {
  collapse: boolean;
  compact: boolean;
  maximized: boolean;
  expanded: boolean;
  tabBar: boolean;
  layout: Layout;
  sidebarLayout: SidebarLayout;
  headerStyle: HeaderStyle;
  sidebarStyle: SidebarStyle;
  mixSidebarStyle: SidebarStyle;
  tabStyle: TabStyle;
  fixedHeader: boolean;
  fixedSidebar: boolean;
  fixedBody: boolean;
  fluid: boolean;
  logoInHeader: boolean;
  colorfulIcon: boolean;
  uniqueOpened: boolean;
  tabInHeader: boolean;
  sidebarCustomStyle: CSSProperties | null;
  sideboxCustomStyle: CSSProperties | null;
  sideCustomStyle: CSSProperties | null;
  headerCustomStyle: CSSProperties | null;
  tabsCustomStyle: CSSProperties | null;
  contentCustomStyle: CSSProperties | null;
  layoutCustomClass: string | null;
  layoutCustomStyle: CSSProperties | null;
  sidebarMenuProps: Record<string, any> | null;
  sideboxMenuProps: Record<string, any> | null;
  transitionName: string;
  weakMode: boolean;
  darkMode: boolean;
  color: string | null;
  contentWidth: number | null;
  roundedTheme: boolean;
  menuItemTrigger: MenuItemTrigger;
  footer: boolean;
  tabIcon: boolean;
  skinConfig: SkinConfig | null;
  layoutName: string | null;
  responsive: boolean;
}

export type ThemeStateProp = keyof ThemeState;

/**
 * 默认值
 */
const DEFAULT_STATE: ThemeState = {
  /** 是否折叠侧栏 */
  collapse: false,
  /** 侧栏一级是否紧凑风格 */
  compact: false,
  /** 内容区是否最大化 */
  maximized: false,
  /** 内容区最大化时是否不带页签栏 */
  expanded: false,
  /** 是否需要页签栏 */
  tabBar: true,
  /** 布局类型 */
  layout: 'default',
  /** 侧栏布局类型 */
  sidebarLayout: 'default',
  /** 顶栏风格 */
  headerStyle: 'light',
  /** 侧栏风格 */
  sidebarStyle: 'light',
  /** 双侧栏二级风格 */
  mixSidebarStyle: 'light',
  /** 页签风格 */
  tabStyle: 'simple',
  /** 是否固定顶栏 */
  fixedHeader: true,
  /** 是否固定侧栏 */
  fixedSidebar: true,
  /** 是否固定内容区 */
  fixedBody: true,
  /** 内容区是否撑满 */
  fluid: true,
  /** 图标是否置于顶栏 */
  logoInHeader: false,
  /** 侧栏菜单是否彩色图标 */
  colorfulIcon: false,
  /** 侧栏排他展开 */
  uniqueOpened: true,
  /** 页签是否置于顶栏 */
  tabInHeader: false,
  /** 自定义侧栏样式 */
  sidebarCustomStyle: null,
  /** 自定义双侧栏一级样式 */
  sideboxCustomStyle: null,
  /** 自定义侧栏容器样式 */
  sideCustomStyle: null,
  /** 自定义顶栏样式 */
  headerCustomStyle: null,
  /** 自定义页签栏样式 */
  tabsCustomStyle: null,
  /** 自定义内容区样式 */
  contentCustomStyle: null,
  /** 自定义布局类名 */
  layoutCustomClass: null,
  /** 自定义布局样式 */
  layoutCustomStyle: null,
  /** 侧栏菜单属性 */
  sidebarMenuProps: null,
  /** 双侧栏一级菜单属性 */
  sideboxMenuProps: null,
  /** 路由切换动画 */
  transitionName: 'slide-right',
  /** 是否色弱模式 */
  weakMode: false,
  /** 是否暗黑模式 */
  darkMode: false,
  /** 主题色 */
  color: null,
  /** 内容区宽度 */
  contentWidth: null,
  /** 是否开启圆角主题 */
  roundedTheme: true,
  /** 菜单触发模式 */
  menuItemTrigger: 'click',
  /** 是否开启全局页脚 */
  footer: true,
  /** 页签是否显示图标 */
  tabIcon: true,
  /** 皮肤背景配置 */
  skinConfig: null,
  /** 常用布局名称 */
  layoutName: null,
  /** 是否开启响应式 */
  responsive: true
};

/**
 * 主题状态管理
 */
export const useThemeStore = defineStore('theme', {
  state: (): ThemeState => {
    const state: ThemeState = cloneDeep(DEFAULT_STATE);
    // 读取本地缓存
    const cache = getCacheSetting();
    Object.keys(state).forEach((key) => {
      if (key !== 'skinConfig') {
        const value = cache[key];
        if (typeof value !== 'undefined') {
          state[key] = value;
        }
      }
    });
    return state;
  },
  actions: {
    /**
     * 批量修改配置
     * @param config 配置
     * @returns 过滤禁止修改后的配置
     */
    setThemeConfig(config?: Partial<ThemeState>) {
      const obj: Partial<ThemeState> = {};
      if (config) {
        Object.keys(config).forEach((k) => {
          const v = config[k];
          if (
            !SKIN_THEME_CONFIG_EXCLUDES.includes(k) &&
            typeof v !== 'undefined'
          ) {
            this[k] = v;
            obj[k] = v;
          }
        });
      }
      return obj;
    },
    /**
     * 修改皮肤背景或暗黑模式
     * @param value 皮肤背景配置
     * @param dark 修改暗黑模式时是否是暗黑模式
     * @param syncSkin 是否同步修改皮肤背景中的主题状态配置
     */
    async setSkinOrDark(
      value: SkinConfig | null,
      dark?: boolean,
      syncSkin?: boolean
    ) {
      const obj: Partial<ThemeState> = {};
      if (dark == null) {
        this.skinConfig = value;
        obj.skinConfig = await getSkinConfig(this.skinConfig, true, false);
        if (obj.skinConfig) {
          obj.skinConfig.layouts = void 0;
        }
      } else {
        this.darkMode = dark;
        obj.darkMode = this.darkMode;
      }
      // 同步修改主题色
      const skinColor =
        (this.darkMode
          ? this.skinConfig?.darkConfig?.color
          : this.skinConfig?.color) ?? null;
      if (skinColor != null && skinColor !== this.color) {
        this.color = skinColor;
        obj.color = this.color;
      }
      if (syncSkin) {
        // 同步修改皮肤背景中的主题状态配置
        if (dark == null && this.skinConfig == null) {
          const temp = this.setThemeConfig(cloneDeep(DEFAULT_STATE));
          Object.assign(obj, temp);
          this.layoutName = null;
        } else {
          const layouts = this.skinConfig?.layouts || [];
          const layoutItem =
            (this.layoutName
              ? layouts.find((d) => d.name === this.layoutName)
              : void 0) || layouts[0];
          const temp = this.setThemeConfig(this.getLayoutConfig(layoutItem));
          Object.assign(obj, temp);
          this.layoutName = layoutItem ? layoutItem.name : null;
        }
        obj.layoutName = this.layoutName;
      }
      cacheSetting(obj);
    },
    /**
     * 修改配置
     * @param prop 属性名
     * @param value 值
     * @param syncSkin 是否同步修改皮肤背景中的主题状态配置
     */
    async setValue(prop: ThemeStateProp, value?: any, syncSkin?: boolean) {
      if (prop === 'skinConfig') {
        if (typeof value === 'function') {
          // 皮肤背景文件特殊处理
          const skin = await value(async (file: File) => {
            const id = await storeWallpaperFile(file);
            cacheSkinBg(id, file);
            return id;
          });
          const config = await getSkinConfig(skin, false, true);
          await this.setSkinOrDark(config, void 0, syncSkin);
        } else {
          await this.setSkinOrDark(value, void 0, syncSkin);
        }
        await releaseSkinBgCache(false, this.skinConfig);
      } else if (prop === 'darkMode') {
        await this.setSkinOrDark(this.skinConfig, !!value, syncSkin);
      } else {
        this[prop as any] = value;
        cacheSetting(prop, value);
      }
      if (prop === 'color' || prop === 'darkMode' || prop === 'skinConfig') {
        // 切换主题色、暗黑模式、皮肤背景
        changeTheme(this.color, this.darkMode, this.skinConfig);
      } else if (prop === 'roundedTheme') {
        changeRoundedTheme(value); // 切换圆角主题
      } else if (prop === 'weakMode') {
        changeWeakMode(value); // 切换色弱模式
      } else if (prop === 'responsive') {
        changeResponsive(value); // 切换移动端响应式
      }
    },
    /**
     * 重置
     */
    async resetSetting() {
      Object.keys(DEFAULT_STATE).forEach((key) => {
        if (!RESET_EXCLUDES.includes(key)) {
          this[key] = cloneDeep(DEFAULT_STATE[key]);
        }
      });
      clearSetting(void 0, tabStateProps);
      await releaseSkinBgCache(true, this.skinConfig);
      changeResponsive(this.responsive);
      changeRoundedTheme(this.roundedTheme);
      changeWeakMode(this.weakMode);
      changeTheme(this.color, this.darkMode, this.skinConfig);
    },
    /**
     * 恢复主题
     */
    recoverTheme() {
      // 关闭响应式布局
      if (!this.responsive) {
        changeResponsive(false);
      }
      // 开启色弱模式
      if (this.weakMode) {
        changeWeakMode(true);
      }
      // 开启圆角主题
      if (this.roundedTheme) {
        changeRoundedTheme(true);
      }
      // 读取缓存的皮肤背景
      getCacheSkinConfig(this.skinConfig)
        .then((skin) => {
          this.skinConfig = skin;
          // 恢复主题色、暗黑模式、皮肤背景
          if (this.color || this.darkMode || this.skinConfig) {
            changeTheme(this.color, this.darkMode, this.skinConfig);
          }
        })
        .catch((e) => {
          console.error(e);
        });
    },
    /**
     * 获取布局对应的主题配置
     * @param layoutItem 布局
     */
    getLayoutConfig(layoutItem: PredefinedLayout) {
      const traditionalConfig = this.roundedTheme
        ? void 0
        : layoutItem.traditionalThemeConfig;
      return { ...(layoutItem.config || {}), ...(traditionalConfig || {}) };
    },
    /**
     * 修改常用布局
     * @param layoutItem 布局
     */
    setLayout(layoutItem: PredefinedLayout) {
      this.layoutName = layoutItem.name;
      const obj: Partial<ThemeState> = this.setThemeConfig(
        this.getLayoutConfig(layoutItem)
      );
      obj.layoutName = this.layoutName;
      cacheSetting(obj);
    }
  }
});
