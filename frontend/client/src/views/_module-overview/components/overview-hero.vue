<template>
  <div class="overview-hero" :style="accentVars">
    <div class="overview-hero__text">
      <div class="overview-hero__eyebrow">模块总览</div>
      <h2 class="overview-hero__title">{{ title }}</h2>
      <p class="overview-hero__positioning">{{ positioning }}</p>
      <p v-if="description" class="overview-hero__desc">{{ description }}</p>
      <div v-if="quickActions?.length" class="overview-hero__actions">
        <el-button
          v-for="action in quickActions"
          :key="action.path"
          :type="action.primary ? 'primary' : 'default'"
          round
          @click="emit('navigate', action.path)"
        >
          <overview-icon
            v-if="action.icon"
            :name="action.icon"
            style="margin-right: 6px; font-size: 15px"
          />
          {{ action.title }}
        </el-button>
      </div>
    </div>
    <div class="overview-hero__art">
      <img v-if="illustration" :src="illustration" :alt="title" />
      <div v-else class="overview-hero__motif">
        <span
          class="overview-hero__motif-dot overview-hero__motif-dot--a"
        ></span>
        <span
          class="overview-hero__motif-dot overview-hero__motif-dot--b"
        ></span>
        <overview-icon :name="heroIcon || 'default'" />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { CSSProperties } from 'vue';
  import type { OverviewQuickAction } from '@/config/module-overview/types';
  import OverviewIcon from './overview-icon.vue';

  defineOptions({ name: 'OverviewHero' });

  const props = defineProps<{
    title?: string;
    positioning?: string;
    description?: string;
    illustration?: string;
    heroIcon?: string;
    accentColor?: string;
    quickActions?: OverviewQuickAction[];
  }>();

  const emit = defineEmits<{
    (e: 'navigate', path: string): void;
  }>();

  const accentVars = computed<CSSProperties>(() => ({
    '--overview-accent': props.accentColor || 'var(--el-color-primary)'
  }));
</script>

<style lang="scss" scoped>
  .overview-hero {
    position: relative;
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 28px 32px 28px 36px;
    border-radius: 12px;
    overflow: hidden;
    background: linear-gradient(
      120deg,
      var(--el-color-primary-light-9),
      var(--el-bg-color)
    );
    border: 1px solid var(--el-border-color-lighter);

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 4px;
      background: var(--overview-accent);
    }
  }

  .overview-hero__text {
    flex: 1 1 auto;
    min-width: 0;
  }

  .overview-hero__eyebrow {
    display: inline-block;
    font-size: 12px;
    line-height: 20px;
    padding: 0 10px;
    border-radius: 10px;
    color: var(--overview-accent);
    background: var(--el-color-primary-light-9);
    margin-bottom: 12px;
  }

  .overview-hero__title {
    margin: 0 0 10px;
    font-size: 24px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .overview-hero__positioning {
    margin: 0;
    font-size: 14px;
    line-height: 1.7;
    color: var(--el-text-color-regular);
    max-width: 720px;
  }

  .overview-hero__desc {
    margin: 10px 0 0;
    font-size: 13px;
    line-height: 1.7;
    color: var(--el-text-color-secondary);
    max-width: 720px;
  }

  .overview-hero__actions {
    margin-top: 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }

  .overview-hero__art {
    flex: 0 0 auto;
    width: 300px;
    max-width: 38%;
    display: flex;
    justify-content: center;

    img {
      width: 100%;
      height: auto;
      display: block;
    }
  }

  .overview-hero__motif {
    position: relative;
    width: 160px;
    height: 160px;
    border-radius: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--overview-accent);
    background: linear-gradient(
      135deg,
      var(--el-color-primary-light-9),
      var(--el-bg-color)
    );
    border: 1px solid var(--el-border-color-lighter);

    .overview-icon {
      font-size: 72px;
    }
  }

  .overview-hero__motif-dot {
    position: absolute;
    border-radius: 50%;
    background: var(--overview-accent);
    opacity: 0.16;
  }

  .overview-hero__motif-dot--a {
    width: 46px;
    height: 46px;
    top: -14px;
    right: -14px;
  }

  .overview-hero__motif-dot--b {
    width: 26px;
    height: 26px;
    bottom: -8px;
    left: -8px;
    opacity: 0.24;
  }

  @media screen and (max-width: 860px) {
    .overview-hero {
      flex-direction: column-reverse;
      align-items: flex-start;
    }

    .overview-hero__art {
      width: 200px;
      max-width: 60%;
    }
  }
</style>
