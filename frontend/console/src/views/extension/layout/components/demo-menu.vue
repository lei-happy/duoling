<template>
  <ele-card header="多列菜单" :body-style="{ padding: '12px' }">
    <frame-card>
      <ele-admin-layout
        :height="600"
        :sidebarMenus="sidebarMenus"
        :sidebarActive="sidebarActive"
        :tabs="tabs"
        :tabActive="tabActive"
        :tabBar="true"
        :fixedHome="true"
        sidebarStyle="dark"
        v-model:collapse="collapse"
        :menu-scroll-to-active="false"
        :sidebar-menu-props="{
          collapse: false,
          textEllipsisTooltip: true,
          mode: collapse && !mobile ? 'compact' : 'vertical',
          popperOffset: 10
        }"
        :mobile="mobile"
        :style="{ '--ele-sidebar-collapse-width': '74px' }"
        class="demo-menu-wrapper"
      >
        <template #logo>
          <div style="display: flex; align-items: center; gap: 4px">
            <img src="@/assets/logo.svg" style="width: 22px; height: 22px" />
            <h1>Ele Admin</h1>
          </div>
          <h1>后台管理模板系统</h1>
        </template>
        <template #left>
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
            <el-icon style="transform: scale(1.17)">
              <BellOutlined />
            </el-icon>
          </layout-tool>
          <layout-tool style="padding-left: 4px; padding-right: 4px">
            <div
              :style="{
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                background: 'var(--el-color-primary-light-8)',
                marginRight: '6px'
              }"
            ></div>
            <div>用户名</div>
            <el-icon :size="13" style="margin: 0 0 0 2px">
              <ArrowDown />
            </el-icon>
          </layout-tool>
        </template>
        <template #icon="{ icon }">
          <img v-if="icon" :src="icon" class="demo-menu-icon" />
        </template>
        <div :style="{ flex: 'auto', padding: '12px 12px 0 12px' }">
          <ele-card
            :body-style="{ padding: '12px' }"
            style="margin-bottom: 12px"
          >
            <div
              :style="{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                background: 'var(--el-color-primary-light-8)'
              }"
            ></div>
          </ele-card>
          <el-row :gutter="12">
            <el-col :span="12">
              <ele-card style="height: 120px; margin-bottom: 12px" />
            </el-col>
            <el-col :span="12">
              <ele-card style="height: 120px; margin-bottom: 12px" />
            </el-col>
            <el-col :span="16">
              <ele-card style="height: 332px; margin-bottom: 12px" />
            </el-col>
            <el-col :span="8">
              <div>
                <ele-card style="height: 160px; margin-bottom: 12px" />
                <ele-card style="height: 160px; margin-bottom: 12px" />
              </div>
            </el-col>
            <el-col :span="8">
              <ele-card style="height: 160px; margin-bottom: 12px" />
            </el-col>
            <el-col :span="8">
              <ele-card style="height: 160px; margin-bottom: 12px" />
            </el-col>
            <el-col :span="8">
              <ele-card style="height: 160px; margin-bottom: 12px" />
            </el-col>
          </el-row>
        </div>
        <div style="padding: 4px 0 16px 0; text-align: center; opacity: 0.4">
          页脚页脚&emsp;页脚页脚&emsp;页脚页脚
        </div>
      </ele-admin-layout>
    </frame-card>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, computed } from 'vue';
  import { LayoutTool } from 'ele-admin-plus';
  import {
    MenuFoldOutlined,
    MenuUnfoldOutlined,
    ReloadOutlined,
    BellOutlined,
    ArrowDown
  } from '@/components/icons';
  import type { MenuItem } from 'ele-admin-plus/es/ele-menus/types';
  import type { TabPaneItem } from 'ele-admin-plus/es/ele-tabs/types';
  import { useMobile } from '@/utils/use-mobile';
  import FrameCard from './frame-card.vue';

  const sidebarMenus = computed<MenuItem[]>(() => {
    return [
      {
        index: '/home',
        title: '工作台',
        icon: 'https://cdn2.weimob.com/saas/@assets/saas-fe-website-web-stc/_next/static/media/wosIntro4.73c5f876.png'
      },
      {
        index: '/system',
        title: '系统管理',
        group: mobile.value || !collapse.value,
        icon: 'https://cdn2.weimob.com/saas/@assets/saas-fe-website-web-stc/_next/static/media/wosIntro5.3dafe778.png',
        children: [
          {
            index: '/system/user',
            title: '用户管理'
          },
          {
            index: '/system/role',
            title: '角色管理'
          },
          {
            index: '/system/menu',
            title: '菜单管理'
          },
          {
            index: '/system/organization',
            title: '机构管理'
          },
          {
            index: '/system/tenant',
            title: '租户管理'
          },
          {
            index: '/system/dictionary',
            title: '字典管理'
          }
        ],
        popperClass: 'demo-menu-pop'
      },
      {
        index: '/data',
        title: '数据中心',
        group: mobile.value || !collapse.value,
        icon: 'https://cdn2.weimob.com/saas/@assets/saas-fe-website-web-stc/_next/static/media/wosIntro3.fe812660.png',
        children: [
          {
            index: '/data/operation',
            title: '运营数据'
          },
          {
            index: '/data/member',
            title: '会员数据'
          },
          {
            index: '/data/sell',
            title: '销售数据'
          },
          {
            index: '/data/financial',
            title: '财务数据'
          },
          {
            index: '/data/channel',
            title: '渠道数据'
          }
        ],
        popperClass: 'demo-menu-pop'
      }
    ];
  });

  const sidebarActive = ref('/home');

  const tabs = ref<TabPaneItem[]>([
    { name: '/system/user', label: '用户管理', closable: true },
    { name: '/system/role', label: '角色管理', closable: true }
  ]);

  const tabActive = ref('/system/user');

  const collapse = ref(false);

  const { mobile } = useMobile();
