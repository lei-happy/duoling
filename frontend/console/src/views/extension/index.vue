<template>
  <ele-page
    ref="wrapRef"
    :multi-card="false"
    :hide-footer="true"
    class="demo-extension"
  >
    <div class="demo-extension-nav">
      <ele-card :flex-table="true" :body-style="{ padding: 0 }">
        <el-scrollbar>
          <ele-menus
            ref="menuRef"
            mode="compact"
            :items="items"
            :default-active="active"
          />
        </el-scrollbar>
      </ele-card>
    </div>
    <div style="flex: 1; overflow: hidden">
      <transition name="slide-right" mode="out-in">
        <component v-if="bodyComponent" :is="bodyComponent" />
      </transition>
    </div>
    <ele-backtop :target="wrapRef?.$el" />
  </ele-page>
</template>

<script lang="ts" setup>
  import type { Component } from 'vue';
  import { ref, defineAsyncComponent, shallowRef, watch, nextTick } from 'vue';
  import { useRoute } from 'vue-router';
  import type {
    EleMenusInstance,
    ElePageInstance
  } from 'ele-admin-plus/es/ele-app/plus';
  import type { MenuItem } from 'ele-admin-plus/es/ele-menus/types';
  import { LinkOutlined } from '@/components/icons';

  defineOptions({ name: 'Extension' });

  const items: MenuItem[] = [
    {
      index: 'table',
      path: '/extension?name=table',
      title: '高级表格',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/table/index.vue')
        )
      }
    },
    {
      index: 'modal',
      path: '/extension?name=modal',
      title: '高级弹窗',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/modal/index.vue')
        )
      }
    },
    {
      index: 'message',
      path: '/extension?name=message',
      title: '消息提示',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/message/index.vue')
        )
      }
    },
    {
      index: 'layout',
      path: '/extension?name=layout',
      title: '布局组件',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/layout/index.vue')
        )
      }
    },
    {
      index: 'table-select',
      path: '/extension?name=table-select',
      title: '下拉表格',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/table-select/index.vue')
        )
      }
    },
    {
      index: 'tree-select',
      path: '/extension?name=tree-select',
      title: '下拉树',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/tree-select/index.vue')
        )
      }
    },
    {
      index: 'upload',
      path: '/extension?name=upload',
      title: '文件上传',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/upload/index.vue')
        )
      }
    },
    {
      index: 'icon',
      path: '/extension?name=icon',
      title: '图标选择',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/icon/index.vue')
        )
      }
    },
    {
      index: 'file',
      path: '/extension?name=file',
      title: '文件列表',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/file/index.vue')
        )
      }
    },
    {
      index: 'split',
      path: '/extension?name=split',
      title: '分割面板',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/split/index.vue')
        )
      }
    },
    {
      index: 'printer',
      path: '/extension?name=printer',
      title: '打印组件',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/printer/index.vue')
        )
      }
    },
    {
      index: 'text',
      path: '/extension?name=text',
      title: '文本组件',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/text/index.vue')
        )
      }
    },
    {
      index: 'tag',
      path: '/extension?name=tag',
      title: '标签输入',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/tag/index.vue')
        )
      }
    },
    {
      index: 'avatar',
      path: '/extension?name=avatar',
      title: '头像组合',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/avatar/index.vue')
        )
      }
    },
    {
      index: 'tour',
      path: '/extension?name=tour',
      title: '引导组件',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/tour/index.vue')
        )
      }
    },
    {
      index: 'menu',
      path: '/extension?name=menu',
      title: '导航菜单',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/menu/index.vue')
        )
      }
    },
    {
      index: 'check-card',
      path: '/extension?name=check-card',
      title: '可选卡片',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/check-card/index.vue')
        )
      }
    },
    {
      index: 'watermark',
      path: '/extension?name=watermark',
      title: '水印组件',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/watermark/index.vue')
        )
      }
    },
    {
      index: 'viewer',
      path: '/extension?name=viewer',
      title: '查看器',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/viewer/index.vue')
        )
      }
    },
    {
      index: 'steps',
      path: '/extension?name=steps',
      title: '步骤条',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/steps/index.vue')
        )
      }
    },
    {
      index: 'segmented',
      path: '/extension?name=segmented',
      title: '分段器',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/segmented/index.vue')
        )
      }
    },
    {
      index: 'tabs',
      path: '/extension?name=tabs',
      title: '标签页',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/tabs/index.vue')
        )
      }
    },
    {
      index: 'qr-code',
      path: '/extension?name=qr-code',
      title: '二维码',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/qr-code/index.vue')
        )
      }
    },
    {
      index: 'bar-code',
      path: '/extension?name=bar-code',
      title: '条形码',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/bar-code/index.vue')
        )
      }
    },
    {
      index: 'regions',
      path: '/extension?name=regions',
      title: '城市选择',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/regions/index.vue')
        )
      }
    },
    {
      index: 'excel',
      path: '/extension?name=excel',
      title: '导入导出',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/excel/index.vue')
        )
      }
    },
    {
      index: 'dragsort',
      path: '/extension?name=dragsort',
      title: '拖拽排序',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/dragsort/index.vue')
        )
      }
    },
    {
      index: 'map',
      path: '/extension?name=map',
      title: '地图组件',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/map/index.vue')
        )
      }
    },
    {
      index: 'player',
      path: '/extension?name=player',
      title: '视频播放',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/player/index.vue')
        )
      }
    },
    {
      index: 'editor',
      path: '/extension?name=editor',
      title: '富文本框',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/editor/index.vue')
        )
      }
    },
    {
      index: 'markdown',
      path: '/extension?name=markdown',
      title: 'markdown',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/markdown/index.vue')
        )
      }
    },
    {
      index: 'monaco',
      path: '/extension?name=monaco',
      title: '代码编辑',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/monaco/index.vue')
        )
      }
    },
    {
      index: 'user-select',
      path: '/extension?name=user-select',
      title: '用户选择',
      icon: LinkOutlined,
      meta: {
        component: defineAsyncComponent(
          () => import('@/views/extension/user-select/index.vue')
        )
      }
    }
  ];

  const active = ref<string>('table/index.vue');

  const menuRef = ref<EleMenusInstance>(null);

  const wrapRef = ref<ElePageInstance>(null);

  const bodyComponent = shallowRef<Component>();

  const route = useRoute();

  watch(
    () => route.query.name,
    (name) => {
      if (route.path === '/extension') {
        active.value = [name].flat()[0] || 'table';
      }
    },
    { immediate: true }
  );

  watch(
    active,
    (name) => {
      bodyComponent.value = items.find(
        (item) => item.index === name
      )?.meta?.component;
      nextTick(() => {
        menuRef.value?.scrollToActive?.();
      });
    },
    { immediate: true }
  );
</script>

<style lang="scss" scoped>
  .demo-extension {
    flex: 1;
    padding: 0;
    display: flex;
    align-items: flex-start;
    position: relative;
    overflow: auto;
  }

  .demo-extension-nav {
    flex-shrink: 0;
    width: 100px;
    height: 100%;
    padding: 16px 0 16px 16px;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    position: sticky;
    top: 0;

    :deep(.ele-card) {
      .el-scrollbar__bar.is-vertical {
        width: 4px;
      }

      .ele-menu {
        background: none;
        border: none;
      }
    }
  }
</style>
