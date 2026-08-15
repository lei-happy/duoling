<template>
  <div
    class="banner"
    tabindex="0"
    role="group"
    :aria-label="label"
    @keydown="onKeydown"
  >
    <div class="banner-view">
      <div
        class="banner-track"
        :style="{ transform: `translate3d(-${current * 100}%, 0, 0)` }"
      >
        <!--
          划走的那几屏仍在 DOM 里，不 inert 的话读屏会把四层内容连着念完，
          Tab 也会跳进看不见的链接。用 undefined 而不是 false，避免渲染出
          inert="false" —— 这个属性只要存在就生效。
        -->
        <div
          v-for="i in indexes"
          :key="i"
          class="banner-slide"
          :inert="i !== current || undefined"
          :aria-hidden="i !== current || undefined"
        >
          <slot :name="`slide-${i}`" />
        </div>
      </div>
    </div>

    <div class="banner-ctrl">
      <div class="banner-dots">
        <button
          v-for="i in indexes"
          :key="i"
          type="button"
          class="banner-dot"
          :class="{ 'is-on': i === current }"
          :aria-current="i === current"
          :aria-label="`第 ${i + 1} 层`"
          @click="go(i)"
        />
      </div>
      <div class="banner-arrows">
        <button
          type="button"
          class="banner-arrow"
          aria-label="上一层"
          :disabled="current === 0"
          @click="go(current - 1)"
        >
          ←
        </button>
        <button
          type="button"
          class="banner-arrow"
          aria-label="下一层"
          :disabled="current === count - 1"
          @click="go(current + 1)"
        >
          →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

/**
 * 横向幻灯，用于「对照一下，你的企业在哪一层」四层展示。
 *
 * 不自动播放：这里每一屏都是需要读完的内容，自己会走的轮播只会打断阅读。
 */

const props = defineProps<{
  /** 幻灯片数量，配合 slide-0 / slide-1 ... 具名插槽使用 */
  count: number;
  label: string;
}>();

/** 0 起的下标序列，和具名插槽 slide-0 / slide-1 … 对齐 */
const indexes = computed(() => Array.from({ length: props.count }, (_, i) => i));

const current = ref(0);

function go(i: number) {
  current.value = Math.min(Math.max(i, 0), props.count - 1);
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'ArrowLeft') {
    event.preventDefault();
    go(current.value - 1);
  } else if (event.key === 'ArrowRight') {
    event.preventDefault();
    go(current.value + 1);
  }
}
</script>

<style scoped lang="scss">
.banner {
  border-radius: var(--r-lg);
  background: var(--paper);
  overflow: hidden;
  box-shadow: var(--shadow-sm);

  &:focus-visible {
    outline: 2px solid var(--brand);
    outline-offset: 2px;
  }
}

.banner-view {
  overflow: hidden;
}

.banner-track {
  display: flex;
  transition: transform var(--dur-move) var(--ease);
}

.banner-slide {
  flex: 0 0 100%;
  min-width: 0;
  padding: 30px;
}

.banner-ctrl {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 20px;
  border-top: 1px solid var(--line);
  background: var(--bg);
}

.banner-dots {
  display: flex;
  gap: 8px;
}

.banner-dot {
  width: 24px;
  height: 4px;
  padding: 0;
  border: 0;
  border-radius: 2px;
  background: var(--ink-4);
  cursor: pointer;
  transition: background var(--dur-hover) var(--ease);

  &.is-on {
    background: var(--brand);
  }
}

.banner-arrows {
  display: flex;
  gap: 8px;
}

.banner-arrow {
  width: 32px;
  height: 32px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  background: var(--paper);
  font-family: var(--mono);
  color: var(--ink-2);
  cursor: pointer;
  transition:
    border-color var(--dur-hover) var(--ease),
    color var(--dur-hover) var(--ease);

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

@media (hover: hover) and (pointer: fine) {
  .banner-arrow:hover:not(:disabled) {
    border-color: var(--brand);
    color: var(--brand);
  }
}

@media (max-width: 768px) {
  .banner-slide {
    padding: 22px 20px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .banner-track {
    transition: none;
  }
}
</style>
