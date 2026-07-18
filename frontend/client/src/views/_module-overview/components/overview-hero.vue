<template>
  <div
    class="overview-hero"
    :class="{ 'overview-hero--wide': isWideArt }"
    :style="accentVars"
  >
    <div class="overview-hero__text">
      <div class="overview-hero__eyebrow">模块总览</div>
      <h2 class="overview-hero__title">{{ title }}</h2>
      <p class="overview-hero__positioning">{{ positioning }}</p>
      <p v-if="description" class="overview-hero__desc">{{ description }}</p>
    </div>
    <div class="overview-hero__art">
      <img
        v-if="illustration"
        :src="illustration"
        :alt="title"
        :style="imgStyle"
      />
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
  import OverviewIcon from './overview-icon.vue';

  defineOptions({ name: 'OverviewHero' });

  const props = defineProps<{
    title?: string;
    positioning?: string;
    description?: string;
    illustration?: string;
    /** 插画宽高比，如 4 表示 4:1 */
    aspectRatio?: number;
    heroIcon?: string;
    accentColor?: string;
  }>();

  const isWideArt = computed(
    () => typeof props.aspectRatio === 'number' && props.aspectRatio >= 3
  );

  const accentVars = computed<CSSProperties>(() => ({
    '--overview-accent': props.accentColor || 'var(--el-color-primary)'
  }));

  const imgStyle = computed<CSSProperties | undefined>(() => {
    if (!props.aspectRatio) return undefined;
    return { aspectRatio: `${props.aspectRatio} / 1` };
  });
</script>

<style lang="scss" scoped>
  .overview-hero {
    position: relative;
    display: flex;
    align-items: center;
    gap: 24px;
    min-height: 148px;
    padding: 20px 28px;
    border-radius: 14px;
    overflow: hidden;
    background: linear-gradient(
      118deg,
      color-mix(in srgb, var(--overview-accent) 20%, #ffffff) 0%,
      color-mix(in srgb, var(--overview-accent) 8%, #ffffff) 40%,
      var(--el-bg-color) 100%
    );
    border: 1px solid
      color-mix(
        in srgb,
        var(--overview-accent) 16%,
        var(--el-border-color-lighter)
      );
  }

  .overview-hero__text {
    flex: 0 1 auto;
    min-width: 0;
    max-width: 460px;
  }

  .overview-hero--wide .overview-hero__text {
    max-width: 400px;
  }

  .overview-hero__eyebrow {
    display: inline-block;
    font-size: 12px;
    line-height: 20px;
    padding: 0 10px;
    border-radius: 10px;
    color: var(--overview-accent);
    background: color-mix(in srgb, var(--overview-accent) 14%, #ffffff);
    margin-bottom: 12px;
  }

  .overview-hero__title {
    margin: 0 0 8px;
    font-size: 22px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .overview-hero__positioning {
    margin: 0;
    font-size: 13px;
    line-height: 1.6;
    color: var(--el-text-color-regular);
    max-width: 720px;
  }

  .overview-hero__desc {
    margin: 8px 0 0;
    font-size: 13px;
    line-height: 1.6;
    color: var(--el-text-color-secondary);
    max-width: 720px;
  }

  .overview-hero__art {
    flex: 1 1 auto;
    align-self: center;
    min-width: 0;
    display: flex;
    justify-content: center;
    align-items: center;

    img {
      width: 100%;
      max-width: 360px;
      height: auto;
      display: block;
      object-fit: contain;
      object-position: center;
    }
  }

  .overview-hero--wide .overview-hero__art {
    justify-content: flex-end;

    img {
      max-width: min(100%, 640px);
      max-height: 160px;
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
      width: 100%;
      max-width: 420px;
      justify-content: center;
    }

    .overview-hero--wide .overview-hero__art {
      max-width: 100%;
      justify-content: center;

      img {
        max-width: 100%;
        max-height: none;
      }
    }
  }
</style>
