<template>
  <!-- 全屏切换 -->
  <layout-tool class="hidden-sm-and-down" @click="toggleFullscreen">
    <el-icon style="transform: scale(1.18)">
      <CompressOutlined v-if="isFullscreen" style="stroke-width: 4" />
      <ExpandOutlined v-else style="stroke-width: 4" />
    </el-icon>
  </layout-tool>
  <!-- 语言切换 -->
  <layout-tool :class="{ 'hidden-sm-and-down': tabBar && tabInHeader }">
    <i18n-icon :icon-style="{ transform: 'scale(1.15)' }" />
  </layout-tool>
  <!-- 消息通知 -->
  <layout-tool :class="{ 'hidden-sm-and-down': tabBar && tabInHeader }">
    <header-notice />
  </layout-tool>
  <!-- 租户切换 -->
  <layout-tool>
    <tenant-switch />
  </layout-tool>
  <!-- 用户信息 -->
  <layout-tool>
    <header-user />
  </layout-tool>
  <!-- 夜间模式 -->
  <layout-tool ref="darkSwitchRef" class="ele-dark-switch hidden-sm-and-down">
    <el-switch
      :active-action-icon="MoonOutlined"
      :inactive-action-icon="SunOutlined"
      :model-value="darkMode"
      @update:modelValue="updateDarkMode"
    />
  </layout-tool>
  <!-- 主题设置 -->
  <layout-tool @click="openSetting" style="position: relative">
    <el-icon>
      <MoreOutlined />
    </el-icon>
    <!-- <div v-if="showTip" class="ele-theme-setting-tip">
      <IconOutline />
      <div>
        <div>试试切换布局或主题~</div>
        <IconOutline :width="152" :height="34" />
      </div>
    </div> -->
  </layout-tool>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { storeToRefs } from 'pinia';
  import {
    LayoutTool,
    requestFullscreen,
    exitFullscreen,
    useModal,
    EleMessage
  } from 'ele-admin-plus';
  import {
    ExpandOutlined,
    CompressOutlined,
    MoreOutlined,
    MoonOutlined,
    SunOutlined
  } from '@/components/icons';
  import { doWithTransition } from '@/utils/common';
  import { useThemeStore } from '@/store/modules/theme';
  import HeaderUser from './header-user.vue';
  import HeaderNotice from './header-notice.vue';
  import TenantSwitch from './tenant-switch.vue';
  import I18nIcon from './i18n-icon.vue';
  import IconOutline from './covers/icon-outline.vue';

  const props = defineProps({
    /** 是否全屏状态 */
    isFullscreen: Boolean
  });

  const emit = defineEmits(['update:isFullscreen']);

  const { openModal } = useModal();

  const themeStore = useThemeStore();
  const { tabBar, tabInHeader, darkMode, weakMode } = storeToRefs(themeStore);

  const { t } = useI18n();

  /** 全屏切换 */
  const toggleFullscreen = () => {
    if (props.isFullscreen) {
      exitFullscreen();
      emit('update:isFullscreen', false);
      return;
    }
    try {
      requestFullscreen();
      emit('update:isFullscreen', true);
    } catch (e: any) {
      console.error(e);
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  /** 打开主题设置抽屉 */
  const openSetting = () => {
    showTip.value = false;
    openModal({
      modalId: 'theme-setting-drawer',
      type: 'drawer',
      asyncComponent: () => import('./setting-drawer.vue'),
      props: {
        size: 268,
        title: t('layout.setting.title'),
        zIndex: 199999,
        bodyStyle: { padding: 0, height: '100%' },
        modalClass: 'ele-setting-drawer'
      },
      keepAlive: true
    });
  };

  /** 暗黑主题切换开关 */
  const darkSwitchRef = ref<any>(null);

  /** 切换暗黑模式 */
  const updateDarkMode = (isDark?: any) => {
    doWithTransition(
      () => themeStore.setValue('darkMode', isDark),
      darkSwitchRef.value?.$el?.querySelector?.('.el-switch__action'),
      weakMode.value ? isDark : !isDark
    );
  };

  /** 显示主题配置提示 */
  const showTip = ref(true);
</script>
