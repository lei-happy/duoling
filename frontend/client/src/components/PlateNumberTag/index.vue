<template>
  <span
    class="plate-number-tag"
    :class="[
      `plate-number-tag--${size}`,
      `plate-number-tag--${variant}`,
      { 'plate-number-tag--dimmed': dimmed }
    ]"
  >
    <slot>{{ displayText }}</slot>
  </span>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { PlateCategory } from '@/constants/plate-category';
  import { DEFAULT_PLATE_CATEGORY } from '@/constants/plate-category';
  import { formatPlateNumberDisplay } from '@/utils/plate-util';

  defineOptions({ name: 'PlateNumberTag' });

  const props = withDefaults(
    defineProps<{
      /** 无默认插槽时用文本展示 */
      text?: string;
      /** default：表格等；large：创建运力预览等强调场景 */
      size?: 'default' | 'large';
      /** 禁用行等弱化展示 */
      dimmed?: boolean;
      /** 蓝牌 / 黄牌 / 新能源；缺省为黄牌 */
      category?: PlateCategory;
    }>(),
    {
      size: 'default',
      dimmed: false,
      category: undefined
    }
  );

  const variant = computed(() => props.category ?? DEFAULT_PLATE_CATEGORY);

  const displayText = computed(() =>
    formatPlateNumberDisplay(props.text, variant.value)
  );
</script>

<style scoped>
  .plate-number-tag {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-sizing: border-box;
    /* 与字体大小联动，黄/蓝/新能源、7/8 位号牌统一视觉宽度（偏紧凑） */
    width: 7.5em;
    min-width: 7.5em;
    max-width: 100%;
    white-space: nowrap;
    font-weight: 700;
    border-radius: 4px;
    padding: 2px 4px;
    font-size: 13px;
    line-height: 1.35;
    vertical-align: middle;
    letter-spacing: 0.02em;
    font-variant-numeric: tabular-nums;
    border: 1px solid transparent;
  }

  .plate-number-tag--YELLOW {
    background: #ffcc00;
    color: #000;
    border-color: rgba(0, 0, 0, 0.35);
  }

  .plate-number-tag--BLUE {
    background: #1a4b8c;
    color: #fff;
    border-color: rgba(255, 255, 255, 0.85);
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.35);
  }

  .plate-number-tag--NEW_ENERGY {
    background: linear-gradient(
      180deg,
      #f8f9fb 0%,
      #ffffff 28%,
      #8fd99e 72%,
      #34a853 100%
    );
    color: #111;
    border-color: rgba(0, 0, 0, 0.55);
  }

  .plate-number-tag--large {
    font-size: 15px;
    padding: 3px 8px;
    border-radius: 5px;
  }

  .plate-number-tag--dimmed {
    opacity: 0.55;
  }
</style>
