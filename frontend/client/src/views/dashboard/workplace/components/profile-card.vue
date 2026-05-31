<!-- 用户信息 + 今日需关注 -->
<template>
  <ele-card :body-style="{ padding: '20px' }">
    <div class="profile-wrapper">
      <div class="profile-main">
        <el-avatar :size="68" :src="loginUser.avatar" class="profile-avatar" />
        <div class="profile-body">
          <ele-text size="xl" type="heading" style="font-weight: normal">
            {{ greetingText }}
          </ele-text>
          <ele-text type="placeholder" :icon="PartlyCloudy">
            今日多云转阴, 18℃ ~ 22℃, 出门记得穿外套哦~
          </ele-text>
        </div>
      </div>
      <div v-if="items.length" class="profile-count">
        <button
          v-for="item in items"
          :key="item.key"
          type="button"
          class="profile-count-item"
          :class="{ 'is-urgent': item.urgent }"
          @click="goMetric(item)"
        >
          <div class="profile-count-header">
            <el-tag
              size="large"
              :type="item.tagType"
              :disable-transitions="true"
            >
              <el-icon>
                <component :is="iconMap[item.icon]" />
              </el-icon>
            </el-tag>
            <span class="profile-count-name">{{ item.label }}</span>
          </div>
          <ele-text
            size="xl"
            type="heading"
            class="profile-count-value"
            style="font-weight: normal"
          >
            <template v-if="loading">—</template>
            <template v-else>{{ formatCount(item.value) }}</template>
          </ele-text>
        </button>
      </div>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import { DocumentChecked, Promotion, Select, PartlyCloudy } from '@element-plus/icons-vue';
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
  .profile-wrapper {
    display: flex;
    align-items: center;

    .profile-main {
      flex: 1;
      display: flex;
      align-items: center;
      overflow: hidden;

      .profile-avatar {
        flex-shrink: 0;
        background: none;
      }

      .profile-body {
        flex: 1;
        padding-left: 12px;
        box-sizing: border-box;
      }
    }
  }

  .profile-count {
    flex-shrink: 0;
    text-align: right;
    white-space: nowrap;

    .profile-count-item {
      display: inline-block;
      margin: 0 4px 0 24px;
      padding: 0;
      border: none;
      background: none;
      cursor: pointer;
      text-align: right;
      color: inherit;
      transition: opacity 0.15s ease;

      &:hover {
        opacity: 0.82;
      }

      .el-tag {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        line-height: 0;
        padding: 0;
      }

      .profile-count-name {
        margin-left: 8px;
      }

      .profile-count-header {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        margin-bottom: 4px;
      }

      .profile-count-value {
        transition: color 0.15s ease;
      }

      &.is-urgent .profile-count-value {
        color: var(--el-color-warning);
      }
    }
  }

  @media screen and (max-width: 992px) {
    .profile-count .profile-count-item {
      margin: 0 2px 0 12px;
    }
  }

  @media screen and (max-width: 768px) {
    .profile-wrapper {
      display: block;

      .profile-count {
        margin-top: 14px;
        text-align: left;

        .profile-count-item {
          margin: 0 16px 0 0;
          text-align: left;

          .profile-count-header {
            justify-content: flex-start;
          }
        }
      }
    }
  }
</style>
