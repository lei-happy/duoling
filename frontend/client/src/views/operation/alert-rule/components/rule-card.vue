<!--
  单条默认阈值卡片

  扫一眼：名字、阶段、升级轨道、开没开。
  动手改：色段上的数字、时间基准、启用开关。系统默认收成一句脚注，不再占一列。
-->
<template>
  <article
    class="rule-card"
    :class="{
      'is-disabled': !row.enabled,
      'is-dirty': row.dirty
    }"
  >
    <header class="rule-card__head">
      <div class="rule-card__identity">
        <div class="rule-card__title-row">
          <h3 class="rule-card__title">{{ displayName }}</h3>
          <span v-if="stageChip" class="rule-card__stage">{{ stageChip }}</span>
          <span v-if="!row.enabled" class="rule-card__off">已停用</span>
          <span v-if="row.dirty" class="rule-card__dirty">未保存</span>
        </div>
        <p class="rule-card__desc">{{ row.description }}</p>
      </div>
      <el-tooltip
        content="关掉后这种预警对全公司都不再提醒"
        placement="top"
        :show-after="300"
      >
        <el-switch
          v-model="row.enabled"
          :loading="row.saving"
          :disabled="row.saving"
          @change="emit('toggle')"
        />
      </el-tooltip>
    </header>

    <div v-if="row.enabled" class="rule-card__config">
      <div v-if="row.kind === 'execution'" class="rule-card__instant">
        <span class="rule-card__instant-dot" aria-hidden="true"></span>
        命中即提醒，没有时间阈值可调
      </div>

      <template v-else-if="row.supportsTimeBasis">
        <section
          class="rule-card__clock"
          :class="{ 'is-off': !row.planEnabled }"
        >
          <div class="rule-card__clock-head">
            <el-checkbox
              :model-value="row.planEnabled"
              @change="(v: boolean) => setClock('plan', v)"
            >
              内部计划时间
            </el-checkbox>
          </div>
          <threshold-track
            v-if="row.planEnabled"
            :kind="row.kind"
            v-model:warn-ahead-minutes="row.warnAheadMinutes"
            v-model:critical-after-minutes="row.criticalAfterMinutes"
            time-basis-label="内部计划时间"
            @change="emit('change')"
          />
          <p v-else class="rule-card__clock-off">已关掉，只看客户要求时间</p>
        </section>
        <section
          class="rule-card__clock"
          :class="{ 'is-off': !row.requiredEnabled }"
        >
          <div class="rule-card__clock-head">
            <el-checkbox
              :model-value="row.requiredEnabled"
              @change="(v: boolean) => setClock('required', v)"
            >
              客户要求时间
            </el-checkbox>
          </div>
          <threshold-track
            v-if="row.requiredEnabled"
            :kind="row.kind"
            v-model:warn-ahead-minutes="row.warnAheadRequiredMinutes"
            v-model:critical-after-minutes="row.criticalAfterRequiredMinutes"
            time-basis-label="客户要求时间"
            @change="emit('change')"
          />
          <p v-else class="rule-card__clock-off">已关掉，只看内部计划时间</p>
        </section>
        <p class="rule-card__basis-hint">
          两路都开时，谁先碰到阈值听谁的。任务没填的那路会自动跳过。
        </p>
      </template>

      <threshold-track
        v-else
        :kind="row.kind"
        v-model:warn-ahead-minutes="row.warnAheadMinutes"
        v-model:critical-after-minutes="row.criticalAfterMinutes"
        v-model:anchor-offset-minutes="row.anchorOffsetMinutes"
        v-model:stagnant-hours="row.stagnantHours"
        @change="emit('change')"
      />

      <footer class="rule-card__foot">
        <p v-if="!row.supportsTimeBasis" class="rule-card__kind-hint">
          {{ ALERT_KIND_HINT[row.kind] }}
        </p>
        <div class="rule-card__meta">
          <span class="rule-card__default">{{ defaultCaption }}</span>
          <button
            v-if="row.ruleId"
            type="button"
            class="rule-card__reset"
            v-permission="'operation:alert-rule:edit'"
            @click="emit('reset')"
          >
            恢复系统默认
          </button>
          <el-button
            v-if="row.dirty"
            type="primary"
            size="small"
            :loading="row.saving"
            v-permission="'operation:alert-rule:edit'"
            @click="emit('save')"
          >
            保存
          </el-button>
        </div>
      </footer>
    </div>
  </article>
