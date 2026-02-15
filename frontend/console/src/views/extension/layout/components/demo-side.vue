<template>
  <ele-card header="自定义侧栏样式" :body-style="{ padding: '12px' }">
    <div style="margin-bottom: 8px">
      通过 sidebarCustomStyle 属性设置圆角和外间距，通过 sidebarMenuProps
      属性设置在折叠时菜单风格改为双侧栏一级的风格
    </div>
    <frame-card>
      <ele-admin-layout
        :height="520"
        :sidebar-menus="sidebarMenus"
        :sidebar-active="sidebarActive"
        :fixed-body="true"
        :logo-in-header="true"
        :tab-bar="false"
        :breadcrumb="false"
        sidebar-style="light"
        :sidebar-custom-style="{
          borderRadius: mobile ? 0 : '8px',
          margin: mobile ? 0 : '12px 0 12px 12px',
          boxShadow: 'none'
        }"
        :header-custom-style="{ paddingRight: '4px' }"
        :menu-scroll-to-active="false"
        v-model:collapse="collapse"
        :sidebar-menu-props="{
          collapse: false,
          mode: collapse && !mobile ? 'compact' : 'vertical',
          style: { '--ele-menu-compact-item-padding': '8px 0' }
        }"
        :mobile="mobile"
        :style="{
          '--ele-sidebar-width': '180px',
          '--ele-sidebar-collapse-width': '68px',
          zIndex: 99
        }"
        class="demo-side-wrapper"
      >
        <template #logo>
          <img src="@/assets/logo.svg" />
        </template>
        <template #logoTitle>
          <h1>Ele Admin</h1>
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
        <template #top>
          <div
            :style="{
              padding: collapse && !mobile ? '6px' : '12px',
              borderBottom: '1px solid var(--el-border-color-lighter)'
            }"
          >
            <el-button
              v-if="collapse && !mobile"
              type="primary"
              :icon="UploadOutlined"
              :round="true"
              :style="{ width: '100%' }"
            />
            <el-button
              v-else
              type="primary"
              :icon="UploadOutlined"
              :round="true"
              :style="{ width: '100%', fontSize: '13px', overflow: 'hidden' }"
            >
              发布作品
            </el-button>
          </div>
        </template>
        <template v-if="!mobile" #bottom>
          <div :style="{ flexShrink: 0, padding: '8px' }">
            <layout-tool style="height: 32px" @click="collapse = !collapse">
              <el-icon style="transform: scale(1.05)">
                <MenuUnfoldOutlined v-if="collapse" />
                <MenuFoldOutlined v-else />
              </el-icon>
            </layout-tool>
          </div>
        </template>
        <template v-else #left>
          <layout-tool @click="collapse = !collapse">
            <el-icon style="transform: scale(1.14)">
              <MenuUnfoldOutlined v-if="collapse" />
              <MenuFoldOutlined v-else />
            </el-icon>
          </layout-tool>
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
  import { ref, computed, markRaw } from 'vue';
  import { LayoutTool } from 'ele-admin-plus';
  import type { MenuItem } from 'ele-admin-plus/es/ele-menus/types';
  import {
    HomeFilled,
    VideoCameraFilled,
    WalletFilled,
    UserFilled,
    Promotion
  } from '@element-plus/icons-vue';
  import {
    BellOutlined,
    ArrowDown,
    UploadOutlined,
    MenuFoldOutlined,
    MenuUnfoldOutlined
  } from '@/components/icons';
  import { useMobile } from '@/utils/use-mobile';
  import FrameCard from './frame-card.vue';

  const sidebarMenus = computed<MenuItem[]>(() => {
    const isCollapse = collapse.value;
    return [
      {
        index: '/home',
        title: '首页',
        icon: markRaw(HomeFilled),
        iconProps: { style: { marginTop: '-2px' } }
      },
      {
        index: '/creater',
        title: isCollapse ? '创作' : '创作中心',
        group: true,
        children: [
          {
            index: '/product',
            title: isCollapse ? '作品' : '我的作品',
            icon: markRaw(VideoCameraFilled),
            iconProps: { style: { marginTop: '-2px' } }
          },
          {
            index: '/income',
            title: isCollapse ? '收益' : '作品收益',
            icon: markRaw(WalletFilled),
            iconProps: { style: { marginTop: '-2px' } }
          }
        ]
      },
      {
        index: '/interaction',
        title: isCollapse ? '互动' : '互动中心',
        group: true,
        children: [
          {
            index: '/letter',
            title: isCollapse ? '私信' : '我的私信',
            icon: markRaw(Promotion),
            iconProps: { style: { marginTop: '-2px' } }
          },
          {
            index: '/follow',
            title: isCollapse ? '粉丝' : '我的粉丝',
            icon: markRaw(UserFilled),
            iconProps: { style: { marginTop: '-2px' } }
          }
        ]
      }
    ];
  });

  const sidebarActive = ref('/home');

  const collapse = ref(false);

  const { mobile } = useMobile();
</script>

<style lang="scss" scoped>
  .demo-side-wrapper :deep(.el-menu-item) {
    & > .el-icon {
      color: var(--el-text-color-placeholder);
    }

    &.is-active > .el-icon {
      color: var(--el-color-primary);
    }
  }
</style>
