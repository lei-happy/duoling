<!--
  预警阈值时间轴

  把「关注 / 严重」两级阈值画成一条从左到右的升级轨道：
    正常 → 关注 → 应完成 → 严重
  数字输入在上、色段在下：改值时色段宽度跟着走，调度员不用读字段名也能看懂尺子。
-->
<template>
  <div
    class="threshold-track"
    :class="{
      'is-compact': compact,
      'is-disabled': disabled,
      [`is-${kind}`]: true
    }"
  >
    <div v-if="!compact" class="threshold-track__controls">
      <div v-if="kind === 'anchor'" class="threshold-track__anchor">
        <span class="threshold-track__chip-label">允许停留</span>
        <el-input-number
          :model-value="anchorOffsetMinutes"
          size="small"
          :min="0"
          :step="30"
          :disabled="disabled"
          controls-position="right"
          @update:model-value="onAnchor"
        />
        <span class="threshold-track__chip-unit">分钟后算应完成</span>
      </div>

      <div class="threshold-track__row">
        <div
          v-if="kind === 'stagnant'"
          class="threshold-track__chip threshold-track__chip--warn"
        >
          <span class="threshold-track__chip-label">停留超过</span>
          <el-input-number
            :model-value="stagnantHours"
            size="small"
            :min="1"
            :step="1"
            :disabled="disabled"
            controls-position="right"
            @update:model-value="onStagnant"
          />
          <span class="threshold-track__chip-unit">小时开始关注</span>
        </div>
        <div v-else class="threshold-track__chip threshold-track__chip--warn">
          <span class="threshold-track__chip-label">
            <template v-if="timeBasisLabel"
              >相对「{{ timeBasisLabel }}」</template
            >
            提前
          </span>
          <el-input-number
            :model-value="warnAheadMinutes"
            size="small"
            :min="0"
            :step="30"
            :disabled="disabled"
            controls-position="right"
            @update:model-value="onWarn"
          />
          <span class="threshold-track__chip-unit">分钟标为「关注」</span>
        </div>

        <div class="threshold-track__chip threshold-track__chip--critical">
          <span class="threshold-track__chip-label">
            {{ kind === 'stagnant' ? '再拖' : '超时' }}
          </span>
          <el-input-number
            :model-value="criticalAfterMinutes"
            size="small"
            :min="0"
            :step="30"
            :disabled="disabled"
            controls-position="right"
            @update:model-value="onCritical"
          />
          <span class="threshold-track__chip-unit">分钟升为「严重」</span>
        </div>
      </div>
    </div>

    <div class="threshold-track__bar" role="img" :aria-label="ariaLabel">
      <div
        class="threshold-track__seg threshold-track__seg--normal"
        :style="segStyle(weights.normal)"
      >
        <span class="threshold-track__seg-label">正常</span>
      </div>
      <div
        v-if="weights.warn > 0"
        class="threshold-track__seg threshold-track__seg--warn"
        :style="segStyle(weights.warn)"
      >
        <span class="threshold-track__seg-label">关注</span>
      </div>
      <div v-if="showDueTick" class="threshold-track__tick">
        <span class="threshold-track__tick-line" aria-hidden="true"></span>
        <span class="threshold-track__tick-label">{{ dueLabel }}</span>
      </div>
      <div
        class="threshold-track__seg threshold-track__seg--critical"
        :style="segStyle(weights.critical)"
      >
        <span class="threshold-track__seg-label">严重</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import {
    formatThresholdMinutes,
    summarizeThreshold
  } from '../../task/alert-config';

  const props = withDefaults(
    defineProps<{
      kind: string;
      warnAheadMinutes?: number | null;
      criticalAfterMinutes?: number | null;
      anchorOffsetMinutes?: number | null;
      stagnantHours?: number | null;
      timeBasisLabel?: string;
      compact?: boolean;
      disabled?: boolean;
    }>(),
    {
      compact: false,
      disabled: false
    }
  );

  const emit = defineEmits<{
    (e: 'update:warnAheadMinutes', v: number): void;
    (e: 'update:criticalAfterMinutes', v: number): void;
    (e: 'update:anchorOffsetMinutes', v: number): void;
    (e: 'update:stagnantHours', v: number): void;
    (e: 'change'): void;
  }>();

  const MIN_WEIGHT = 24;

  const weights = computed(() => {
    if (props.kind === 'stagnant') {
      const safe = Math.max((props.stagnantHours ?? 0) * 60, MIN_WEIGHT);
      const warnMin = Math.max(0, props.criticalAfterMinutes ?? 0);
      return {
        normal: safe,
        warn: warnMin > 0 ? Math.max(warnMin, MIN_WEIGHT) : 0,
        critical: warnMin > 0 ? MIN_WEIGHT : MIN_WEIGHT * 0.8
      };
    }
    const warnMin = Math.max(0, props.warnAheadMinutes ?? 0);
    const critMin = Math.max(0, props.criticalAfterMinutes ?? 0);
    return {
      normal: Math.max(warnMin, critMin, 90),
      warn: warnMin > 0 ? Math.max(warnMin, MIN_WEIGHT) : 0,
      critical: critMin > 0 ? Math.max(critMin, MIN_WEIGHT) : MIN_WEIGHT * 0.7
    };
  });

  const showDueTick = computed(() => props.kind !== 'stagnant');

  const dueLabel = computed(() => '应完成');

  const summary = computed(() =>
    summarizeThreshold({
      kind: props.kind,
      warnAheadMinutes: props.warnAheadMinutes,
      criticalAfterMinutes: props.criticalAfterMinutes,
      anchorOffsetMinutes: props.anchorOffsetMinutes,
      stagnantHours: props.stagnantHours
    })
  );

  const ariaLabel = computed(() => {
    if (props.kind === 'stagnant') {
      return `停留超过 ${props.stagnantHours ?? 0} 小时关注，再拖 ${formatThresholdMinutes(props.criticalAfterMinutes)} 升为严重`;
    }
    return summary.value;
  });

  const totalWeight = computed(
    () => weights.value.normal + weights.value.warn + weights.value.critical
  );

  const segStyle = (weight: number) => ({
    flexGrow: weight,
    flexBasis: `${totalWeight.value ? (weight / totalWeight.value) * 100 : 0}%`
  });

  const bump = () => emit('change');

  const onWarn = (v: number | undefined) => {
    emit('update:warnAheadMinutes', v ?? 0);
    bump();
  };
  const onCritical = (v: number | undefined) => {
    emit('update:criticalAfterMinutes', v ?? 0);
    bump();
  };
  const onAnchor = (v: number | undefined) => {
    emit('update:anchorOffsetMinutes', v ?? 0);
    bump();
  };
  const onStagnant = (v: number | undefined) => {
    emit('update:stagnantHours', v ?? 1);
    bump();
  };
