<!-- 用户问候 + 天气预报 -->
<template>
  <ele-card
    shadow="never"
    class="profile-card"
    :class="{
      'is-synced': !!height,
      'is-compact': isCompact
    }"
    :body-style="bodyStyle"
    :style="cardStyle"
  >
    <div class="profile-wrapper">
      <!-- 背景点缀层 -->
      <div class="profile-bg" aria-hidden="true">
        <span class="profile-bg__ring"></span>
        <span class="profile-bg__orb profile-bg__orb--1"></span>
        <span class="profile-bg__orb profile-bg__orb--2"></span>
        <span class="profile-bg__dot profile-bg__dot--1"></span>
        <span class="profile-bg__dot profile-bg__dot--2"></span>
        <span class="profile-bg__dot profile-bg__dot--3"></span>
      </div>

      <!-- 头像 + 问候 -->
      <div class="profile-header">
        <el-avatar
          :size="isCompact ? 40 : 48"
          :src="loginUser.avatar"
          class="profile-avatar"
        />
        <div class="profile-header-body">
          <div class="profile-name">你好，{{ displayName }}</div>
          <div v-if="greetingMessage" class="profile-greeting">
            {{ greetingMessage }}
          </div>
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
  import type { CSSProperties } from 'vue';
  import { useUserStore } from '@/store/modules/user';
  import { getProfileGreetingParts } from '../utils/profile-greeting';
  import WeatherWidget from './weather-widget.vue';

  /** 同步高度低于此值时启用更紧凑的字号/间距 */
  const COMPACT_HEIGHT_PX = 220;

  const props = defineProps<{
    /** 与 Banner 同步的顶部行高度，由父级 workplace 注入（Banner 5:1 定高） */
    height?: string;
  }>();

  const syncedHeightPx = computed(() => {
    if (!props.height) return 0;
    const n = Number.parseFloat(props.height);
    return Number.isFinite(n) ? n : 0;
  });

  const isCompact = computed(
    () =>
      !!props.height &&
      syncedHeightPx.value > 0 &&
      syncedHeightPx.value < COMPACT_HEIGHT_PX
  );

  const cardStyle = computed(() =>
    props.height ? { height: props.height } : undefined
  );

  /** 跟随 Banner 定高时减小 padding，优先保证天气插件 60px 完整可见 */
  const bodyStyle = computed<CSSProperties>(() => {
    let padding = '20px';
    if (props.height) {
      padding = isCompact.value ? '8px 14px 6px' : '12px 16px 8px';
    }
    return {
      padding,
      height: '100%',
      boxSizing: 'border-box'
    };
  });

  const userStore = useUserStore();

  /** 当前登录用户信息 */
  const loginUser = computed(() => userStore.info ?? {});

  /** 角色名称（取首个角色） */
  const roleName = computed(
    () => userStore.info?.roles?.[0]?.roleName?.trim() || ''
  );

  /** 问候展示名 */
  const displayName = ref('伙伴');
  /** 祝福语（不含用户名） */
  const greetingMessage = ref('');

  /** 按上海时段随机问候（仅用户身份变化时刷新，避免快捷操作等偏好保存触发重随机） */
  watch(
    () =>
      [
        userStore.info?.userId,
        userStore.info?.nickname,
        userStore.info?.phone
      ] as const,
    () => {
      if (userStore.info?.userId) {
        const parts = getProfileGreetingParts(userStore.info);
        displayName.value = parts.displayName;
        greetingMessage.value = parts.message;
      }
    },
    { immediate: true }
  );
</script>

