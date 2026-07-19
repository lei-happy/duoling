<!--
  自有运力列表 KPI 卡片
  ====================

  - 6 张状态卡：全部 / 空闲 / 运输中 / 休假 / 停运 / 维修保养中
  - 视觉沿用计划工作台 waybill-stats-cards（左侧色条 + 大号数字 + 副标题）
  - 点击卡片 emit `selectCard` 切换列表
-->
<template>
  <div class="cap-cards" :style="{ '--cap-cards-count': cards.length }">
    <button
      v-for="card in cards"
      :key="card.key"
      type="button"
      class="cap-card"
      :class="[
        `cap-card--${card.key}`,
        { 'is-selected': activeCardKey === card.key }
      ]"
      @click="emit('selectCard', card.key)"
    >
      <div class="cap-card__head">
        <span class="cap-card__accent-bar" aria-hidden="true"></span>
        <span class="cap-card__title">{{ card.label }}</span>
      </div>
      <div class="cap-card__metric">
        <span class="cap-card__value">{{ card.total }}</span>
        <span class="cap-card__unit">组</span>
      </div>
      <div class="cap-card__sub">{{ card.sub }}</div>
    </button>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { CapacityListStats } from '@/api/capacity/self-capacity/list/model';

  export type CapacityStatsCardKey =
    | 'all'
    | '1'
    | '2'
    | '3'
    | '4'
    | '5';

  const props = defineProps<{
    stats: CapacityListStats | null;
    activeCardKey?: CapacityStatsCardKey;
  }>();

  const emit = defineEmits<{
    (e: 'selectCard', cardKey: CapacityStatsCardKey): void;
  }>();

  interface CapacityCard {
    key: CapacityStatsCardKey;
    label: string;
    total: number;
    sub: string;
  }

  const CARD_DEFS: Array<{
    key: CapacityStatsCardKey;
    label: string;
    sub: string;
    statsKey: keyof CapacityListStats;
  }> = [
    {
      key: 'all',
      label: '全部',
      sub: '当前绑定中的运力',
      statsKey: 'total'
    },
    {
      key: '1',
      label: '空闲',
      sub: '可调度派单',
      statsKey: 'available'
    },
    {
      key: '2',
      label: '运输中',
      sub: '任务在途中',
      statsKey: 'inTransit'
    },
    {
      key: '3',
      label: '休假',
      sub: '暂不接单',
      statsKey: 'resting'
    },
    {
      key: '4',
      label: '停运',
      sub: '暂停运营',
      statsKey: 'stopped'
    },
    {
      key: '5',
      label: '维修保养中',
      sub: '维修模块锁定',
      statsKey: 'maintenance'
    }
  ];

  const cards = computed<CapacityCard[]>(() => {
    const t = props.stats;
    return CARD_DEFS.map((def) => ({
      key: def.key,
      label: def.label,
      total: t?.[def.statsKey] ?? 0,
      sub: def.sub
    }));
  });
</script>

<style lang="scss" scoped>
  .cap-cards {
    display: grid;
    grid-template-columns: repeat(var(--cap-cards-count, 6), minmax(0, 1fr));
    gap: 10px;
  }

  .cap-card {
    display: block;
    width: 100%;
    margin: 0;
    padding: 12px;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 12px;
    background: var(--el-bg-color);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    cursor: pointer;
    text-align: left;
    transition:
      border-color 0.2s cubic-bezier(0.23, 1, 0.32, 1),
      box-shadow 0.2s cubic-bezier(0.23, 1, 0.32, 1),
      background 0.2s cubic-bezier(0.23, 1, 0.32, 1),
      transform 0.16s cubic-bezier(0.23, 1, 0.32, 1);

    --cap-accent: var(--el-color-primary);
    --cap-soft-bg: var(--el-color-primary-light-9);
    --cap-soft-ring: var(--el-color-primary-light-7);

    &--all {
      --cap-accent: var(--el-color-primary);
      --cap-soft-bg: var(--el-color-primary-light-9);
      --cap-soft-ring: var(--el-color-primary-light-7);
    }
    &--1 {
      --cap-accent: var(--el-color-success);
      --cap-soft-bg: var(--el-color-success-light-9);
      --cap-soft-ring: var(--el-color-success-light-7);
    }
    &--2 {
      --cap-accent: var(--el-color-primary);
      --cap-soft-bg: var(--el-color-primary-light-9);
      --cap-soft-ring: var(--el-color-primary-light-7);
    }
    &--3 {
      --cap-accent: var(--el-text-color-secondary);
      --cap-soft-bg: var(--el-fill-color-light);
      --cap-soft-ring: var(--el-border-color);
    }
    &--4 {
      --cap-accent: var(--el-color-danger);
      --cap-soft-bg: var(--el-color-danger-light-9);
      --cap-soft-ring: var(--el-color-danger-light-7);
    }
    &--5 {
      --cap-accent: var(--el-color-warning);
      --cap-soft-bg: var(--el-color-warning-light-9);
      --cap-soft-ring: var(--el-color-warning-light-7);
    }

    &.is-selected {
      background: var(--cap-soft-bg);
      border-color: var(--cap-accent);
      box-shadow: 0 0 0 1px var(--cap-soft-ring);
    }

    @media (hover: hover) and (pointer: fine) {
      &:hover {
        border-color: var(--cap-accent);
      }

      &:active {
        transform: scale(0.97);
      }
    }

    &__head {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
    }

    &__accent-bar {
      flex-shrink: 0;
      width: 3px;
      height: 15px;
      border-radius: 999px;
      background: var(--cap-accent);
      box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.35),
        inset 0 -1px 2px rgba(0, 0, 0, 0.12);
    }

    &__title {
      font-size: 13px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      letter-spacing: 0.02em;
      white-space: nowrap;
    }

    &__metric {
      display: flex;
      align-items: baseline;
      gap: 4px;
    }

    &__value {
      font-size: 26px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
      line-height: 1.1;
      color: var(--el-text-color-primary);
    }

    &__unit {
      font-size: 11px;
      color: var(--el-text-color-placeholder);
    }

    &__sub {
      margin-top: 4px;
      font-size: 11px;
      color: var(--el-text-color-secondary);
      line-height: 1.3;
    }
  }
</style>
