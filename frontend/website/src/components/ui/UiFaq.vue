<template>
  <div class="faq">
    <details v-for="item in items" :key="item.q" class="faq-item">
      <summary>{{ item.q }}</summary>
      <div class="faq-body">{{ item.a }}</div>
    </details>
  </div>
</template>

<script setup lang="ts">
export interface FaqItem {
  q: string;
  a: string;
}

defineProps<{ items: FaqItem[] }>();
</script>

<style scoped lang="scss">
/*
 * 用原生 details/summary：键盘、屏幕阅读器、无 JS 场景全部开箱可用，
 * 手写一套 aria-expanded 只会更差。
 */
.faq {
  border-top: 1px solid var(--line);
}

.faq-item {
  border-bottom: 1px solid var(--line);
}

.faq-item summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 20px 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  list-style: none;

  &::-webkit-details-marker {
    display: none;
  }

  /* 加号旋转成叉，比换图标少一次重绘 */
  &::after {
    content: '+';
    font-family: var(--mono);
    font-size: 20px;
    font-weight: 400;
    color: var(--ink-3);
    transition: transform var(--dur-move) var(--ease);
    flex-shrink: 0;
  }
}

.faq-item[open] summary::after {
  transform: rotate(45deg);
  color: var(--brand);
}

.faq-body {
  padding: 0 4px 22px;
  color: var(--ink-2);
  font-size: 15px;
}

@media (hover: hover) and (pointer: fine) {
  .faq-item summary:hover {
    color: var(--brand);
  }
}

@media (prefers-reduced-motion: reduce) {
  .faq-item summary::after {
    transition: color var(--dur-move) var(--ease);
  }
}
</style>