<style lang="scss" scoped>
  .profile-card {
    border-radius: 12px;
    min-height: 216px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-sizing: border-box;

    /* 大屏跟随 Banner 定高时取消 min-height，避免撑破 5:1 同步高度 */
    &.is-synced {
      min-height: 0;
    }

    :deep(.ele-card-body) {
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
  }

  .profile-wrapper {
    position: relative;
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    z-index: 1;
  }

  .profile-bg {
    position: absolute;
    inset: -20px;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
    background:
      radial-gradient(
        120% 100% at 100% 0%,
        rgba(99, 173, 255, 0.22) 0%,
        rgba(99, 173, 255, 0) 58%
      ),
      linear-gradient(145deg, #f0f6ff 0%, #ffffff 52%, #f8fbff 100%);
    border-radius: 12px;

    &__ring {
      position: absolute;
      top: -36px;
      right: -36px;
      width: 128px;
      height: 128px;
      border: 2px solid rgba(22, 93, 255, 0.1);
      border-radius: 50%;
    }

    &__orb {
      position: absolute;
      border-radius: 50%;

      &--1 {
        top: 12px;
        right: 48px;
        width: 56px;
        height: 56px;
        background: radial-gradient(
          circle at 30% 30%,
          rgba(255, 255, 255, 0.95) 0%,
          rgba(99, 173, 255, 0.28) 100%
        );
        opacity: 0.85;
      }

      &--2 {
        top: 52px;
        right: 8px;
        width: 32px;
        height: 32px;
        background: rgba(22, 93, 255, 0.12);
      }
    }

    &__dot {
      position: absolute;
      border-radius: 50%;
      background: rgba(22, 93, 255, 0.18);

      &--1 {
        top: 28px;
        right: 118px;
        width: 6px;
        height: 6px;
      }

      &--2 {
        top: 18px;
        right: 92px;
        width: 4px;
        height: 4px;
        opacity: 0.6;
      }

      &--3 {
        top: 64px;
        right: 108px;
        width: 5px;
        height: 5px;
        opacity: 0.45;
      }
    }
  }

  .profile-weather-widget {
    position: relative;
    z-index: 1;
    width: 100%;
    margin-top: auto;
    padding-top: 12px;
    /* 天气 iframe 固定 60px，禁止被压缩裁切 */
    flex-shrink: 0;
    min-height: 60px;
  }

  /* 跟随 Banner 定高：收紧上下留白，把空间留给天气 */
  .profile-card.is-synced {
    .profile-weather-widget {
      padding-top: 8px;
    }

    .profile-sub {
      margin-top: 6px;
    }

    .profile-greeting {
      margin-top: 4px;
    }
  }

  .profile-header {
    position: relative;
    z-index: 1;
    display: flex;
    margin-top: 12px;
    align-items: flex-start;
    gap: 12px;
    flex-shrink: 0;

    .profile-avatar {
      flex-shrink: 0;
      background: var(--el-fill-color-light);
      box-shadow:
        0 0 0 2px rgba(255, 255, 255, 0.9),
        0 4px 12px rgba(22, 93, 255, 0.12);
    }
  }

  .profile-header-body {
    flex: 1;
    min-width: 0;
    padding-top: 2px;
  }

  .profile-name {
    font-size: 20px;
    font-weight: 700;
    color: var(--el-text-color-primary);
    line-height: 1.35;
    letter-spacing: 0.2px;
  }

  .profile-greeting {
    margin-top: 6px;
    font-size: 14px;
    font-weight: 400;
    color: var(--el-text-color-secondary);
    line-height: 1.55;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    overflow: hidden;
  }

  .profile-sub {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px 10px;
    margin-top: 8px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .profile-role {
    padding: 1px 8px;
    border-radius: 4px;
    font-size: 12px;
    color: var(--el-color-primary);
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid rgba(22, 93, 255, 0.12);
  }

  /* 定高较矮时进一步压缩字号与间距 */
  .profile-card.is-compact {
    .profile-header {
      gap: 8px;
    }

    .profile-header-body {
      padding-top: 0;
    }

    .profile-name {
      font-size: 16px;
      line-height: 1.25;
    }

    .profile-greeting {
      margin-top: 2px;
      font-size: 12px;
      line-height: 1.35;
      -webkit-line-clamp: 1;
    }

    .profile-sub {
      margin-top: 2px;
    }

    .profile-weather-widget {
      padding-top: 4px;
    }
  }
</style>
