<template>
  <ele-admin-layout
    layout="top"
    :header-menus="headerMenus"
    :fixed-header="fixedHeader"
    :header-custom-style="{
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(12px)',
      boxShadow: 'none',
      borderBottom: '1px solid rgba(0, 0, 0, 0.04)',
      paddingRight: mobile ? '2px' : '12px',
      overflow: 'hidden'
    }"
    :header-menu-props="{
      menuTrigger: mobile ? 'click' : 'hover',
      style: { '--el-color-primary-light-9': 'rgba(22, 119, 255, 0.1)' }
    }"
    :logo-style="{
      marginLeft: mobile ? '12px' : '24px',
      flex: mobile ? 1 : 'none',
      justifyContent: 'flex-start'
    }"
    :header-menus-style="{
      margin: mobile ? '0 -6px 0 -20px' : '0 0 0 20px',
      flex: mobile ? 'none' : 1,
      order: mobile ? 1 : 0
    }"
    :tab-bar="false"
    :breadcrumb="false"
    :fixed-body="false"
    :back-top="false"
    :menu-scroll-to-active="false"
    :style="{
      background: 'none',
      '--ele-header-tool-padding': mobile ? '8px' : '10px'
    }"
  >
    <template #logo>
      <img src="@/assets/logo.svg" />
    </template>
    <template #logoTitle>
      <h1>Ele Admin</h1>
    </template>
    <template #right>
      <layout-tool>登录</layout-tool>
      <layout-tool>注册</layout-tool>
    </template>
    <div :style="{ flex: 'auto' }">
      <el-carousel
        height="320px"
        style="margin-top: calc(0px - var(--ele-header-height) - 1px)"
      >
        <el-carousel-item v-for="item in banner" :key="item">
          <img
            :src="item"
            :style="{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              display: 'block',
              pointerEvents: 'none'
            }"
            class="demo-banner-img"
          />
        </el-carousel-item>
      </el-carousel>
      <div
        :style="{
          maxWidth: '820px',
          margin: '0 auto',
          padding: '0 12px 22px 12px',
          overflow: 'hidden'
        }"
      >
        <div style="text-align: center; padding: 28px 0 20px 0">
          <ele-text size="lg" type="heading">标题标题标题</ele-text>
          <ele-text size="sm" type="secondary">描述描述描述</ele-text>
        </div>
        <el-row :gutter="16">
          <el-col v-for="index in 8" :key="index" :md="6" :sm="8" :xs="12">
            <ele-card style="border-radius: 0; min-height: 140px" />
          </el-col>
        </el-row>
      </div>
      <div
        :style="{
          textAlign: 'center',
          padding: '26px 0',
          backgroundImage:
            'url(https://cdn2.weimob.com/saas/@assets/saas-fe-website-web-stc/_next/static/media/ZhuceBg.d0ce1f1c.png)',
          backgroundSize: '100% 100%'
        }"
      >
        <div style="color: #fff; font-size: 16px">
          文本文本文本文本文本文本文本文本
        </div>
        <div
          :style="{
            width: '88px',
            margin: '0 auto',
            padding: '6px 0',
            borderRadius: '4px',
            color: 'var(--el-color-primary)',
            marginTop: '12px',
            background: '#fff',
            cursor: 'pointer'
          }"
        >
          按钮按钮
        </div>
      </div>
    </div>
    <div
      :style="{
        color: '#999',
        fontSize: '13px',
        background: '#17181B',
        padding: '22px 0 12px 0'
      }"
    >
      <div
        :style="{
          maxWidth: '820px',
          margin: '0 auto',
          padding: '0 12px',
          overflow: 'hidden'
        }"
      >
        <el-row :gutter="16">
          <el-col v-for="index in 4" :key="index" :sm="6" :xs="12">
            <div style="width: max-content; margin: 12px auto">
              <div style="color: #fff; font-size: 14px">标题标题</div>
              <div style="margin-top: 8px; line-height: 2">
                <div>文字文字文字</div>
                <div>文字文字文字</div>
                <div>文字文字文字</div>
              </div>
            </div>
          </el-col>
        </el-row>
        <div
          :style="{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderTop: '1px solid #333',
            paddingTop: '12px',
            marginTop: '22px'
          }"
        >
          <template v-for="index in 4" :key="index">
            <div>文字文字</div>
            <div
              v-if="index !== 4"
              :style="{
                borderLeft: '1px solid #444',
                height: '12px',
                margin: '0 12px'
              }"
            ></div>
          </template>
        </div>
      </div>
    </div>
  </ele-admin-layout>
</template>

<script lang="ts" setup>
  import { ref, computed, markRaw } from 'vue';
  import type { MenuItem } from 'ele-admin-plus/es/ele-menus/types';
  import { LayoutTool } from 'ele-admin-plus';
  import { MenuOutlined } from '@/components/icons';

  const props = defineProps<{
    fixedHeader?: boolean;
    mobile?: boolean;
  }>();

  /** 菜单 */
  const headerMenus = computed<MenuItem[]>(() => {
    const menus = [
      { index: '/index', title: '首页' },
      { index: '/service', title: '产品和服务' },
      { index: '/product', title: '解决方案' },
      { index: '/cases', title: '客户案例' }
    ];
    if (props.mobile) {
      return [
        {
          index: '/menus',
          title: '',
          icon: markRaw(MenuOutlined),
          iconProps: { style: { margin: 0 } },
          iconStyle: { transform: 'translateY(-1px)' },
          children: menus,
          style: {
            '--ele-menu-arrow-size': props.mobile ? '0px' : '14px',
            '--ele-menu-horizontal-active-bg': 'transparent',
            '--ele-menu-horizontal-line-size': 0,
            '--el-menu-active-color': 'var(--el-text-color-primary)'
          }
        }
      ];
    }
    return menus;
  });

  /** 轮播图 */
  const banner = ref([
    'https://cdn2.weimob.com/saas/@assets/saas-fe-website-web-stc/_next/static/media/L101.0a6f1b83.jpg',
    'https://cdn2.weimob.com/saas/@assets/saas-fe-website-web-stc/_next/static/media/L108.d7c6f061.png',
    'https://cdn2.weimob.com/saas/@assets/saas-fe-website-web-stc/_next/static/media/L100.98e3daa4.jpg'
  ]);
</script>

<style lang="scss">
  html.dark .demo-banner-img {
    filter: brightness(78%);
  }
</style>
