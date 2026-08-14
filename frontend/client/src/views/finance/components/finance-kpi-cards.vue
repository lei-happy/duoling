<!--
  财务模块通用 KPI 卡片区

  与既有「费用工作台」的卡片交互一致：卡片可点击，点击即把下方列表筛到该口径。
  卡片内容由调用方给出，本组件只负责排版与配色，避免每个工作台各写一套样式。
-->
<template>
  <div class="fin-kpi-cards">
    <div
      v-for="card in cards"
      :key="card.key"
      class="fin-kpi-card"
      :class="[
        `is-${card.type || 'info'}`,
        { 'is-clickable': !!card.clickable }
      ]"
      @click="onClick(card)"
    >
      <div class="fin-kpi-card__label">{{ card.label }}</div>
      <div class="fin-kpi-card__value">
        <span class="fin-kpi-card__count">{{ card.value }}</span>
        <span v-if="card.unit" class="fin-kpi-card__unit">{{ card.unit }}</span>
      </div>
      <div v-if="card.hint" class="fin-kpi-card__hint">{{ card.hint }}</div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  export interface FinanceKpiCard {
    key: string;
    label: string;
    value: string | number;
    unit?: string;
    type?: 'info' | 'primary' | 'warning' | 'success' | 'danger';
    hint?: string;
    /** 可点击时才响应点击并加悬浮态 */
    clickable?: boolean;
  }

  defineProps<{ cards: FinanceKpiCard[] }>();

  const emit = defineEmits<{ (e: 'select', key: string): void }>();

  const onClick = (card: FinanceKpiCard) => {
    if (card.clickable) emit('select', card.key);
  };
</script>

<style lang="scss" scoped>
  .fin-kpi-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 12px;
    margin-bottom: 12px;
  }

  .fin-kpi-card {
    padding: 14px 16px;
    border: 1px solid var(--el-border-color-light);
    border-radius: 6px;
    background: var(--el-bg-color);
    transition: all 0.2s;

    &.is-clickable {
      cursor: pointer;

      &:hover {
        border-color: var(--el-color-primary);
        box-shadow: 0 2px 8px rgb(0 0 0 / 6%);
      }
    }

    &__label {
      margin-bottom: 6px;
      color: var(--el-text-color-secondary);
      font-size: 13px;
    }

    &__value {
      display: flex;
      align-items: baseline;
      gap: 4px;
    }

    &__count {
      font-size: 24px;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
      line-height: 1;
    }

    &__unit {
      color: var(--el-text-color-secondary);
      font-size: 12px;
    }

    &__hint {
      margin-top: 6px;
      color: var(--el-text-color-placeholder);
      font-size: 12px;
    }

    &.is-info .fin-kpi-card__count {
      color: var(--el-text-color-primary);
    }

    &.is-primary .fin-kpi-card__count {
      color: var(--el-color-primary);
    }

    &.is-warning .fin-kpi-card__count {
      color: var(--el-color-warning);
    }

    &.is-success .fin-kpi-card__count {
      color: var(--el-color-success);
    }

    &.is-danger .fin-kpi-card__count {
      color: var(--el-color-danger);
    }
  }
</style>
