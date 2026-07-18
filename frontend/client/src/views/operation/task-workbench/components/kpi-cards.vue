<!--
  调度工作台 KPI：五阶段卡片（待分配 / 待派车 / 待装车 / 在途中 / 待签收）

  - 置于页面背景之上（由 index.vue 外层挂载），与下方筛选/列表白卡片区隔
  - 主区点击 = 本阶段全部任务
  - 标题同行右侧「常 / 警」药丸 = 正常 / 预警快速筛选
  - 栅格固定 5 列、永远单行（对齐计划工作台卡片布局）

  阶段「待结算」已下线：财务结算与 task.status 解耦，结算单走财务工作台。
  详见《02.计划与任务单状态机联动设计.md》。
-->
<template>
  <div class="kpi-cards" :style="{ '--kpi-cards-count': cards.length }">
    <div
      v-for="card in cards"
      :key="card.key"
      class="kpi-card"
      :class="[
        `kpi-card--${card.key}`,
        { 'is-selected': isStageSelected(card.key) }
      ]"
    >
      <div class="kpi-card__body">
        <div class="kpi-card__head">
          <span class="kpi-card__accent-bar" aria-hidden="true"></span>
          <span class="kpi-card__title">{{ card.label }}</span>
          <div class="kpi-card__pills" @click.stop>
            <el-tooltip
              content="未触发计划类「预警」规则的任务（本阶段内）"
              placement="top"
              :show-after="350"
            >
              <button
                type="button"
                class="kpi-pill kpi-pill--normal"
                :class="{ 'is-active': isPillActive(card.key, 'normal') }"
                @click="emitSelect(card, 'normal')"
              >
                <span class="kpi-pill__letter">常</span>
                <span class="kpi-pill__num">{{ card.normal }}</span>
              </button>
            </el-tooltip>
            <el-tooltip
              :content="card.alertHint"
              placement="top"
              :show-after="350"
            >
              <button
                type="button"
                class="kpi-pill kpi-pill--alert"
                :class="{ 'is-active': isPillActive(card.key, 'alert') }"
                @click="emitSelect(card, 'alert')"
              >
                <span class="kpi-pill__letter">警</span>
                <span class="kpi-pill__num">{{ card.alert }}</span>
              </button>
            </el-tooltip>
          </div>
        </div>
        <button
          type="button"
          class="kpi-card__main"
          :class="{ 'is-active': isMainAllActive(card.key) }"
          @click="emitSelect(card, 'all')"
        >
          <div class="kpi-card__metric">
            <span class="kpi-card__value">{{ card.total }}</span>
            <span class="kpi-card__unit">单</span>
          </div>
          <div class="kpi-card__sub">{{ card.sub }}</div>
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { TaskWorkbenchStats } from '@/api/operation/task/model';

  type WorkbenchListSubset = 'all' | 'normal' | 'alert';

  const props = defineProps<{
    stats: TaskWorkbenchStats | null;
    loading?: boolean;
    /** 形如 pending-assign 或 pending-assign:alert */
    activeCardKey?: string;
  }>();

  const emit = defineEmits<{
    (
      e: 'selectCard',
      payload: {
        cardKey: string;
        status: number | number[];
        subset: WorkbenchListSubset;
      }
    ): void;
  }>();

  interface KpiCard {
    key: string;
    label: string;
    status: number | number[];
    total: number;
    normal: number;
    alert: number;
    alertHint: string;
    sub: string;
  }

  const activeKey = computed(() => props.activeCardKey ?? '');

  const cards = computed<KpiCard[]>(() => {
    const t = props.stats?.totals;
    const a = props.stats?.alerts;
    const pa = t?.pendingAssign ?? 0;
    const aa = a?.overdueAssignment ?? 0;
    const pd = t?.pendingDispatch ?? 0;
    const ad = a?.overdueDispatch ?? 0;
    const onWay = (t?.loading ?? 0) + (t?.onWay ?? 0);
    const aTransit = a?.overdueArrive ?? 0;
    const pl = t?.pendingLoad ?? 0;
    const al = a?.pendingLoadAlert ?? 0;
    const ps = t?.pendingSign ?? 0;
    const as = a?.pendingSignAlert ?? 0;

    const mk = (
      key: string,
      label: string,
      status: number | number[],
      total: number,
      alert: number,
      alertHint: string,
      sub: string
    ): KpiCard => ({
      key,
      label,
      status,
      total,
      alert,
      normal: Math.max(0, total - alert),
      alertHint,
      sub
    });

    return [
      mk(
        'pending-assign',
        '待分配',
        -1,
        pa,
        aa,
        '当前：计划装车时间已过，任务仍处于待分配。后续可扩展更多预警规则。',
        '本阶段任务合计'
      ),
      mk(
        'pending-dispatch',
        '待派车',
        0,
        pd,
        ad,
        '当前：计划装车时间已过仍未派车。后续可扩展更多预警规则。',
        '本阶段任务合计'
      ),
      mk(
        'pending-load',
        '待装车',
        1,
        pl,
        al,
        '待装车环节预警规则开发中；接入后将在此汇总需关注的任务。',
        '本阶段任务合计'
      ),
      mk(
        'on-way',
        '在途中',
        [2, 3],
        onWay,
        aTransit,
        '当前：计划到货时间已过，任务仍处于在途/已装车。后续可扩展更多预警规则。',
        '本阶段任务合计'
      ),
      mk(
        'pending-sign',
        '待签收',
        4,
        ps,
        as,
        '已到达目的地、等待逐计划签收。签收完成后任务自动进入「已签收」。',
        '已到达待签收'
      )
    ];
  });

  const isStageSelected = (key: string) => {
    const k = activeKey.value;
    return k === key || k.startsWith(`${key}:`);
  };

  const isPillActive = (key: string, subset: 'normal' | 'alert') =>
    activeKey.value === `${key}:${subset}`;

  const isMainAllActive = (key: string) => activeKey.value === key;

  const emitSelect = (card: KpiCard, subset: WorkbenchListSubset) => {
    emit('selectCard', {
      cardKey: card.key,
      status: card.status,
      subset
    });
  };
