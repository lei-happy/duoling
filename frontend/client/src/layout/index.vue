<template>
  <ele-pro-layout
    :menus="menus"
    :tabs="tabs"
    :collapse="collapse"
    :compact="compact"
    :maximized="maximized"
    :expanded="expanded"
    :tab-bar="tabBar ? (tabInHeader ? 'header' : true) : false"
    :breadcrumb="layout === 'default' && (!tabBar || !tabInHeader)"
    :layout="layout"
    :sidebar-layout="sidebarLayout"
    :header-style="headerStyle"
    :sidebar-style="sidebarStyle"
    :mix-sidebar-style="mixSidebarStyle"
    :tab-style="tabStyle"
    :fixed-header="fixedHeader"
    :fixed-sidebar="fixedSidebar"
    :fixed-body="fixedBody"
    :fluid="fluid"
    :logo-in-header="logoInHeader"
    :colorful-icon="colorfulIcon"
    :sidebox-menu-props="{
      colorful: colorfulIcon,
      ...(sideboxMenuProps || {})
    }"
    :sidebar-menu-props="{
      ...(sidebarMenuProps || {}),
      colorful: sidebarLayout === 'mix' ? sidebarMenuProps?.colorful : void 0
    }"
    :unique-opened="uniqueOpened"
    :fixed-home="fixedHome"
    :home-path="HOME_PATH"
    :redirect-path="REDIRECT_PATH"
    :locale="locale"
    :i18n="i18n"
    :tab-sortable="!mobileDevice"
    :tab-context-menu="{
      popperOptions: {
        strategy: 'fixed',
        modifiers: [{ name: 'offset', options: { offset: [0, 8] } }]
      },
      menuStyle: tabDropdownMenuStyle
    }"
    :tab-context-menus="getTabContext"
    :nav-trigger="layout === 'top' ? void 0 : menuItemTrigger"
    :box-trigger="menuItemTrigger"
    :keep-alive="pageKeepAlive"
    :transition-name="transitionName"
    :ellipsis-props="{ hideTimeout: 800 }"
    :sidebar-custom-style="sidebarCustomStyle"
    :sidebox-custom-style="sideboxCustomStyle"
    :side-custom-style="sideCustomStyle"
    :header-custom-style="headerCustomStyle"
    :tabs-custom-style="tabsCustomStyle"
    :content-custom-style="contentCustomStyle"
    :class="layoutCustomClass"
    :style="layoutCustomStyle"
    :responsive="responsive"
    @update:collapse="updateCollapse"
    @update:maximized="updateMaximized"
    @tabAdd="addPageTab"
    @tabClick="handleTabClick"
    @tabRemove="removePageTab"
    @tabContextMenu="handleTabContextMenu"
    @tabSortChange="setPageTabs"
    @bodySizeChange="handleBodySizeChange"
  >
    <upgrade-to-pro-banner />
    <router-layout />
    <!-- logo -->
    <template #logo>
      <img src="@/assets/logo.svg" />
    </template>
    <template #logoTitle>
      <h1>{{ userStore.displayName || DEFAULT_NAME }}</h1>
    </template>
    <!-- 顶栏左侧按钮 -->
    <template #left="{ sidebar }">
      <!-- 折叠侧栏 -->
      <layout-tool v-if="sidebar" @click="updateCollapse(!collapse)">
        <el-icon style="transform: scale(1.14)">
          <MenuUnfoldOutlined v-if="collapse" />
          <MenuFoldOutlined v-else />
        </el-icon>
      </layout-tool>
      <!-- 刷新 -->
      <layout-tool
        :class="{ 'hidden-sm-and-down': tabBar && tabInHeader }"
        @click="reloadPageTab()"
      >
        <el-icon style="transform: scale(1.09)">
          <ReloadOutlined />
        </el-icon>
      </layout-tool>
    </template>
    <!-- 顶栏右侧按钮 -->
    <template #right>
      <header-right />
    </template>
    <!-- 页签栏右侧下拉菜单 -->
    <template v-if="tabBar && !tabInHeader" #tabExtra="{ active }">
      <tab-dropdown
        :items="getTabContext(void 0, active)"
        :dropdown-props="{
          popperOptions: {
            strategy: 'fixed',
            modifiers: [{ name: 'offset', options: { offset: [12, 8] } }]
          },
          menuStyle: tabDropdownMenuStyle
        }"
        @menuClick="(key) => handleTabDropdownMenu(key, active)"
      />
    </template>
    <!-- 折叠双侧栏一级 -->
    <template #boxBottom>
      <div :style="{ flexShrink: 0, padding: roundedTheme ? '4px 8px' : 0 }">
        <layout-tool style="height: 32px" @click="updateCompact(!compact)">
          <el-icon style="transform: scale(1.05)">
            <MenuUnfoldOutlined v-if="compact" />
            <MenuFoldOutlined v-else />
          </el-icon>
        </layout-tool>
      </div>
    </template>
    <!-- 全局页脚 -->
    <template v-if="footer" #footer>
      <page-footer />
    </template>
    <!-- 菜单图标：支持自定义 SVG 及清新主题图片 -->
    <template #icon="{ icon }">
      <menu-icon :icon="icon" img-class="el-icon" />
    </template>
    <template v-if="isSimpleTheme" #tabHome>
      <menu-icon
        v-if="tabIcon"
        icon="IconProHomeOutlined"
        :img-style="{ margin: '0 4px 0 -4px', verticalAlign: '-5px' }"
      />
      <span>{{ t('layout.home') }}</span>
    </template>
    <!-- 页签标题 -->
    <template #tabTitle="{ label, item }">
      <menu-icon
        v-if="tabIcon"
        :icon="item.meta?.icon"
        :component-props="item.meta?.props?.iconProps"
        component-class="ele-tab-icon"
        :component-style="{ marginRight: '4px' }"
        :icon-style="item.meta?.props?.iconStyle"
        :img-style="{ margin: '0 4px 0 -4px', verticalAlign: '-5px' }"
      />
      <span>{{ label }}</span>
    </template>
  </ele-pro-layout>
  <SystemWatermarkOverlay
    v-if="watermarkReady && watermarkEnabled"
    :key="watermarkRenderKey"
    :content="watermarkContent"
    :gap="watermarkGap"
    :rotate="watermarkRotate"
    :font="watermarkFont"
    :z-index="watermarkZIndex"
    fixed
  />
  <!-- 内容全屏退出按钮 -->
  <el-icon
    v-if="maximized ? (!tabBar || tabInHeader ? true : expanded) : false"
    class="ele-layout-fullscreen-icon"
    @click="updateMaximized(false)"
  >
    <FullscreenExitOutlined />
  </el-icon>
