<!--
  调度工作台 KPI 卡片区

  6 个状态计数卡片 + 2 个异常告警卡片，
  点击可触发 emit('selectCard') 切换下方列表筛选状态。
-->
<template>
  <div class="kpi-cards">
    <div
      v-for="card in cards"
      :key="card.key"
      class="kpi-card"
      :class="[
        `kpi-card--${card.type}`,
        { 'is-alert': card.isAlert, 'is-selected': card.key === activeCardKey }
      ]"
      @click="onClick(card)"
    >
      <div class="kpi-card__label-wrap">
        <el-tooltip
          v-if="card.hint"
          :content="card.hint"
          placement="top"
          :show-after="400"
        >
          <span class="kpi-card__label kpi-card__label--has-tip">{{
            card.label
          }}</span>
        </el-tooltip>
        <span v-else class="kpi-card__label">{{ card.label }}</span>
      </div>
      <div class="kpi-card__value">
        <span class="kpi-card__count">{{ card.value }}</span>
        <span class="kpi-card__suffix">单</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { TaskWorkbenchStats } from '@/api/operation/task/model';

  const props = defineProps<{
    stats: TaskWorkbenchStats | null;
    loading?: boolean;
    /** 当前选中的卡片 key，与父组件状态同步 */
    activeCardKey?: string;
  }>();

  const emit = defineEmits<{
    (
      e: 'selectCard',
      payload: { cardKey: string; status: number | number[] }
    ): void;
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

  const activeCardKey = computed(() => props.activeCardKey ?? '');

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
        hint: '计划到货时间已过仍未到达',
        isAlert: true
      }
    ];
  });

  const onClick = (card: Card) => {
    if (card.status !== undefined) {
      emit('selectCard', { cardKey: card.key, status: card.status });
    }
  };
</script>

<style lang="scss" scoped>
  .kpi-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 10px;
    margin-bottom: 12px;
  }
  .kpi-card {
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-light);
    border-radius: 6px;
    padding: 8px 12px 10px;
    cursor: pointer;
    transition:
      border-color 0.2s,
      box-shadow 0.2s;
    position: relative;

    &:hover {
      border-color: var(--el-color-primary-light-5);
      box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
    }

    &.is-selected {
      border-color: var(--el-color-primary);
      box-shadow:
        0 0 0 1px var(--el-color-primary-light-7),
        0 2px 8px rgba(0, 0, 0, 0.06);
    }

    &__label-wrap {
      min-height: 18px;
    }
    &__label {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      line-height: 1.35;
      &--has-tip {
        border-bottom: 1px dashed var(--el-border-color);
        cursor: help;
      }
    }
    &__value {
      display: flex;
      align-items: baseline;
      gap: 4px;
      margin-top: 4px;
    }
    &__count {
      font-size: 22px;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
      line-height: 1;
    }
    &__suffix {
      font-size: 12px;
      color: var(--el-text-color-secondary);
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

    &.is-alert.is-selected {
      border-color: var(--el-color-primary);
      box-shadow:
        0 0 0 1px var(--el-color-primary-light-7),
        0 2px 8px rgba(0, 0, 0, 0.06);
    }
  }
</style>