</script>

<style lang="scss" scoped>
  .demo-menu-wrapper :deep(.ele-admin-sidebar) {
    background: #121319;
    --el-color-primary: #328dfc;

    .el-menu {
      padding: 0 8px;
      --ele-menu-dark-color: #fff;

      &::before,
      &::after {
        display: none !important;
      }

      & > .el-menu-item,
      & > .el-sub-menu > .el-sub-menu__title {
        margin: 0 0 8px 0 !important;
        height: 38px;
        line-height: 38px;
        border-radius: 6px;
        padding: 0 6px;
      }
    }

    .el-menu-item-group {
      & > .el-menu-item-group__title {
        margin: 0 0 8px 0 !important;
        color: rgba(255, 255, 255, 0.6);
        font-size: 14px;
        height: 32px !important;
        line-height: 32px !important;
        padding: 0 6px !important;
      }

      & > ul {
        display: grid;
        grid-gap: 6px;
        grid-template-columns: repeat(2, 1fr);
        padding: 8px;
        border-radius: 6px;
        background: #25293a;
        box-sizing: border-box;
        margin-bottom: 8px;

        &::before,
        &::after {
          display: none !important;
        }

        & > .el-menu-item {
          margin: 0 !important;
          height: 36px !important;
          line-height: 36px !important;
          border-radius: 6px !important;
          overflow: hidden;
        }
      }
    }

    .demo-menu-icon {
      width: 22px;
      height: 22px;
      margin-right: 4px;
    }

    .ele-admin-logo {
      height: auto;
      flex-direction: column;
      padding: 12px 0;
    }

    &.is-collapse {
      .ele-admin-logo {
        h1 {
          display: none;
        }

        img {
          width: 30px !important;
          height: 30px !important;
        }
      }

      .el-menu {
        & > .el-menu-item,
        & > .el-sub-menu > .el-sub-menu__title {
          height: auto !important;
          padding: 8px 0 !important;
        }
      }
    }
  }
</style>

<style lang="scss">
  .demo-menu-pop {
    ul.el-menu {
      display: grid;
      grid-gap: 6px;
      grid-template-columns: repeat(2, 1fr);
      padding: 8px;
      border-radius: 6px;
      background: #25293a !important;
      box-sizing: border-box;

      &::before,
      &::after {
        display: none !important;
      }

      & > .el-menu-item {
        margin: 0 !important;
        height: 36px !important;
        line-height: 36px !important;
        border-radius: 6px !important;
        overflow: hidden;
      }
    }
  }
</style>
