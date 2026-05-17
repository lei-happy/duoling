<!--
  费用工作台 KPI 卡片区

  显示待审批 / 待支付 / 今日已支付 等关键指标，
  点击切到对应状态 Tab。
-->
<template>
  <div class="kpi-cards">
    <div
      v-for="card in cards"
      :key="card.key"
      class="kpi-card"
      :class="[`kpi-card--${card.type}`]"
      @click="onClick(card)"
    >
      <div class="kpi-card__label">{{ card.label }}</div>
      <div class="kpi-card__value">
        <span class="kpi-card__count">{{ card.value }}</span>
        <span class="kpi-card__suffix">{{ card.unit }}</span>
      </div>
      <div v-if="card.hint" class="kpi-card__hint">{{ card.hint }}</div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { TaskFinanceWorkbenchStats } from '@/api/operation/task-finance/model';

  const props = defineProps<{
    stats: TaskFinanceWorkbenchStats | null;
    loading?: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'selectStatus', status: number): void;
  }>();

  interface Card {
    key: string;
    label: string;
    value: string | number;
    unit: string;
    type: 'info' | 'primary' | 'warning' | 'success' | 'danger';
    status?: number;
    hint?: string;
  }

  const fmt = (v?: number) =>
    Number(v || 0).toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });

  const cards = computed<Card[]>(() => {
    const t = props.stats?.totals;
    const a = props.stats?.amounts;
    return [
      {
        key: 'draft',
        label: '草稿',
        value: t?.draft ?? 0,
        unit: '张',
        type: 'info',
        status: 0
      },
      {
        key: 'pending-review',
        label: '待审批',
        value: t?.pendingReview ?? 0,
        unit: '张',
        type: 'warning',
        status: 1,
        hint: `计划合计 ¥ ${fmt(a?.pendingReviewAmount)}`
      },
      {
        key: 'pending-pay',
        label: '待支付',
        value: t?.pendingPay ?? 0,
        unit: '张',
        type: 'primary',
        status: 2,
        hint: `计划合计 ¥ ${fmt(a?.pendingPayAmount)}`
      },
      {
        key: 'today-paid',
        label: '今日已支付',
        value: `¥ ${fmt(a?.todayPaidAmount)}`,
        unit: '',
        type: 'success',
        status: 3,
        hint: `累计已支付 ${t?.paid ?? 0} 张`
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
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
  }
</style>
