<!--
  调度工作台 KPI：六阶段卡片（待分配 / 待派车 / 待装车 / 待发车 / 在途 / 待交车）

  - 置于页面背景之上（由 index.vue 外层挂载），与下方筛选/列表白卡片区隔
  - 主区点击 = 本阶段全部任务
  - 标题同行右侧「常 / 关注 / 严重」三个药丸 = 按预警级别快速筛选
  - 三个数字互斥且相加等于本阶段总数：一个任务同时命中多条规则时按最高级别归类
  - 计数全部来自后端 biz_task_alert，与列表 alertLevel 过滤同源，点进去条数必然一致
  - 每个卡片对应单一 task.status，与 workbench-pool-registry 的池一一对应

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
              :content="`${card.label}中没有任何预警的任务，节奏正常，暂时不用管`"
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
            <el-tooltip :content="card.warnHint" placement="top" :show-after="350">
              <button
                type="button"
                class="kpi-pill kpi-pill--warn"
                :class="{
                  'is-active': isPillActive(card.key, 'warn'),
                  'is-zero': card.warn === 0
                }"
                @click="emitSelect(card, 'warn')"
              >
                <span class="kpi-pill__letter">注</span>
                <span class="kpi-pill__num">{{ card.warn }}</span>
              </button>
            </el-tooltip>
            <el-tooltip
              :content="card.criticalHint"
              placement="top"
              :show-after="350"
            >
              <button
                type="button"
                class="kpi-pill kpi-pill--critical"
                :class="{
                  'is-active': isPillActive(card.key, 'critical'),
                  'is-zero': card.critical === 0
                }"
                @click="emitSelect(card, 'critical')"
              >
                <span class="kpi-pill__letter">急</span>
                <span class="kpi-pill__num">{{ card.critical }}</span>
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

  type WorkbenchListSubset = 'all' | 'normal' | 'warn' | 'critical';

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
        status: number;
        subset: WorkbenchListSubset;
      }
    ): void;
  }>();

  interface KpiCard {
    key: string;
    label: string;
    status: number;
    total: number;
    normal: number;
    warn: number;
    critical: number;
    warnHint: string;
    criticalHint: string;
    sub: string;
  }

  const activeKey = computed(() => props.activeCardKey ?? '');

  const cards = computed<KpiCard[]>(() => {
    const t = props.stats?.totals;
    const stageAlerts = props.stats?.stageAlerts ?? {};

    const levels = (status: number) =>
      stageAlerts[String(status)] ?? { warn: 0, critical: 0 };

    /**
     * `sub` 是标题下方那行小字。原先几乎都写「本阶段任务合计」——数字本身已经说明
     * 是合计，这行等于没信息。改成说清**这批单子卡在等什么**，一眼判断该找谁推进。
     */
    const mk = (
      key: string,
      label: string,
      status: number,
      total: number,
      warnHint: string,
      criticalHint: string,
      sub: string
    ): KpiCard => {
      const { warn, critical } = levels(status);
      return {
        key,
        label,
        status,
        total,
        warn,
        critical,
        // 三个数字必须相加等于总数，否则调度员一眼就会发现对不上
        normal: Math.max(0, total - warn - critical),
        warnHint,
        criticalHint,
        sub
      };
    };

    return [
      mk(
        'pending-assign',
        '待分配',
        -1,
        t?.pendingAssign ?? 0,
        '快到装车时间了还没定承运方，建议尽快安排',
        '已经超过装车时间还没定承运方，需要马上处理',
        '待指定承运方'
      ),
      mk(
        'pending-dispatch',
        '待派车',
        0,
        t?.pendingDispatch ?? 0,
        '快到装车时间了还没派车，建议尽快安排',
        '已经超过装车时间还没派车，需要马上处理',
        '待安排车辆司机'
      ),
      mk(
        'pending-load',
        '待装车',
        1,
        t?.pendingLoad ?? 0,
        '快到装车时间了还没装车，建议联系承运方',
        '已经超过装车时间还没装车，需要马上催办',
        '等承运方装车'
      ),
      mk(
        'pending-depart',
        '待发车',
        2,
        t?.loading ?? 0,
        '装完车压在场内有点久了，建议催促发车',
        '装完车长时间没发车，需要马上催办',
        '装车完毕待发车'
      ),
      mk(
        'on-way',
        '在途',
        3,
        t?.onWay ?? 0,
        '快到承诺到货时间了还没到，建议提前跟客户沟通',
        '已经超过承诺到货时间还没到，需要马上跟进',
        '运输中待到达'
      ),
      mk(
        'pending-deliver',
        '待交车',
        4,
        t?.pendingSign ?? 0,
        '到场后交接进度偏慢，建议跟进验车',
        '到场后长时间没完成交接，需要马上跟进',
        '待逐台验车交接'
      )
    ];
  });

  const isStageSelected = (key: string) => {
    const k = activeKey.value;
    return k === key || k.startsWith(`${key}:`);
  };

  const isPillActive = (key: string, subset: 'normal' | 'warn' | 'critical') =>
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
    grid-template-columns: repeat(var(--kpi-cards-count, 6), minmax(0, 1fr));
    gap: 10px;
  }

  /* 阶段增加到 6 个后，窄屏单行会挤压数字，折成两行更易读 */
  @media (max-width: 1400px) {
    .kpi-cards {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
  }

  @media (max-width: 768px) {
    .kpi-cards {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
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

    /* 六阶段配色：琥珀 / 蓝 / 靛 / 青 / 橙 / 绿 */
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
    &--pending-depart {
      --kpi-accent: #0f9e8e;
      --kpi-soft-bg: rgba(15, 158, 142, 0.1);
      --kpi-soft-ring: rgba(15, 158, 142, 0.32);
    }
    &--on-way {
      --kpi-accent: #ea6a1f;
      --kpi-soft-bg: rgba(234, 106, 31, 0.11);
      --kpi-soft-ring: rgba(234, 106, 31, 0.35);
    }
    &--pending-deliver {
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
      /* 三个药丸后横向空间变紧，间距与内边距同步收窄 */
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
      /* 各阶段说明字数不等，禁止换行以保证六张卡等高 */
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
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

    &--warn .kpi-pill__letter {
      color: var(--el-color-warning);
    }

    &--warn.is-active {
      border-color: var(--el-color-warning-light-5);
      box-shadow: 0 0 0 2px var(--el-color-warning-light-8);
    }

    &--critical .kpi-pill__letter {
      color: var(--el-color-danger);
    }

    &--critical.is-active {
      border-color: var(--el-color-danger-light-5);
      box-shadow: 0 0 0 2px var(--el-color-danger-light-8);
    }

    /* 没有预警时压低存在感，让真正有数字的药丸先被看见 */
    &.is-zero {
      opacity: 0.45;

      .kpi-pill__letter {
        color: var(--el-text-color-placeholder);
      }
    }
  }
</style>
