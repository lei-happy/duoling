<template>
  <!-- AI 数字员工入口：圆形炫彩按钮，hover 展开员工列表，点击打开会话弹窗 -->
  <layout-tool v-if="hasAiAssistant" class="header-ai-entry-tool">
    <header-ai-entry />
  </layout-tool>
  <!-- 版本升级说明入口 -->
  <layout-tool>
    <header-changelog />
  </layout-tool>
  <!-- 意见反馈入口 -->
  <layout-tool>
    <header-feedback />
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
  <!-- 夜间模式：暂不提供切换功能，隐藏开关 -->
  <layout-tool
    v-if="false"
    ref="darkSwitchRef"
    class="ele-dark-switch hidden-sm-and-down"
  >
    <el-switch
      :active-action-icon="MoonOutlined"
      :inactive-action-icon="SunOutlined"
      :model-value="darkMode"
      @update:modelValue="updateDarkMode"
    />
  </layout-tool>
  <!-- 主题设置入口已隐藏：租户端已关闭自定义主题功能 -->
</template>

<script lang="ts" setup>
  import { computed, ref, onMounted } from 'vue';
  import { storeToRefs } from 'pinia';
  import { LayoutTool } from 'ele-admin-plus';
  import { MoonOutlined, SunOutlined } from '@/components/icons';
  import { doWithTransition } from '@/utils/common';
  import { useThemeStore } from '@/store/modules/theme';
  import { useUserStore } from '@/store/modules/user';
  import { getUserTenants } from '@/api/login';
  import type { TenantOption } from '@/api/login/model';
  import HeaderUser from './header-user.vue';
  import HeaderNotice from './header-notice.vue';
  import HeaderChangelog from './header-changelog.vue';
  import HeaderFeedback from './header-feedback.vue';
  import HeaderAiEntry from './header-ai-entry.vue';
  import TenantSwitch from './tenant-switch.vue';

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
