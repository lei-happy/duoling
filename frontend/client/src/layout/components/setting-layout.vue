<!-- 常用布局 -->
<template>
  <div class="ele-setting-layout-list">
    <SettingLayoutItem
      v-for="item in skinConfig?.layouts || PREDEFINED_LAYOUTS"
      :key="item.name"
      :title="t(`layout.setting.layouts.${item.name}`)"
      :cover="item.cover"
      :active="!!(layoutName && item.name === layoutName)"
      @click="handleLayoutItemClick(item)"
    />
  </div>
</template>

<script lang="ts" setup>
  import { useI18n } from 'vue-i18n';
  import { storeToRefs } from 'pinia';
  import type { PredefinedLayout } from 'ele-admin-plus/es/utils/theme-util';
  import { useThemeStore } from '@/store/modules/theme';
  import { PREDEFINED_LAYOUTS } from '@/utils/skin-config';
  import SettingLayoutItem from './setting-layout-item.vue';

  const { t } = useI18n();
  const themeStore = useThemeStore();

  const { skinConfig, layoutName } = storeToRefs(themeStore);

  /** 切换常用布局 */
  const handleLayoutItemClick = (layoutItem: PredefinedLayout) => {
    themeStore.setLayout(layoutItem);
  };
</script>
