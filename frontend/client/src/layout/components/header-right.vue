<template>
  <!-- AI 数字员工入口：圆形炫彩按钮，hover 展开员工列表，点击打开会话弹窗 -->
  <layout-tool v-if="hasAiAssistant" class="header-ai-entry-tool">
    <header-ai-entry />
  </layout-tool>
  <!-- 消息通知：无租户切换时与右侧头像略拉开间距 -->
  <layout-tool
    :class="{
      'hidden-sm-and-down': tabBar && tabInHeader,
      'header-notice-gap': tenantList.length <= 1
    }"
  >
    <header-notice />
  </layout-tool>
  <!-- 租户切换：仅多企业时展示，避免单企业下占位 -->
  <layout-tool v-if="tenantList.length > 1">
    <tenant-switch :tenants="tenantList" />
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
  import { computed, ref, onMounted } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { storeToRefs } from 'pinia';
  import { LayoutTool, useModal } from 'ele-admin-plus';
  import { MoreOutlined, MoonOutlined, SunOutlined } from '@/components/icons';
  import { doWithTransition } from '@/utils/common';
  import { useThemeStore } from '@/store/modules/theme';
  import { useUserStore } from '@/store/modules/user';
  import { getUserTenants } from '@/api/login';
  import type { TenantOption } from '@/api/login/model';
  import HeaderUser from './header-user.vue';
  import HeaderNotice from './header-notice.vue';
  import HeaderAiEntry from './header-ai-entry.vue';
  import TenantSwitch from './tenant-switch.vue';

  const { openModal } = useModal();

  /** 当前用户可选企业列表（用于判断是否展示顶栏切换入口） */
  const tenantList = ref<TenantOption[]>([]);

  onMounted(async () => {
    try {
      tenantList.value = await getUserTenants();
    } catch (e) {
      console.error('获取租户列表失败', e);
    }
  });

  const themeStore = useThemeStore();
  const { tabBar, tabInHeader, darkMode, weakMode } = storeToRefs(themeStore);

  /** AI 数字员工顶栏入口可见性：随租户产品版本动态控制 */
  const userStore = useUserStore();
  const hasAiAssistant = computed(() =>
    (userStore.features ?? []).includes('ai_assistant')
  );

  const { t } = useI18n();

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

<style scoped>
  .header-notice-gap {
    margin-inline-end: 10px;
  }
  /* AI 入口与右侧消息铃铛之间留出一些呼吸 */
  .header-ai-entry-tool {
    margin-inline-end: 4px;
  }
</style>
