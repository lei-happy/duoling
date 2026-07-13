<!-- 用户问候 + 天气预报 -->
<template>
  <ele-card shadow="never" class="profile-card" :body-style="{ padding: '20px' }">
    <div class="profile-wrapper">
      <!-- 头像 + 问候 -->
      <div class="profile-header">
        <el-avatar :size="48" :src="loginUser.avatar" class="profile-avatar" />
        <div class="profile-header-body">
          <div class="profile-greeting">{{ greetingText }}</div>
          <div class="profile-sub">
            <span v-if="roleName" class="profile-role">{{ roleName }}</span>
          </div>
        </div>
      </div>

      <!-- 天气预报插件 -->
      <weather-widget class="profile-weather-widget" />
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { useUserStore } from '@/store/modules/user';
  import { getProfileGreetingText } from '../utils/profile-greeting';
  import WeatherWidget from './weather-widget.vue';

  const userStore = useUserStore();

  /** 当前登录用户信息 */
  const loginUser = computed(() => userStore.info ?? {});

  /** 角色名称（取首个角色） */
  const roleName = computed(
    () => userStore.info?.roles?.[0]?.roleName?.trim() || ''
  );

  /** 按上海时段随机问候（仅用户身份变化时刷新，避免快捷操作等偏好保存触发重随机） */
  const greetingText = ref('');
  watch(
    () =>
      [
        userStore.info?.userId,
        userStore.info?.nickname,
        userStore.info?.phone
      ] as const,
    () => {
      if (userStore.info?.userId) {
        greetingText.value = getProfileGreetingText(userStore.info);
      }
    },
    { immediate: true }
  );
</script>

<style lang="scss" scoped>
  .profile-card {
    border-radius: 12px;
    /* 高度自适应内容，确保天气信息完整显示（不再强制与 Banner 等高） */
    min-height: 216px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
  }

  .profile-wrapper {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .profile-weather-widget {
    width: 100%;
  }

  .profile-header {
    display: flex;
    align-items: center;
    gap: 12px;

    .profile-avatar {
      flex-shrink: 0;
      background: var(--el-fill-color-light);
    }
  }

  .profile-header-body {
    flex: 1;
    min-width: 0;
  }

  .profile-greeting {
    font-size: 18px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    line-height: 1.4;
  }

  .profile-sub {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px 10px;
    margin-top: 6px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .profile-role {
    padding: 1px 8px;
    border-radius: 4px;
    font-size: 12px;
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }
</style>
