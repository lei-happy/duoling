<!--
  社会运力列表 KPI：6 卡
  启用：正常 | 未生效 | 停用 | 黑名单
  审核：待处理 | 已通过
-->
<template>
  <div class="sc-cards">
    <button
      v-for="card in statusCards"
      :key="card.key"
      type="button"
      class="sc-card"
      :class="[
        `sc-card--${card.key}`,
        { 'is-selected': activeStatusKey === card.key }
      ]"
      @click="emit('selectStatus', card.key)"
    >
      <div class="sc-card__head">
        <span class="sc-card__accent-bar" aria-hidden="true"></span>
        <span class="sc-card__title">{{ card.label }}</span>
      </div>
      <div class="sc-card__metric">
        <span class="sc-card__value">{{ card.total }}</span>
        <span class="sc-card__unit">条</span>
      </div>
    </button>

    <div
      class="sc-card sc-card--pending_process"
      :class="{ 'is-selected': isPendingGroupSelected }"
    >
      <div class="sc-card__body">
        <div class="sc-card__head">
          <span class="sc-card__accent-bar" aria-hidden="true"></span>
          <span class="sc-card__title">待处理</span>
          <div class="sc-card__pills" @click.stop>
            <el-tooltip
              v-for="pill in pendingPills"
              :key="pill.key"
              :content="pill.tip"
              placement="top"
              :show-after="300"
            >
              <button
                type="button"
                class="sc-pill"
                :class="[
                  `sc-pill--${pill.key}`,
                  { 'is-active': activeApprovalKey === pill.key }
                ]"
                @click="emit('selectApproval', pill.key)"
              >
                <span class="sc-pill__letter">{{ pill.letter }}</span>
                <span class="sc-pill__num">{{ pill.total }}</span>
              </button>
            </el-tooltip>
          </div>
        </div>
        <button
          type="button"
          class="sc-card__main"
          :class="{ 'is-active': activeApprovalKey === 'pending_process' }"
          @click="emit('selectApproval', 'pending_process')"
        >
          <div class="sc-card__metric">
            <span class="sc-card__value">{{ pendingProcessTotal }}</span>
            <span class="sc-card__unit">条</span>
          </div>
        </button>
      </div>
    </div>

    <button
      type="button"
      class="sc-card sc-card--approved"
      :class="{ 'is-selected': activeApprovalKey === 'approved' }"
      @click="emit('selectApproval', 'approved')"
    >
      <div class="sc-card__head">
        <span class="sc-card__accent-bar" aria-hidden="true"></span>
        <span class="sc-card__title">已通过</span>
      </div>
      <div class="sc-card__metric">
        <span class="sc-card__value">{{ approvalTotals?.approved ?? 0 }}</span>
        <span class="sc-card__unit">条</span>
      </div>
    </button>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { SocialCapacityListStats } from '@/api/capacity/social-capacity/list/model';

  export type ApprovalCardKey =
    | 'pending_process'
    | 'approved'
    | 'draft'
    | 'pending'
    | 'rejected';
  export type StatusCardKey = 'active' | 'inactive' | 'disabled' | 'blacklist';

  const props = defineProps<{
    stats: SocialCapacityListStats | null;
    activeApprovalKey?: ApprovalCardKey | null;
    activeStatusKey?: StatusCardKey | null;
  }>();

  const emit = defineEmits<{
    (e: 'selectApproval', key: ApprovalCardKey): void;
    (e: 'selectStatus', key: StatusCardKey): void;
  }>();

  interface PendingPill {
    key: Extract<ApprovalCardKey, 'draft' | 'pending' | 'rejected'>;
    letter: string;
    tip: string;
    total: number;
  }

  const approvalTotals = computed(() => props.stats?.approvalTotals);

  const pendingPills = computed<PendingPill[]>(() => {
    const t = approvalTotals.value;
    return [
      { key: 'draft', letter: '草', tip: '草稿', total: t?.draft ?? 0 },
      { key: 'pending', letter: '审', tip: '待审核', total: t?.pending ?? 0 },
      { key: 'rejected', letter: '驳', tip: '已驳回', total: t?.rejected ?? 0 }
    ];
  });

  const pendingProcessTotal = computed(() => {
    const t = approvalTotals.value;
    const draft = t?.draft ?? 0;
    const pending = t?.pending ?? 0;
    const rejected = t?.rejected ?? 0;
    return t?.pendingProcess ?? draft + pending + rejected;
  });

  const isPendingGroupSelected = computed(() => {
    const key = props.activeApprovalKey;
    return (
      key === 'pending_process' ||
      key === 'draft' ||
      key === 'pending' ||
      key === 'rejected'
    );
  });

  const statusCards = computed(() => {
    const t = props.stats?.statusTotals;
    return [
      { key: 'active' as const, label: '正常', total: t?.active ?? 0 },
      { key: 'inactive' as const, label: '未生效', total: t?.inactive ?? 0 },
      { key: 'disabled' as const, label: '停用', total: t?.disabled ?? 0 },
      { key: 'blacklist' as const, label: '黑名单', total: t?.blacklist ?? 0 }
    ];
  });