</template>

<script lang="ts" setup>
  /* 父级传入的是列表项引用，就地改字段与原先表格一致 */
  /* eslint-disable vue/no-mutating-props */
  import { computed } from 'vue';
  import {
    ALERT_KIND_HINT,
    alertStageLabel,
    summarizeThreshold
  } from '../../task/alert-config';
  import type { TaskAlertRuleCatalogItem } from '@/api/operation/task-alert/model';
  import ThresholdTrack from './threshold-track.vue';

  export interface DefaultRuleRow {
    key: string;
    ruleCode: string;
    ruleName: string;
    kind: string;
    description: string;
    stage: number | null;
    supportsTimeBasis: boolean;
    ruleId?: number;
    enabled: boolean;
    timeBasis: number;
    planEnabled: boolean;
    requiredEnabled: boolean;
    anchorOffsetMinutes?: number;
    warnAheadMinutes?: number;
    criticalAfterMinutes?: number;
    warnAheadRequiredMinutes?: number;
    criticalAfterRequiredMinutes?: number;
    stagnantHours?: number;
    builtIn: TaskAlertRuleCatalogItem['defaults'];
    dirty: boolean;
    saving?: boolean;
  }

  const row = defineModel<DefaultRuleRow>('row', { required: true });

  const emit = defineEmits<{
    (e: 'change'): void;
    (e: 'toggle'): void;
    (e: 'reset'): void;
    (e: 'save'): void;
  }>();

  const displayName = computed(() => {
    if (row.value.kind === 'stagnant' && row.value.stage != null) {
      return `${alertStageLabel(row.value.stage)}滞留`;
    }
    return row.value.ruleName;
  });

  const stageChip = computed(() => {
    if (row.value.kind === 'stagnant') return null;
    if (row.value.stage == null) return null;
    return alertStageLabel(row.value.stage);
  });

  const builtInSummary = computed(() => {
    const b = row.value.builtIn;
    const stagnant =
      row.value.stage != null
        ? b.stagnantHours?.[String(row.value.stage)]
        : undefined;
    return summarizeThreshold({
      kind: row.value.kind,
      warnAheadMinutes: b.warnAheadMinutes,
      criticalAfterMinutes:
        row.value.kind === 'stagnant'
          ? (stagnant ?? 0) * 60
          : b.criticalAfterMinutes,
      warnAheadRequiredMinutes: b.warnAheadRequiredMinutes,
      criticalAfterRequiredMinutes: b.criticalAfterRequiredMinutes,
      anchorOffsetMinutes: b.anchorOffsetMinutes,
      stagnantHours: stagnant,
      planEnabled: b.planEnabled,
      requiredEnabled: b.requiredEnabled
    });
  });

  const defaultCaption = computed(() => {
    if (!row.value.ruleId) return `系统默认：${builtInSummary.value}`;
    return `已按本公司调整 · 系统默认是「${builtInSummary.value}」`;
  });

  const setClock = (which: 'plan' | 'required', on: boolean) => {
    if (!on) {
      const other =
        which === 'plan' ? row.value.requiredEnabled : row.value.planEnabled;
      if (!other) return;
    }
    if (which === 'plan') row.value.planEnabled = on;
    else row.value.requiredEnabled = on;
    emit('change');
  };
</script>

