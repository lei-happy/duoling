<!--
  调度工作台 KPI 卡片区

  6 个状态计数卡片 + 2 个异常告警卡片，
  点击可触发 emit('selectStatus') 切换主区域 Tab。
-->
<template>
  <div class="kpi-cards">
    <div
      v-for="card in cards"
      :key="card.key"
      class="kpi-card"
      :class="[`kpi-card--${card.type}`, { 'is-alert': card.isAlert }]"
      @click="onClick(card)"
    >
      <div class="kpi-card__label">{{ card.label }}</div>
      <div class="kpi-card__value">
        <span class="kpi-card__count">{{ card.value }}</span>
        <span class="kpi-card__suffix">单</span>
      </div>
      <div v-if="card.hint" class="kpi-card__hint">{{ card.hint }}</div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { TaskWorkbenchStats } from '@/api/operation/task/model';

  const props = defineProps<{
    stats: TaskWorkbenchStats | null;
    loading?: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'selectStatus', status: number | number[]): void;
  }>();

  interface Card {
    key: string;
    label: string;
    value: number;
    type: 'info' | 'primary' | 'warning' | 'success' | 'danger';
    status?: number | number[];
    hint?: string;
    isAlert?: boolean;
  }

  const cards = computed<Card[]>(() => {
    const t = props.stats?.totals;
    const a = props.stats?.alerts;
    return [
      {
        key: 'pending-dispatch',
        label: '待派车',
        value: t?.pendingDispatch ?? 0,
        type: 'info',
        status: 0
      },
      {
        key: 'pending-load',
        label: '待装车',
        value: t?.pendingLoad ?? 0,
        type: 'primary',
        status: 1
      },
      {
        key: 'on-way',
        label: '在途中',
        value: (t?.loading ?? 0) + (t?.onWay ?? 0),
        type: 'warning',
        status: [2, 3]
      },
      {
        key: 'pending-sign',
        label: '待签收',
        value: t?.pendingSign ?? 0,
        type: 'success',
        status: 4
      },
      {
        key: 'pending-settle',
        label: '待结算',
        value: t?.pendingSettle ?? 0,
        type: 'success',
        status: 5
      },
      {
        key: 'overdue-dispatch',
        label: '逾期未派车',
        value: a?.overdueDispatch ?? 0,
        type: 'danger',
        status: 0,
        hint: '计划装车时间已过仍未派车',
        isAlert: true
      },
      {
        key: 'overdue-arrive',
        label: '在途逾期',
        value: a?.overdueArrive ?? 0,
        type: 'danger',
        status: [2, 3],
        hint: '计划到达时间已过仍未到达',
        isAlert: true
      }
    ];
  });

  const onClick = (card: Card) => {
    if (card.status !== undefined) emit('selectStatus', card.status);
  };
</script>

<style lang="scss" scoped>
  .kpi-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 12px;
  }
  .kpi-card {
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-light);
    border-radius: 6px;
    padding: 14px 16px;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;

    &:hover {
      border-color: var(--el-color-primary);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }

    &__label {
      font-size: 13px;
      color: var(--el-text-color-secondary);
      margin-bottom: 6px;
    }
    &__value {
      display: flex;
      align-items: baseline;
      gap: 4px;
    }
    &__count {
      font-size: 26px;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
      line-height: 1;
    }
    &__suffix {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
    &__hint {
      font-size: 12px;
      color: var(--el-text-color-placeholder);
      margin-top: 6px;
    }

    &--info .kpi-card__count {
      color: var(--el-text-color-primary);
    }
    &--primary .kpi-card__count {
      color: var(--el-color-primary);
    }
    &--warning .kpi-card__count {
      color: var(--el-color-warning);
    }
    &--success .kpi-card__count {
      color: var(--el-color-success);
    }
    &--danger .kpi-card__count {
      color: var(--el-color-danger);
    }

    &.is-alert {
      background-color: var(--el-color-danger-light-9);
      border-color: var(--el-color-danger-light-7);
    }
  }
</style>