</script>

<style lang="scss" scoped>
  .sc-cards {
    display: grid;
    /* 正常/未生效/停用/黑名单 | 待处理(略宽以容纳 tag) | 已通过 */
    grid-template-columns: 1fr 1fr 1fr 1fr 1.55fr 1fr;
    gap: 10px;
  }

  .sc-card {
    --sc-accent: var(--el-color-primary);
    --sc-soft-bg: var(--el-color-primary-light-9);
    --sc-soft-ring: var(--el-color-primary-light-7);

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

    &--pending_process {
      --sc-accent: var(--el-color-warning);
      --sc-soft-bg: var(--el-color-warning-light-9);
      --sc-soft-ring: var(--el-color-warning-light-7);
      padding: 0;
      cursor: default;
    }
    &--approved {
      --sc-accent: var(--el-color-success);
      --sc-soft-bg: var(--el-color-success-light-9);
      --sc-soft-ring: var(--el-color-success-light-7);
    }
    &--inactive {
      --sc-accent: var(--el-color-info);
      --sc-soft-bg: var(--el-color-info-light-9);
      --sc-soft-ring: var(--el-color-info-light-7);
    }
    &--active {
      --sc-accent: var(--el-color-success);
      --sc-soft-bg: var(--el-color-success-light-9);
      --sc-soft-ring: var(--el-color-success-light-7);
    }
    &--disabled {
      --sc-accent: var(--el-color-warning);
      --sc-soft-bg: var(--el-color-warning-light-9);
      --sc-soft-ring: var(--el-color-warning-light-7);
    }
    &--blacklist {
      --sc-accent: var(--el-color-danger);
      --sc-soft-bg: var(--el-color-danger-light-9);
      --sc-soft-ring: var(--el-color-danger-light-7);
    }

    &--inactive,
    &--active,
    &--disabled,
    &--blacklist {
      padding: 10px 10px;

      .sc-card__head {
        gap: 6px;
        margin-bottom: 4px;
      }

      .sc-card__title {
        font-size: 12px;
      }

      .sc-card__value {
        font-size: 24px;
      }
    }

    &.is-selected {
      background: var(--sc-soft-bg);
      border-color: var(--sc-accent);
      box-shadow: 0 0 0 1px var(--sc-soft-ring);
    }

    &:not(.sc-card--pending_process):hover {
      border-color: var(--sc-accent);
    }

    &__body {
      display: flex;
      flex-direction: column;
      padding: 12px;
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
      background: var(--sc-accent);
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

    &__pills {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      margin-left: auto;
    }

    &__main {
      display: block;
      width: 100%;
      margin: 0;
      padding: 0;
      border: none;
      background: transparent;
      cursor: pointer;
      text-align: left;
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
  }

  .sc-pill {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    padding: 2px 6px;
    border-radius: 999px;
    border: 1px solid transparent;
    background: var(--el-fill-color);
    cursor: pointer;
    font-size: 11px;
    line-height: 1.4;
    transition:
      background 0.15s ease,
      box-shadow 0.15s ease,
      border-color 0.15s ease;

    &:hover {
      background: var(--el-fill-color-dark);
    }

    &__letter {
      font-weight: 700;
      font-size: 11px;
      min-width: 1em;
      text-align: center;
    }

    &__num {
      font-weight: 600;
      font-variant-numeric: tabular-nums;
      color: var(--el-text-color-primary);
    }

    &--draft .sc-pill__letter {
      color: var(--el-color-info);
    }
    &--draft.is-active {
      border-color: var(--el-color-info-light-5);
      box-shadow: 0 0 0 2px var(--el-color-info-light-8);
    }

    &--pending .sc-pill__letter {
      color: var(--el-color-primary);
    }
    &--pending.is-active {
      border-color: var(--el-color-primary-light-5);
      box-shadow: 0 0 0 2px var(--el-color-primary-light-8);
    }

    &--rejected .sc-pill__letter {
      color: var(--el-color-danger);
    }
    &--rejected.is-active {
      border-color: var(--el-color-danger-light-5);
      box-shadow: 0 0 0 2px var(--el-color-danger-light-8);
    }
  }
</style>
