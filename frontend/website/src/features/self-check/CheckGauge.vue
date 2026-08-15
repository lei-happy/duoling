<template>
  <aside class="gauge" :data-band="stage.band" :style="resultVars">
    <span class="eyebrow">当前水位</span>
    <p class="gauge-stage">{{ stageLabel }}</p>

    <div class="gauge-score">
      <div>
        已答
        <b class="num">{{ scores.answered }}<i>/{{ TOTAL_QUESTIONS }}</i></b>
      </div>
      <div>
        折算总分
        <b class="num">{{ scores.total }}<i>/80</i></b>
      </div>
    </div>

    <WaterLadder
      class="gauge-ladder"
      palette="result"
      :index="ladderIndex"
      :pointer-label="stage.band"
    />

    <div class="dims">
      <div
        v-for="d in DIM_ORDER"
        :key="d"
        class="dim"
        :class="{ 'is-weak': scores.complete && d === weak }"
      >
        <div class="dim-top">
          <span>{{ DIM_NAME[d] }}</span>
          <b class="num">{{ scores.dims[d] }}<i>/20</i></b>
        </div>
        <div class="dim-bar">
          <i :style="{ transform: `scaleX(${scores.dims[d] / 20})` }" />
        </div>
        <span v-if="scores.complete && d === weak" class="dim-flag">
          最弱一环
        </span>
      </div>
    </div>

    <div class="gauge-actions">
      <button
        type="button"
        class="btn btn-primary"
        :disabled="scores.answered === 0"
        @click="emit('submit')"
      >
        {{ submitLabel }}
      </button>
      <button type="button" class="btn btn-line" @click="emit('reset')">
        清空重答
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import WaterLadder from '@/components/ui/WaterLadder.vue';
import {
  DIM_NAME,
  DIM_ORDER,
  QUESTION_IDS,
  type DimKey
} from './question-bank';
import type { ScoreResult } from './scoring';
import type { Stage } from './stages';

const props = defineProps<{
  scores: ScoreResult;
  stage: Stage;
  stageLabel: string;
  submitLabel: string;
  ladderIndex: number | null;
  weak: DimKey;
}>();

const emit = defineEmits<{ submit: []; reset: [] }>();

const resultVars = computed(() =>
  props.ladderIndex
    ? { '--result-current': `var(--result-${props.ladderIndex})` }
    : undefined
);

const TOTAL_QUESTIONS = QUESTION_IDS.length;
</script>

<style scoped lang="scss">
/* 侧栏跟着页面滚动吸顶，答题时始终能看见水位在动 */
.gauge {
  position: sticky;
  top: 92px;
  max-height: calc(100vh - 112px);
  min-width: 0;
  overflow-x: hidden;
  overflow-y: auto;
  background: var(--paper);
  border-radius: var(--r-lg);
  padding: 24px;
  box-shadow: var(--shadow);
}

.gauge-stage {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 4px 0 18px;
  color: var(--result-current, var(--ink-1));
}

.gauge-score {
  display: flex;
  gap: 22px;
  padding: 14px 0 18px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--line-soft);

  div {
    font-size: 13px;
    color: var(--ink-3);
  }

  b {
    display: block;
    font-size: 26px;
    font-weight: 600;
    color: var(--ink-1);
    line-height: 1.2;
  }

  i {
    font-style: normal;
    font-size: 14px;
    color: var(--ink-3);
  }
}

.gauge-ladder {
  margin: 0 0 22px;
}

.dims {
  display: grid;
  gap: 14px;
  padding-top: 20px;
  border-top: 1px solid var(--line-soft);
}

.dim-top {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 13px;
  color: var(--ink-2);
  margin-bottom: 6px;

  b {
    font-size: 14px;
    color: var(--ink-1);
  }

  i {
    font-style: normal;
    font-size: 11px;
    color: var(--ink-3);
  }
}

.dim-bar {
  height: 5px;
  border-radius: 3px;
  background: var(--bg-2);
  overflow: hidden;

  /* 用 scaleX 而不是 width，进度条的增长走合成层 */
  i {
    display: block;
    height: 100%;
    border-radius: 3px;
    background: var(--result-current, var(--tier-3));
    transform-origin: left center;
    transition: transform var(--dur-move) var(--ease);
  }
}

.dim-flag {
  display: inline-block;
  margin-top: 6px;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--result-current, var(--brand));
}

.gauge-actions {
  margin-top: 22px;
  display: grid;
  gap: 10px;

  .btn {
    width: 100%;
  }
}

@media (max-width: 1024px) {
  .gauge {
    position: static;
    max-height: none;
    overflow-x: hidden;
    overflow-y: visible;
  }

  .gauge-ladder {
    max-width: 520px;
  }
}

/* 进度条最终长度照常显示，只是不再演"长出来"的过程 */
@media (prefers-reduced-motion: reduce) {
  .dim-bar i {
    transition: none;
  }
}
</style>