<style lang="scss" scoped>
  .rule-card {
    padding: 16px 18px 14px;
    border-radius: 12px;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-bg-color);
    box-shadow: 0 1px 0 rgba(15, 23, 42, 0.03);
    transition:
      border-color 160ms ease,
      box-shadow 160ms ease,
      opacity 200ms ease;

    &.is-dirty {
      border-color: color-mix(
        in srgb,
        var(--el-color-primary) 45%,
        var(--el-border-color-lighter)
      );
      box-shadow: 0 0 0 1px
        color-mix(in srgb, var(--el-color-primary) 18%, transparent);
    }

    &.is-disabled {
      background: var(--el-fill-color-blank);

      .rule-card__head {
        margin-bottom: 0;
      }
    }

    &__head {
      display: flex;
      align-items: flex-start;
      gap: 16px;
      margin-bottom: 12px;
    }

    &__identity {
      flex: 1 1 auto;
      min-width: 0;
    }

    &__title-row {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
    }

    &__title {
      margin: 0;
      font-size: 15px;
      font-weight: 600;
      line-height: 1.3;
      letter-spacing: -0.01em;
      color: var(--el-text-color-primary);
    }

    &__stage {
      padding: 1px 7px;
      border-radius: 999px;
      background: var(--el-fill-color);
      color: var(--el-text-color-regular);
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.02em;
    }

    &__off {
      padding: 1px 7px;
      border-radius: 999px;
      background: var(--el-fill-color);
      color: var(--el-text-color-secondary);
      font-size: 11px;
      font-weight: 600;
    }

    &__dirty {
      padding: 1px 7px;
      border-radius: 999px;
      background: var(--el-color-primary-light-9);
      color: var(--el-color-primary);
      font-size: 11px;
      font-weight: 600;
    }

    &__off-hint {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }

    &__config {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    &__basis-hint {
      margin: -2px 0 0;
      font-size: 12px;
      line-height: 1.5;
      color: var(--el-text-color-secondary);
    }

    &__clock {
      padding: 10px 12px 12px;
      border-radius: 10px;
      border: 1px solid var(--el-border-color-extra-light);
      background: var(--el-fill-color-blank);

      &.is-off {
        background: var(--el-fill-color-lighter);
        border-color: transparent;
      }
    }

    &__clock-head {
      display: flex;
      align-items: center;
      margin-bottom: 8px;
      font-size: 13px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    &__clock-off {
      margin: 0;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }

    &__desc {
      margin: 4px 0 0;
      font-size: 12.5px;
      line-height: 1.5;
      color: var(--el-text-color-secondary);
    }

    &__instant {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 12px;
      border-radius: 8px;
      background: var(--el-fill-color-light);
      font-size: 13px;
      color: var(--el-text-color-regular);
    }

    &__instant-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--el-color-danger);
      box-shadow: 0 0 0 3px var(--el-color-danger-light-8);
    }

    &__foot {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px 16px;

      &.is-collapsed {
        margin-top: 12px;
      }
    }

    &__basis {
      display: inline-flex;
      align-self: flex-start;
      padding: 3px;
      border-radius: 9px;
      background: var(--el-fill-color);
    }

    &__basis-btn {
      margin: 0;
      padding: 5px 10px;
      border: none;
      border-radius: 7px;
      background: transparent;
      color: var(--el-text-color-regular);
      font-size: 12px;
      font-weight: 500;
      line-height: 1.3;
      cursor: pointer;
      transition:
        background 140ms ease,
        color 140ms ease,
        box-shadow 140ms ease,
        transform 100ms ease-out;

      &.is-active {
        background: var(--el-bg-color);
        color: var(--el-text-color-primary);
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
      }

      &:hover:not(:disabled):not(.is-active) {
        color: var(--el-text-color-primary);
      }

      &:active:not(:disabled) {
        transform: scale(0.97);
      }

      &:focus-visible {
        outline: 2px solid var(--el-color-primary);
        outline-offset: 1px;
      }

      &:disabled {
        cursor: not-allowed;
      }
    }

    &__kind-hint {
      margin: 0;
      font-size: 12px;
      line-height: 1.5;
      color: var(--el-text-color-secondary);
    }

    &__meta {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      margin-left: auto;
    }

    &__default {
      font-size: 12px;
      color: var(--el-text-color-placeholder);
      line-height: 1.4;
    }

    &__reset {
      margin: 0;
      padding: 0;
      border: none;
      background: none;
      color: var(--el-color-primary);
      font-size: 12px;
      cursor: pointer;
      transition:
        opacity 140ms ease,
        transform 100ms ease-out;

      &:hover {
        opacity: 0.8;
      }

      &:active {
        transform: scale(0.97);
      }

      &:focus-visible {
        outline: 2px solid var(--el-color-primary);
        outline-offset: 2px;
        border-radius: 4px;
      }
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .rule-card,
    .rule-card__basis-btn,
    .rule-card__reset {
      transition: none;
    }
  }
</style>