</script>

<style lang="scss" scoped>
  .kpi-cards {
    display: grid;
    grid-template-columns: repeat(var(--kpi-cards-count, 5), minmax(0, 1fr));
    gap: 10px;
  }

  .kpi-card {
    position: relative;
    border-radius: 12px;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-bg-color);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    overflow: hidden;
    transition:
      border-color 0.2s ease,
      box-shadow 0.2s ease,
      background 0.2s ease;

    /* 默认（防漏类名） */
    --kpi-accent: var(--el-color-primary);
    --kpi-soft-bg: var(--el-color-primary-light-9);
    --kpi-soft-ring: var(--el-color-primary-light-7);

    /* 五阶段配色：琥珀 / 蓝 / 靛 / 橙 / 绿 */
    &--pending-assign {
      --kpi-accent: var(--el-color-warning);
      --kpi-soft-bg: var(--el-color-warning-light-9);
      --kpi-soft-ring: var(--el-color-warning-light-7);
    }
    &--pending-dispatch {
      --kpi-accent: var(--el-color-primary);
      --kpi-soft-bg: var(--el-color-primary-light-9);
      --kpi-soft-ring: var(--el-color-primary-light-7);
    }
    &--pending-load {
      --kpi-accent: #5b62e6;
      --kpi-soft-bg: rgba(91, 98, 230, 0.1);
      --kpi-soft-ring: rgba(91, 98, 230, 0.32);
    }
    &--on-way {
      --kpi-accent: #ea6a1f;
      --kpi-soft-bg: rgba(234, 106, 31, 0.11);
      --kpi-soft-ring: rgba(234, 106, 31, 0.35);
    }
    &--pending-sign {
      --kpi-accent: var(--el-color-success);
      --kpi-soft-bg: var(--el-color-success-light-9);
      --kpi-soft-ring: var(--el-color-success-light-7);
    }

    &.is-selected {
      background: var(--kpi-soft-bg);
      border-color: var(--kpi-accent);
      box-shadow: 0 0 0 1px var(--kpi-soft-ring);
    }

    &__body {
      display: flex;
      flex-direction: column;
      padding: 12px 12px 12px;
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
      background: var(--kpi-accent);
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

    &__pills {
      display: inline-flex;
      align-items: center;
      gap: 6px;
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

      &:hover,
      &.is-active {
        background: transparent;
        box-shadow: none;
      }
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

    .kpi-pill--normal .kpi-pill__letter {
      color: var(--kpi-accent);
    }

    .kpi-pill--normal.is-active {
      border-color: var(--kpi-accent);
      box-shadow: 0 0 0 2px var(--kpi-soft-bg);
    }
  }

  .kpi-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px;
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

    &--alert .kpi-pill__letter {
      color: var(--el-color-danger);
    }

    &--alert.is-active {
      border-color: var(--el-color-danger-light-5);
      box-shadow: 0 0 0 2px var(--el-color-danger-light-8);
    }
  }
</style>
