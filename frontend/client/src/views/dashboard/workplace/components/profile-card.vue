<!-- 用户问候 + 今日需关注统计 -->
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
            <span class="profile-weather">
              <el-icon class="profile-weather-icon"><PartlyCloudy /></el-icon>
              今日多云转阴 18℃~22℃
            </span>
          </div>
        </div>
      </div>

      <!-- 今日需关注统计卡片组 -->
      <div v-if="items.length" class="profile-stats">
        <button
          v-for="item in items"
          :key="item.key"
          type="button"
          class="profile-stat"
          :class="{ 'is-urgent': item.urgent }"
          @click="goMetric(item)"
        >
          <div class="profile-stat-info">
            <span class="profile-stat-label">{{ item.label }}</span>
            <span class="profile-stat-value">
              <template v-if="loading">—</template>
              <template v-else>{{ formatCount(item.value) }}</template>
            </span>
          </div>
          <el-icon class="profile-stat-icon">
            <component :is="iconMap[item.icon]" />
          </el-icon>
        </button>
      </div>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import {
    DocumentChecked,
    Promotion,
    Select,
    PartlyCloudy
  } from '@element-plus/icons-vue';
  import { useUserStore } from '@/store/modules/user';
  import { getProfileGreetingText } from '../utils/profile-greeting';
  import {
    useAttentionMetrics,
    type AttentionMetricItem
  } from '../attention-metrics/use-attention-metrics';

  const router = useRouter();
  const userStore = useUserStore();
  const { loading, items, reload } = useAttentionMetrics();

  const iconMap: Record<string, object> = {
    DocumentChecked,
    Promotion,
    Select
  };

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

  const formatCount = (value: number | null) => {
    if (value == null) {
      return '—';
    }
    return value.toLocaleString('zh-CN');
  };

  const goMetric = (item: AttentionMetricItem) => {
    router.push(item.route);
  };

  defineExpose({ reloadMetrics: reload });
</script>

<style lang="scss" scoped>
  .profile-card {
    border-radius: 12px;
    height: 216px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;

    :deep(.ele-card-body) {
      flex: 1;
      min-height: 0;
    }
  }

  .profile-wrapper {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 18px;
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

  .profile-weather {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    white-space: nowrap;
  }

  .profile-weather-icon {
    font-size: 14px;
    color: var(--el-color-warning);
  }

  /* 统计卡片组 */
  .profile-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }

  .profile-stat {
    flex: 1 1 0;
    min-width: 120px;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 16px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    text-align: left;
    background: linear-gradient(135deg, #eaf4ff 0%, #eff6ff 100%);
    transition:
      transform 0.2s ease,
      box-shadow 0.2s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(22, 93, 255, 0.14);
    }
  }

  .profile-stat-info {
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-width: 0;
  }

  .profile-stat-label {
    font-size: 13px;
    color: #4e5969;
    white-space: nowrap;
  }

  .profile-stat-value {
    font-size: 26px;
    font-weight: 700;
    line-height: 1;
    color: var(--el-color-primary);
  }

  .profile-stat.is-urgent .profile-stat-value {
    color: var(--el-color-primary);
  }

  .profile-stat-icon {
    font-size: 34px;
    color: rgba(22, 93, 255, 0.16);
    flex-shrink: 0;
  }

  @media screen and (max-width: 480px) {
    .profile-stat {
      flex-basis: 100%;
    }
  }
</style>
