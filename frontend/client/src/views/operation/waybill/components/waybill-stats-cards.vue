<!--
  运单工作台 KPI 卡片
  ====================

  - 7 张状态卡：待确认 / 待调度 / 调度中 / 运输中 / 已送达 / 已完成 / 已关闭
  - 仅展示主数字 + 标题（"简单统计"），不做"常 / 警"分桶
  - 点击卡片 emit `selectCard` 切换列表

  视觉沿用 task-workbench/kpi-cards.vue 的设计语言（左侧色条 + 大号数字 + 副标题）。
  栅格固定 7 列、永远单行——窄桌面上单卡会被压缩，但相比换行更易扫读。
-->
<template>
  <div
    class="wb-cards"
    :style="{ '--wb-cards-count': cards.length }"
  >
    <button
      v-for="card in cards"
      :key="card.key"
      type="button"
      class="wb-card"
      :class="[
        `wb-card--${card.key}`,
        { 'is-selected': activeCardKey === card.key }
      ]"
      @click="emit('selectCard', card.key)"
    >
      <div class="wb-card__head">
        <span class="wb-card__accent-bar" aria-hidden="true"></span>
        <span class="wb-card__title">{{ card.label }}</span>
      </div>
      <div class="wb-card__metric">
        <span class="wb-card__value">{{ card.total }}</span>
        <span class="wb-card__unit">单</span>
      </div>
      <div class="wb-card__sub">{{ card.sub }}</div>
    </button>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { WaybillWorkbenchStats } from '@/api/waybill/model';
  import { WAYBILL_POOLS } from '../waybill-pool-registry';

  const props = defineProps<{
    stats: WaybillWorkbenchStats | null;
    activeCardKey?: string;
    /** 自动确认开关打开 AND 待确认数=0 时，隐藏「待确认」卡片 */
    pendingConfirmHidden?: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'selectCard', cardKey: string): void;
  }>();

  interface WaybillCard {
    key: string;
    label: string;
    total: number;
    sub: string;
  }

  /** 各 pool key → totals 字段名 */
  const TOTAL_KEY_MAP: Record<string, keyof WaybillWorkbenchStats['totals']> = {
    'pending-confirm': 'pendingConfirm',
    'pending-dispatch': 'pendingDispatch',
    scheduling: 'scheduling',
    'in-transit': 'inTransit',
    delivered: 'delivered',
    completed: 'completed',
    closed: 'closed'
  };

  /** 副标题文案（业务语义提示） */
  const SUB_TEXT: Record<string, string> = {
    'pending-confirm': '新建待运营确认',
    'pending-dispatch': '待挂接到任务单',
    scheduling: '部分挂接进行中',
    'in-transit': '部分或全部在途',
    delivered: '全部货物已到达',
    completed: '全部签收',
    closed: '终态'
  };

  const cards = computed<WaybillCard[]>(() => {
    const t = props.stats?.totals;
    return WAYBILL_POOLS.filter(
      (pool) => !(pool.key === 'pending-confirm' && props.pendingConfirmHidden)
    ).map((pool) => {
      const k = TOTAL_KEY_MAP[pool.key];
      const total = k && t ? (t[k] ?? 0) : 0;
      return {
        key: pool.key,
        label: pool.label,
        total,
        sub: SUB_TEXT[pool.key] ?? ''
      };
    });
  });
</script>

<style lang="scss" scoped>
  .wb-cards {
    display: grid;
    grid-template-columns: repeat(var(--wb-cards-count, 7), minmax(0, 1fr));
    gap: 10px;
  }

  .wb-card {
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
      border-color 0.2s ease,
      box-shadow 0.2s ease,
      background 0.2s ease;

    /* 默认色（防漏类） */
    --wb-accent: var(--el-color-primary);
    --wb-soft-bg: var(--el-color-primary-light-9);
    --wb-soft-ring: var(--el-color-primary-light-7);

    /* 7 阶段配色：琥珀 / 蓝 / 橙 / 紫 / 青 / 绿 / 灰 */
    &--pending-confirm {
      --wb-accent: var(--el-color-warning);
      --wb-soft-bg: var(--el-color-warning-light-9);
      --wb-soft-ring: var(--el-color-warning-light-7);
    }
    &--pending-dispatch {
      --wb-accent: var(--el-color-primary);
      --wb-soft-bg: var(--el-color-primary-light-9);
      --wb-soft-ring: var(--el-color-primary-light-7);
    }
    &--scheduling {
      --wb-accent: #ea6a1f;
      --wb-soft-bg: rgba(234, 106, 31, 0.11);
      --wb-soft-ring: rgba(234, 106, 31, 0.35);
    }
    &--in-transit {
      --wb-accent: #9333ea;
      --wb-soft-bg: rgba(147, 51, 234, 0.1);
      --wb-soft-ring: rgba(147, 51, 234, 0.32);
    }
    &--delivered {
      --wb-accent: #0ea5e9;
      --wb-soft-bg: rgba(14, 165, 233, 0.1);
      --wb-soft-ring: rgba(14, 165, 233, 0.32);
    }
    &--completed {
      --wb-accent: var(--el-color-success);
      --wb-soft-bg: var(--el-color-success-light-9);
      --wb-soft-ring: var(--el-color-success-light-7);
    }
    &--closed {
      --wb-accent: var(--el-color-info);
      --wb-soft-bg: var(--el-color-info-light-9);
      --wb-soft-ring: var(--el-color-info-light-7);
    }

    &.is-selected {
      background: var(--wb-soft-bg);
      border-color: var(--wb-accent);
      box-shadow: 0 0 0 1px var(--wb-soft-ring);
    }

    &:hover {
      border-color: var(--wb-accent);
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
      background: var(--wb-accent);
      box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.35),
        inset 0 -1px 2px rgba(0, 0, 0, 0.12);
    }

    &__title {
      font-size: 13px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      letter-spacing: 0.02em;
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
