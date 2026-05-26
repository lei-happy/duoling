<!--
  社会运力审批工作台 KPI 卡片
  待审核 | 已通过 | 已驳回 | 全部
-->
<template>
  <div class="approval-cards">
    <button
      v-for="card in cards"
      :key="card.key"
      type="button"
      class="approval-card"
      :class="[
        `approval-card--${card.key}`,
        { 'is-selected': activeKey === card.key }
      ]"
      @click="emit('select', card.key)"
    >
      <div class="approval-card__head">
        <span class="approval-card__accent-bar" aria-hidden="true"></span>
        <span class="approval-card__title">{{ card.label }}</span>
      </div>
      <div class="approval-card__metric">
        <span class="approval-card__value">{{ card.total }}</span>
        <span class="approval-card__unit">条</span>
      </div>
      <div class="approval-card__sub">{{ card.sub }}</div>
    </button>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { SocialCapacityApprovalStats } from '@/api/capacity/social-capacity/approval/model';

  export type ApprovalCardKey = '1' | '2' | '3' | 'all';

  const props = defineProps<{
    stats: SocialCapacityApprovalStats | null;
    activeKey?: ApprovalCardKey;
  }>();

  const emit = defineEmits<{
    (e: 'select', key: ApprovalCardKey): void;
  }>();

  const cards = computed(() => {
    const s = props.stats;
    return [
      {
        key: '1' as const,
        label: '待审核',
        total: s?.pendingCount ?? 0,
        sub: '等待审批处理'
      },
      {
        key: '2' as const,
        label: '已通过',
        total: s?.approvedCount ?? 0,
        sub: '审核已通过'
      },
      {
        key: '3' as const,
        label: '已驳回',
        total: s?.rejectedCount ?? 0,
        sub: '需修改后重新提交'
      },
      {
        key: 'all' as const,
        label: '全部',
        total: s?.totalCount ?? 0,
        sub: '全部审批记录'
      }
    ];
  });
</script>

<style lang="scss" scoped>
  .approval-cards {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 12px;
  }

  .approval-card {
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

    --approval-accent: var(--el-color-primary);
    --approval-soft-bg: var(--el-color-primary-light-9);
    --approval-soft-ring: var(--el-color-primary-light-7);

    &--1 {
      --approval-accent: var(--el-color-primary);
      --approval-soft-bg: var(--el-color-primary-light-9);
      --approval-soft-ring: var(--el-color-primary-light-7);
    }
    &--2 {
      --approval-accent: var(--el-color-success);
      --approval-soft-bg: var(--el-color-success-light-9);
      --approval-soft-ring: var(--el-color-success-light-7);
    }
    &--3 {
      --approval-accent: var(--el-color-danger);
      --approval-soft-bg: var(--el-color-danger-light-9);
      --approval-soft-ring: var(--el-color-danger-light-7);
    }
    &--all {
      --approval-accent: var(--el-color-info);
      --approval-soft-bg: var(--el-color-info-light-9);
      --approval-soft-ring: var(--el-color-info-light-7);
    }

    &.is-selected {
      background: var(--approval-soft-bg);
      border-color: var(--approval-accent);
      box-shadow: 0 0 0 1px var(--approval-soft-ring);
    }

    &:hover {
      border-color: var(--approval-accent);
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
      background: var(--approval-accent);
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
