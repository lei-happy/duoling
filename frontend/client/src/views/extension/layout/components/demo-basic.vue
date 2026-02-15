<template>
  <ele-card header="基础用法" :body-style="{ padding: '12px' }">
    <frame-card :style="mobile ? { maxWidth: '420px' } : {}">
      <div
        :style="{
          height: '520px',
          overflow: 'auto',
          minWidth: mobile ? void 0 : '800px'
        }"
        class="demo-layout-wrapper"
      >
        <ele-admin-layout
          ref="layoutRef"
          :height="520"
          :header-menus="headerMenus"
          :header-active="headerActive"
          :sidebar-menus="sidebarMenus"
          :sidebar-active="sidebarActive"
          :sidebox-menus="sideboxMenus"
          :sidebox-active="sideboxActive"
          :tabs="tabs"
          :tab-active="tabActive"
          :levels="levels"
          :layout="layout"
          :sidebar-layout="sidebarLayout"
          :tab-bar="tabBar"
          :breadcrumb="mobile ? false : breadcrumb"
          :header-style="headerStyle"
          :sidebar-style="sidebarStyle"
          :mix-sidebar-style="mixSidebarStyle"
          :tab-style="tabStyle"
          :fixed-header="fixedHeader"
          :fixed-sidebar="fixedSidebar"
          :fixed-body="fixedBody"
          :logo-in-header="logoInHeader"
          :maximized="maximized"
          v-model:collapse="collapse"
          :compact="compact"
          :mobile="mobile"
          :fixed-home="true"
          :back-top="false"
          :menu-scroll-to-active="false"
          :sidebar-menu-props="{ textEllipsisTooltip: true }"
          :style="{
            '--ele-header-height': headerHeight + 'px',
            '--ele-sidebar-width': sidebarWidth + 'px',
            '--ele-sidebox-width': sideboxWidth + 'px',
            '--ele-sidebar-mix-width': sidebarMixWidth + 'px'
          }"
        >
          <template #logo>
            <img src="@/assets/logo.svg" />
          </template>
          <template #logoTitle>
            <h1>Ele Admin</h1>
          </template>
          <template v-if="layout !== 'top'" #left>
            <layout-tool @click="collapse = !collapse">
              <el-icon style="transform: scale(1.14)">
                <MenuUnfoldOutlined v-if="collapse" />
                <MenuFoldOutlined v-else />
              </el-icon>
            </layout-tool>
            <layout-tool>
              <el-icon style="transform: scale(1.09)">
                <ReloadOutlined />
              </el-icon>
            </layout-tool>
          </template>
          <template #right>
            <layout-tool>
              <el-icon style="transform: scale(1.18)">
                <ExpandOutlined style="stroke-width: 4" />
              </el-icon>
            </layout-tool>
            <layout-tool>
              <el-icon>
                <MoreOutlined />
              </el-icon>
            </layout-tool>
          </template>
          <template #boxBottom>
            <div :style="{ flexShrink: 0, padding: '4px 8px' }">
              <layout-tool style="height: 32px" @click="compact = !compact">
                <el-icon style="transform: scale(1.05)">
                  <MenuUnfoldOutlined v-if="compact" />
                  <MenuFoldOutlined v-else />
                </el-icon>
              </layout-tool>
            </div>
          </template>
          <div
            :style="{
              flex: 'auto',
              padding:
                tabStyle === 'button' && tabBar === true
                  ? '0 12px'
                  : '12px 12px 0 12px',
              boxSizing: 'border-box'
            }"
          >
            <ele-card
              :body-style="{ padding: '16px 8px 16px 14px' }"
              style="margin: 0"
            >
              <option-item label="整体布局">
                <el-radio-group v-model="layout">
                  <el-radio value="default" label="侧栏导航" />
                  <el-radio value="top" label="顶栏导航" />
                  <el-radio value="mix" label="混合导航" />
                  <el-radio value="side" label="仅侧栏导航" />
                </el-radio-group>
              </option-item>
              <option-item label="侧栏布局">
                <el-radio-group v-model="sidebarLayout">
                  <el-radio value="default" label="单侧栏" />
                  <el-radio value="mix" label="双侧栏" />
                  <el-radio value="box" label="仅一级侧栏" />
                </el-radio-group>
              </option-item>
              <option-item label="顶栏风格">
                <el-radio-group
                  :disabled="layout === 'side'"
                  v-model="headerStyle"
                >
                  <el-radio value="light" label="亮色风格" />
                  <el-radio value="dark" label="暗色风格" />
                  <el-radio value="primary" label="主色风格" />
                </el-radio-group>
              </option-item>
              <option-item label="侧栏风格">
                <el-radio-group
                  :disabled="layout === 'top'"
                  v-model="sidebarStyle"
                >
                  <el-radio value="light" label="亮色风格" />
                  <el-radio value="dark" label="暗色风格" />
                </el-radio-group>
              </option-item>
              <option-item label="双侧栏二级风格">
                <el-radio-group
                  :disabled="sidebarLayout !== 'mix'"
                  v-model="mixSidebarStyle"
                >
                  <el-radio value="light" label="亮色风格" />
                  <el-radio value="dark" label="暗色风格" />
                </el-radio-group>
              </option-item>
              <option-item label="页签栏">
                <el-radio-group v-model="tabBar">
                  <el-radio :value="true" label="显示" />
                  <el-radio value="header" label="显示在顶栏" />
                  <el-radio :value="false" label="不显示" />
                </el-radio-group>
              </option-item>
              <option-item label="页签风格">
                <el-radio-group :disabled="!tabBar" v-model="tabStyle">
                  <el-radio value="simple" label="默认风格" />
                  <el-radio value="indicator" label="圆点风格" />
                  <el-radio value="tag" label="标签风格" />
                  <el-radio value="button" label="卡片风格" />
                </el-radio-group>
              </option-item>
              <option-item label="面包屑">
                <el-radio-group v-model="breadcrumb">
                  <el-radio :value="true" label="显示" />
                  <el-radio :value="false" label="不显示" />
                </el-radio-group>
              </option-item>
              <option-item label="内容区域滚动">
                <el-radio-group v-model="fixedBody">
                  <el-radio :value="true" label="是" />
                  <el-radio :value="false" label="否" />
                </el-radio-group>
              </option-item>
              <option-item label="固定顶栏">
                <el-radio-group :disabled="fixedBody" v-model="fixedHeader">
                  <el-radio :value="true" label="是" />
                  <el-radio :value="false" label="否" />
                </el-radio-group>
              </option-item>
              <option-item label="固定侧栏">
                <el-radio-group :disabled="fixedBody" v-model="fixedSidebar">
                  <el-radio :value="true" label="是" />
                  <el-radio :value="false" label="否" />
                </el-radio-group>
              </option-item>
              <option-item label="Logo 位置">
                <el-radio-group
                  :disabled="layout === 'top' || layout === 'side' || mobile"
                  v-model="logoInHeader"
                >
                  <el-radio :value="true" label="顶栏" />
                  <el-radio :value="false" label="侧栏" />
                </el-radio-group>
              </option-item>
              <option-item label="内容区最大化">
                <el-radio-group v-model="maximized">
                  <el-radio :value="false" label="否" />
                  <el-radio :value="true" label="是" />
                  <el-radio value="expanded" label="不带页签栏" />
                </el-radio-group>
              </option-item>
              <option-item label="折叠侧栏">
                <el-radio-group
                  :disabled="
                    (layout === 'top' || sidebarLayout === 'box') && !mobile
                  "
                  v-model="collapse"
                >
                  <el-radio :value="false" label="否" />
                  <el-radio :value="true" label="是" />
                </el-radio-group>
              </option-item>
              <option-item label="折叠双侧栏一级">
                <el-radio-group
                  :disabled="layout === 'top' || sidebarLayout === 'default'"
                  v-model="compact"
                >
                  <el-radio :value="false" label="否" />
                  <el-radio :value="true" label="是" />
                </el-radio-group>
              </option-item>
              <option-item label="移动端风格">
                <el-radio-group v-model="mobile">
                  <el-radio :value="true" label="是" />
                  <el-radio :value="false" label="否" />
                </el-radio-group>
              </option-item>
              <option-item v-if="layout !== 'side'" label="顶栏高度">
                <div style="max-width: 160px">
                  <el-slider v-model="headerHeight" :min="38" :max="68" />
                </div>
              </option-item>
              <option-item v-if="sidebarLayout === 'mix'" label="侧栏宽度">
                <div style="max-width: 160px">
                  <el-slider v-model="sidebarMixWidth" :min="100" :max="260" />
                </div>
              </option-item>
              <option-item v-else label="侧栏宽度">
                <div style="max-width: 160px">
                  <el-slider v-model="sidebarWidth" :min="120" :max="280" />
                </div>
              </option-item>
              <option-item
                v-if="sidebarLayout === 'mix'"
                label="双侧栏一级宽度"
              >
                <div style="max-width: 160px">
                  <el-slider v-model="sideboxWidth" :min="60" :max="120" />
                </div>
              </option-item>
            </ele-card>
          </div>
          <div style="padding: 16px 0; text-align: center; opacity: 0.6">
            我是页脚&emsp;我是页脚&emsp;我是页脚
          </div>
        </ele-admin-layout>
      </div>
    </frame-card>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, watch, markRaw } from 'vue';
  import { LayoutTool } from 'ele-admin-plus';
  import { useTimer } from 'ele-admin-plus/es/utils/hook';
  import {
    SettingOutlined,
    UserOutlined,
    IdcardOutlined,
    LogOutlined,
    CalendarOutlined,
    MenuFoldOutlined,
    MenuUnfoldOutlined,
    ReloadOutlined,
    ExpandOutlined,
    MoreOutlined
  } from '@/components/icons';
  import type {
    Layout,
    SidebarLayout,
    TabBar,
    HeaderStyle,
    SidebarStyle,
    TabStyle,
    Maximized
  } from 'ele-admin-plus/es/ele-admin-layout/types';
  import type { MenuItem } from 'ele-admin-plus/es/ele-menus/types';
  import type { TabPaneItem } from 'ele-admin-plus/es/ele-tabs/types';
  import type { BreadcrumbItem } from 'ele-admin-plus/es/ele-breadcrumb/types';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';
  import FrameCard from './frame-card.vue';

  const layoutRef = ref<any>(null);

  const headerMenus = ref<MenuItem[]>([
    {
      index: '/personnel',
      title: '人事系统',
      icon: markRaw(UserOutlined)
    },
    {
      index: '/finance',
      title: '财务系统',
      icon: markRaw(SettingOutlined)
    }
  ]);

  const headerActive = ref('/personnel');

  const sidebarMenus = ref<MenuItem[]>([
    {
      index: '/system',
      title: '系统管理',
      icon: markRaw(SettingOutlined),
      children: [
        {
          index: '/system/user',
          title: '用户管理',
          icon: markRaw(UserOutlined)
        },
        {
          index: '/system/role',
          title: '角色管理',
          icon: markRaw(IdcardOutlined)
        }
      ]
    },
    {
      index: '/log',
      title: '日志管理',
      icon: markRaw(LogOutlined),
      children: [
        {
          index: '/log/login',
          title: '登录日志',
          icon: markRaw(CalendarOutlined)
        }
      ]
    },
    {
      index: '/profile',
      title: '个人中心',
      icon: markRaw(UserOutlined)
    }
  ]);

  const sidebarActive = ref('/system/user');

  const sideboxMenus = ref<MenuItem[]>([
    {
      index: '/system',
      title: '系统',
      group: true,
      children: [
        {
          index: '/system/user',
          title: '用户管理',
          icon: markRaw(UserOutlined)
        },
        {
          index: '/system/role',
          title: '角色管理',
          icon: markRaw(IdcardOutlined)
        }
      ]
    },
    {
      index: '/log',
      title: '其它',
      group: true,
      children: [
        {
          index: '/log/login',
          title: '登录日志',
          icon: markRaw(CalendarOutlined)
        },
        {
          index: '/profile',
          title: '个人中心',
          icon: markRaw(UserOutlined)
        }
      ]
    }
  ]);

  const sideboxActive = ref('/system/user');

  const tabs = ref<TabPaneItem[]>([
    { name: '/system/user', label: '用户管理', closable: true },
    { name: '/system/role', label: '角色管理', closable: true }
  ]);

  const tabActive = ref('/system/user');

  const levels = ref<BreadcrumbItem[]>([
    { title: '首页' },
    { title: '系统管理' },
    { title: '用户管理' }
  ]);

  const layout = ref<Layout>('default');

  const sidebarLayout = ref<SidebarLayout>('mix');

  const tabBar = ref<TabBar>(true);

  const breadcrumb = ref(true);

  const headerStyle = ref<HeaderStyle>('light');

  const sidebarStyle = ref<SidebarStyle>('light');

  const mixSidebarStyle = ref<SidebarStyle>('light');

  const tabStyle = ref<TabStyle>('button');

  const fixedHeader = ref(true);

  const fixedSidebar = ref(true);

  const fixedBody = ref(true);

  const logoInHeader = ref(false);

  const maximized = ref<Maximized>(false);

  const collapse = ref(false);

  const compact = ref(false);

  const mobile = ref(false);

  const headerHeight = ref(54);

  const sidebarWidth = ref(220);

  const sideboxWidth = ref(80);

  const sidebarMixWidth = ref(160);

  const [startDisableTransitionTimer] = useTimer(400);

  watch([headerHeight, sidebarWidth, sideboxWidth, sidebarMixWidth], () => {
    const el = layoutRef.value?.$el;
    el?.classList?.add?.('is-transition-disabled');
    startDisableTransitionTimer(() => {
      el?.classList?.remove?.('is-transition-disabled');
    });
  });
</script>

<style lang="scss" scoped>
  .demo-layout-wrapper :deep(.option-item) {
    align-items: flex-start;

    .option-item-label {
      width: 106px;
      height: 32px;
      line-height: 32px;
    }

    & + .option-item {
      margin-top: 16px;
    }
  }
</style>