</script>

<style lang="scss" scoped>
  .threshold-track {
    min-width: 0;

    &.is-disabled {
      opacity: 0.48;
      pointer-events: none;
    }

    &:not(.is-compact):not(.is-stagnant) {
      padding-bottom: 18px;
    }

    &__bar {
      display: flex;
      align-items: stretch;
      height: 8px;
      border-radius: 999px;
      background: var(--el-fill-color);
    }

    &__seg {
      position: relative;
      min-width: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      transition:
        flex-grow 200ms ease-out,
        flex-basis 200ms ease-out;

      &:first-child {
        border-radius: 999px 0 0 999px;
      }

      &:last-of-type {
        border-radius: 0 999px 999px 0;
      }

      &-label {
        display: none;
      }

      &--normal {
        background: color-mix(
          in srgb,
          var(--el-color-success) 16%,
          var(--el-fill-color)
        );
        color: var(--el-color-success);
      }

      &--warn {
        background: color-mix(
          in srgb,
          var(--el-color-warning) 22%,
          var(--el-fill-color)
        );
        color: var(--el-color-warning);
      }

      &--critical {
        background: color-mix(
          in srgb,
          var(--el-color-danger) 20%,
          var(--el-fill-color)
        );
        color: var(--el-color-danger);
      }
    }

    &__tick {
      position: relative;
      flex: 0 0 0;
      z-index: 1;
    }

    &__tick-line {
      position: absolute;
      top: -3px;
      bottom: -3px;
      left: -1px;
      width: 2px;
      border-radius: 1px;
      background: var(--el-text-color-primary);
    }

    &__tick-label {
      position: absolute;
      top: calc(100% + 4px);
      left: 50%;
      transform: translateX(-50%);
      font-size: 11px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      white-space: nowrap;
      letter-spacing: 0.02em;
    }

    &__controls {
      margin-bottom: 12px;
    }

    &__anchor {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 10px;
      font-size: 12px;
      color: var(--el-text-color-regular);
    }

    &__row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    &__chip {
      display: inline-flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 6px;
      padding: 6px 10px;
      border-radius: 8px;
      font-size: 12px;
      line-height: 1.4;

      &--warn {
        background: var(--el-color-warning-light-9);
      }

      &--critical {
        background: var(--el-color-danger-light-9);
      }
    }

    &__chip-label {
      color: var(--el-text-color-regular);
      font-weight: 500;
    }

    &__chip-unit {
      color: var(--el-text-color-secondary);
    }

    &.is-compact {
      .threshold-track__bar {
        height: 8px;
        border-radius: 999px;
      }

      .threshold-track__seg:first-child {
        border-radius: 999px 0 0 999px;
      }

      .threshold-track__seg:last-of-type {
        border-radius: 0 999px 999px 0;
      }

      .threshold-track__seg-label,
      .threshold-track__tick-label {
        display: none;
      }

      .threshold-track__tick-line {
        top: -2px;
        bottom: -2px;
      }
    }
  }

  .threshold-track :deep(.el-input-number) {
    width: 108px;
  }

  @media (prefers-reduced-motion: reduce) {
    .threshold-track__seg {
      transition: none;
    }
  }
</style>