</template>

<script lang="ts" setup>
  import { markRaw, onMounted, onBeforeUnmount } from 'vue';
  import { useRouter } from 'vue-router';
  import { storeToRefs } from 'pinia';
  import { useI18n } from 'vue-i18n';
  import { LayoutTool, TabDropdown } from 'ele-admin-plus';
  import type {
    MenuI18n,
    TabItemEventOption,
    BodySizeChangeOption
  } from 'ele-admin-plus/es/ele-pro-layout/types';
  import type { DropdownItem } from 'ele-admin-plus/es/ele-dropdown/types';
  import type { TabPaneItem } from 'ele-admin-plus/es/ele-tabs/types';
  import {
    MenuFoldOutlined,
    MenuUnfoldOutlined,
    ReloadOutlined,
    ExpandOutlined,
    CompressOutlined,
    CloseOutlined,
    ArrowLeftOutlined,
    ArrowRightOutlined,
    MinusCircleOutlined,
    CloseCircleOutlined,
    FullscreenOutlined,
    FullscreenExitOutlined,
    ShareOutlined,
    PinOutlined,
    UnpinOutlined
  } from '@/components/icons';
  import { HOME_PATH, REDIRECT_PATH } from '@/config/setting';
  import { useUserStore } from '@/store/modules/user';
  import { useTabStore } from '@/store/modules/tab';
  import { useThemeStore } from '@/store/modules/theme';
  import { useMobileDevice } from '@/utils/use-mobile';
  import { usePageTab } from '@/utils/use-page-tab';
  import { useIsSimpleTheme } from '@/components/IconSelect/util';
  import MenuIcon from '@/components/IconSelect/components/menu-icon.vue';
  import RouterLayout from '@/components/RouterLayout/index.vue';
  import UpgradeToProBanner from '@/components/UpgradeToProBanner/index.vue';
  import HeaderRight from './components/header-right.vue';
  import PageFooter from './components/page-footer.vue';
  import { useMenuVersionWatcher } from '@/utils/use-menu-version-watcher';
  import { useWatermarkConfig } from '@/utils/use-watermark-config';
  import SystemWatermarkOverlay from '@/components/SystemWatermarkOverlay/index.vue';
  const DEFAULT_NAME = import.meta.env.VITE_APP_NAME;

  defineOptions({ name: 'Layout' });

  // 监听菜单版本戳变化（轮询 + 标签页可视性 + 窗口 focus）
  // 覆盖"用户停留在某页不切路由"时运营后台改授权的场景
  useMenuVersionWatcher();

  const {
    watermarkReady,
    watermarkEnabled,
    watermarkContent,
    watermarkGap,
    watermarkRotate,
    watermarkFont,
    watermarkZIndex,
    watermarkRenderKey,
    loadWatermarkConfig
  } = useWatermarkConfig();

  onMounted(() => {
    loadWatermarkConfig();
  });

  const router = useRouter();
  const { push, resolve } = router;
  const { t, locale } = useI18n();
  const {
    addPageTab,
    removePageTab,
    removeAllPageTab,
    removeLeftPageTab,
    removeRightPageTab,
    removeOtherPageTab,
    reloadPageTab,
    setPageTabs,
    setPageTab
  } = usePageTab();

  // 离开「模块总览」页时自动关闭其页签，避免多次切换一级菜单后
  // 页签区堆积一排「总览」。总览作为一次性入口，最多保留当前一个。
  const removeOverviewTabRef = router.afterEach((to, from) => {
    if (!from.meta?.overviewModule) {
      return;
    }
    if (from.path === to.path || to.path.includes(REDIRECT_PATH)) {
      return;
    }
    const activeKey = to.meta?.tabUnique === false ? to.fullPath : to.path;
    removePageTab({ key: from.path, active: activeKey }, false);
  });

  onBeforeUnmount(() => {
    removeOverviewTabRef?.();
  });

  const { mobileDevice } = useMobileDevice();
  const userStore = useUserStore();
  const tabStore = useTabStore();
  const themeStore = useThemeStore();

  /** 菜单数据 */
  const { menus } = storeToRefs(userStore);

  /** 页签数据 */
  const { tabs, fixedHome, pageKeepAlive } = storeToRefs(tabStore);

  /** 布局风格 */
  const {
    collapse,
    compact,
    maximized,
    expanded,
    tabBar,
    layout,
    sidebarLayout,
    headerStyle,
    sidebarStyle,
    mixSidebarStyle,
    tabStyle,
    fixedHeader,
    fixedSidebar,
    fixedBody,
    fluid,
    logoInHeader,
    colorfulIcon,
    transitionName,
    uniqueOpened,
    tabInHeader,
    sidebarCustomStyle,
    sideboxCustomStyle,
    sideCustomStyle,
    headerCustomStyle,
    tabsCustomStyle,
    contentCustomStyle,
    layoutCustomClass,
    layoutCustomStyle,
    sidebarMenuProps,
    sideboxMenuProps,
    roundedTheme,
    menuItemTrigger,
    footer,
    tabIcon,
    responsive
  } = storeToRefs(themeStore);

  /** 是否是清新主题 */
  const { isSimpleTheme } = useIsSimpleTheme();

  /** 侧栏折叠切换 */
  const updateCollapse = (value: boolean) => {
    themeStore.setValue('collapse', value).catch((e) => console.error(e));
  };

  /** 双侧栏一级折叠切换 */
  const updateCompact = (value: boolean) => {
    themeStore.setValue('compact', value).catch((e) => console.error(e));
  };

  /** 内容区全屏切换 */
  const updateMaximized = async (value: boolean, fullscreen?: boolean) => {
    try {
      if (value) {
        await themeStore.setValue('expanded', !!fullscreen);
      }
      await themeStore.setValue('maximized', value);
    } catch (e) {
      console.error(e);
    }
  };

  /** 页签点击事件 */
  const handleTabClick = (option: TabItemEventOption) => {
    const { key, active, item } = option;
    const path = item?.fullPath || key;
    if (key !== active && path) {
      push(path);
    }
  };

  /** 内容区尺寸改变事件 */
  const handleBodySizeChange = ({ width }: BodySizeChangeOption) => {
    themeStore
      .setValue('contentWidth', width ?? null)
      .catch((e) => console.error(e));
  };

  /** 页签右键菜单 */
  const getTabContext = (item?: TabPaneItem, active?: string) => {
    const items: DropdownItem[] = [
      {
        title: t('layout.tabs.reload'),
        command: 'reload',
        icon: markRaw(ReloadOutlined),
        iconStyle: { transform: 'scale(0.98)' }
      },
      {
        title: t('layout.tabs.close'),
        command: 'close',
        icon: markRaw(CloseOutlined)
      }
    ];
    if (maximized.value) {
      items.push({
        title: t('layout.tabs.maximizedExit'),
        command: 'maximizedExit',
        icon: markRaw(CompressOutlined),
        divided: true
      });
    } else {
      items.push({
        title: t('layout.tabs.maximized'),
        command: 'maximized',
        icon: markRaw(ExpandOutlined),
        iconStyle: { transform: 'scale(0.96)' },
        divided: true
      });
    }
    if (!tabInHeader.value) {
      items.push({
        title: t('layout.tabs.fullscreen'),
        command: 'fullscreen',
        icon: markRaw(FullscreenOutlined),
        iconStyle: { transform: 'scale(0.98)' }
      });
    }
    items.push({
      title: t('layout.tabs.closeLeft'),
      command: 'left',
      icon: markRaw(ArrowLeftOutlined),
      divided: true
    });
    items.push({
      title: t('layout.tabs.closeRight'),
      command: 'right',
      icon: markRaw(ArrowRightOutlined)
    });
    items.push({
      title: t('layout.tabs.closeOther'),
      command: 'other',
      icon: markRaw(MinusCircleOutlined)
    });
    items.push({
      title: t('layout.tabs.closeAll'),
      command: 'all',
      icon: markRaw(CloseCircleOutlined)
    });
    const tab =
      item || (active ? tabs.value.find((t) => t.key === active) : void 0);
    const home = (tab as any)?.home ?? tab?.meta?.home;
    if (
      tab &&
      !(fixedHome.value && home) &&
      !(tabs.value.length === 1 && home)
    ) {
      if (tab.closable) {
        items.push({
          title: t('layout.tabs.pin'),
          command: 'pin',
          icon: markRaw(PinOutlined),
          divided: true
        });
      } else {
        items.push({
          title: t('layout.tabs.unpin'),
          command: 'unpin',
          icon: markRaw(UnpinOutlined),
          divided: true
        });
      }
    }
    items.push({
      title: t('layout.tabs.blank'),
      command: 'blank',
      icon: markRaw(ShareOutlined),
      iconStyle: { transform: 'scale(0.9)' },
      divided: !items[items.length - 1]?.divided
    });
    return items;
  };

  /** 页签右键菜单点击事件 */
  const handleTabContextMenu = (option: TabItemEventOption) => {
    const { command, key, item, active } = option;
    if (command === 'reload') {
      reloadPageTab({ fullPath: item?.fullPath || key });
    } else if (command === 'close') {
      removePageTab({ key, active });
    } else if (command === 'left') {
      removeLeftPageTab({ key, active });
    } else if (command === 'right') {
      removeRightPageTab({ key, active });
    } else if (command === 'other') {
      removeOtherPageTab({ key, active });
    } else if (command === 'all') {
      removeAllPageTab({ key, active });
    } else if (command === 'maximized') {
      updateMaximized(true);
    } else if (command === 'maximizedExit') {
      updateMaximized(false);
    } else if (command === 'fullscreen') {
      updateMaximized(true, true);
    } else if (command === 'blank') {
      window.open(resolve(item?.fullPath || '/').href);
    } else if (command === 'pin') {
      setPageTab({ path: item?.fullPath || key, closable: false });
    } else if (command === 'unpin') {
      setPageTab({ path: item?.fullPath || key, closable: true });
    }
  };

  /** 页签栏右侧下拉菜单点击事件 */
  const handleTabDropdownMenu = (command: string, active: string) => {
    if (command === 'reload') {
      reloadPageTab();
    } else if (command === 'blank') {
      window.open(location.href);
    } else {
      handleTabContextMenu({ command, key: active, active });
    }
  };

  /** 页签栏下拉菜单样式调整 */
  const tabDropdownMenuStyle = {
    '--ele-dropdown-item-padding': '0 18px',
    '--ele-dropdown-item-height': '30px',
    '--ele-dropdown-item-margin': '0px',
    '--ele-dropdown-divider-margin': '3px 0',
    '--ele-dropdown-icon-margin': '0 12px 0 -4px',
    '--ele-dropdown-icon-size': '15px'
  };

  /** 菜单标题国际化 */
  const i18n: MenuI18n = ({ menu, locale, tab }) => {
    if (locale) {
      if (tab && tab.meta?.lang && tab.meta.lang[locale]) {
        return tab.meta.lang[locale];
      }
      if (menu?.meta?.lang && menu.meta.lang[locale]) {
        return menu.meta.lang[locale];
      }
    }
    return menu?.meta?.title;
  };
</script>
