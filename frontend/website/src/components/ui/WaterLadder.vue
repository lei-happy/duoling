<template>
  <div class="ladder">
    <div v-if="$slots.head" class="ladder-head">
      <slot name="head" />
    </div>

    <div class="ladder-track">
      <!--
        指针轨：与刻度尺等宽，所以 translateX 的百分比正好等于刻度尺上的位置。
        用 transform 而不是 left，位移才走合成层。
      -->
      <div
        v-if="index"
        class="ladder-rail"
        :style="{ transform: `translate3d(${pointerLeft}%, 0, 0)` }"
      >
        <span class="ladder-pointer">{{ pointerLabel }}</span>
      </div>

      <i
        v-for="seg in 8"
        :key="seg"
        class="ladder-seg"
        :class="{
          'is-on': index !== null && seg <= index,
          'is-current': index !== null && seg === index
        }"
        :data-tier="tierOf(seg)"
      />
    </div>

    <div v-if="showScale" class="ladder-scale">
      <span v-for="s in SCALE" :key="s.range">
        <b>{{ s.range }}</b>
        {{ s.name }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, toRef } from 'vue';
import { useSpringValue } from '@/composables/useSpringValue';

/**
 * 水位刻度尺 —— 全站唯一的记忆点，贯穿首页、转型页与自测页。
 *
 * 八格对应 L1–L8，四段色阶对应信息化 / 数字化 / 智能化 / 数智化。
 * 指针用弹簧驱动：自测页里用户连点选项时，它要能从当前位置带着速度
 * 改道，而不是每次重新从头滑一遍。
 */

const props = withDefaults(
  defineProps<{
    /** 当前档位 1–8；null 表示还没开始作答，整条尺子保持灰色 */
    index: number | null;
    /** 指针上的文字，如 L3 或「多数企业」 */
    pointerLabel?: string;
    /** 是否显示下方四段刻度说明 */
    showScale?: boolean;
  }>(),
  { pointerLabel: '', showScale: true }
);

const SCALE = [
  { range: 'L1–L2', name: '信息化' },
  { range: 'L3–L4', name: '数字化' },
  { range: 'L5–L6', name: '智能化' },
  { range: 'L7–L8', name: '数智化' }
] as const;

/** 每两格归一段，与四层能力一一对应 */
function tierOf(seg: number) {
  return Math.ceil(seg / 2);
}

// 指针落在当前格的正中间
const targetLeft = computed(() =>
  props.index ? ((props.index - 0.5) / 8) * 100 : 6
);

const pointerLeft = useSpringValue(toRef(targetLeft), {
  damping: 0.85,
  response: 0.35
});
</script>

<style scoped lang="scss">
.ladder-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.ladder-track {
  position: relative;
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 3px;
  height: 12px;
  margin-top: 26px;
}

.ladder-seg {
  border-radius: 2px;
  background: var(--bg-2);
  transition:
    background var(--dur-move) var(--ease),
    transform var(--dur-move) var(--ease);
}

.ladder-seg[data-tier='1'].is-on {
  background: var(--tier-1);
}
.ladder-seg[data-tier='2'].is-on {
  background: var(--tier-2);
}
.ladder-seg[data-tier='3'].is-on {
  background: var(--tier-3);
}
.ladder-seg[data-tier='4'].is-on {
  background: var(--tier-4);
}

/* 当前档位加高一截，扫一眼就知道停在哪 */
.ladder-seg.is-current {
  background: var(--brand);
  transform: scaleY(1.5);
}

.ladder-rail {
  position: absolute;
  left: 0;
  right: 0;
  top: -22px;
  height: 0;
  pointer-events: none;
  will-change: transform;
}

.ladder-pointer {
  position: absolute;
  left: 0;
  transform: translateX(-50%);
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 600;
  color: var(--brand);
  white-space: nowrap;

  &::after {
    content: '';
    display: block;
    width: 1px;
    height: 8px;
    margin: 2px auto 0;
    background: var(--brand);
  }
}

.ladder-scale {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 3px;
  margin-top: 12px;

  span {
    font-size: 12px;
    color: var(--ink-3);
    padding-top: 8px;
    border-top: 1px solid var(--line);
  }

  b {
    display: block;
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 500;
    color: var(--ink-3);
    letter-spacing: 0.06em;
  }
}

/* 深底反转：祖先在别的组件上，scoped 只给最后一个选择器加属性 */
.band-deep .ladder-seg,
.result[data-tier='4'] .ladder-seg {
  background: rgba(255, 255, 255, 0.12);
}

.band-deep .ladder-seg.is-current,
.result[data-tier='4'] .ladder-seg.is-current {
  background: var(--brand-on-dark);
}

.band-deep .ladder-pointer,
.result[data-tier='4'] .ladder-pointer {
  color: var(--brand-on-dark);

  &::after {
    background: var(--brand-on-dark);
  }
}

.band-deep .ladder-scale span,
.result[data-tier='4'] .ladder-scale span {
  color: rgba(244, 247, 252, 0.55);
  border-top-color: var(--line-dark);
}

.band-deep .ladder-scale b,
.result[data-tier='4'] .ladder-scale b {
  color: rgba(244, 247, 252, 0.55);
}

@media (max-width: 768px) {
  .ladder-scale {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px 3px;
  }
}

/* 当前档加高是状态标识而非动效，减弱动态时保留高度、只去掉过渡 */
@media (prefers-reduced-motion: reduce) {
  .ladder-seg {
    transition: background var(--dur-move) var(--ease);
  }
}
</style>
