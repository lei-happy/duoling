<template>
  <div
    id="check-result"
    class="result"
    :data-tier="stage.tier"
    :data-band="stage.band"
  >
    <header class="rs-head">
      <div class="rs-kicker">
        <span class="eyebrow">测评结果</span>
        <span class="rs-mark">
          {{ TIER_MARK[stage.tier].layer }} · {{ TIER_MARK[stage.tier].name }}
          <i v-if="TIER_MARK[stage.tier].tone">{{ TIER_MARK[stage.tier].tone }}</i>
        </span>
      </div>
      <div class="rs-title">
        <b class="rs-band num">{{ stage.band }}</b>
        <h3 class="h-sec">{{ stage.name }}</h3>
      </div>
      <p class="rs-meta num">
        总分 {{ scores.total }}/80 ·
        {{ DIM_ORDER.map((d) => `${DIM_NAME[d]} ${scores.dims[d]}`).join(' · ') }}
      </p>
      <WaterLadder
        class="rs-ladder"
        palette="result"
        :index="ladderIndex"
        :pointer-label="stage.band"
      />
      <p class="lede">{{ stage.desc }}</p>
    </header>

    <div class="rs-cols">
      <section class="rs-col">
        <h4 class="h-sub">先补最弱的一环：{{ DIM_NAME[weak] }}</h4>
        <ol class="rs-list">
          <li v-for="t in ACTIONS_BY_WEAK[weak]" :key="t">{{ t }}</li>
        </ol>
        <p class="muted">
          这三件事建议放进 90 天内完成，都能用经营结果验证。
        </p>
      </section>

      <section class="rs-col rs-col-plan">
        <h4 class="h-sub">这个阶段，{{ BRAND.product }}先帮你做三件事</h4>
        <ol class="rs-list">
          <li v-for="t in stage.moves" :key="t">{{ t }}</li>
        </ol>
        <p class="rs-plan">
          <span class="tag tag-pro">建议版本</span>
          {{ stage.plan }}
          <i>{{ stage.planWhy }}</i>
        </p>
      </section>
    </div>

    <footer class="rs-foot">
      <RouterLink class="btn btn-primary" to="/pricing">
        看 {{ stage.plan }}包含什么<span class="arrow">→</span>
      </RouterLink>
      <RouterLink class="btn btn-line" to="/transformation">
        读懂四个阶段怎么走
      </RouterLink>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink } from 'vue-router';
import { BRAND } from '@/config/brand';
import WaterLadder from '@/components/ui/WaterLadder.vue';
import { DIM_NAME, DIM_ORDER, type DimKey } from './question-bank';
import type { ScoreResult } from './scoring';
import { ACTIONS_BY_WEAK, type Stage } from './stages';

const props = defineProps<{
  stage: Stage;
  scores: ScoreResult;
  weak: DimKey;
}>();

const TIER_MARK = {
  1: { layer: '第一层', name: '信息化', tone: '底座未稳' },
  2: { layer: '第二层', name: '数字化', tone: '数还没对齐' },
  3: { layer: '第三层', name: '智能化', tone: '可以开始试' },
  4: { layer: '第四层', name: '数智化', tone: '闭环在转' }
} as const;

/** L1 → 1，给刻度尺指针定位 */
const ladderIndex = computed(() => Number(props.stage.band.slice(1)) || 1);
</script>

<style scoped lang="scss">
.result {
  position: relative;
  margin-top: 34px;
  border-radius: var(--r-lg);
  padding: 34px;
  background: var(--bg);
  overflow: hidden;
}

.result::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 3px;
  background: var(--tier-1);
}

.rs-kicker {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.rs-head .eyebrow::before {
  content: none;
}

.rs-mark {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--ink-2);
  background: var(--paper);

  i {
    font-style: normal;
    font-weight: 500;
    opacity: 0.8;
  }
}

.result[data-band='L1'] {
  --rs: var(--result-1);
  background: var(--result-1-soft);
}

.result[data-band='L2'] {
  --rs: var(--result-2);
  background: var(--result-2-soft);
}

.result[data-band='L3'] {
  --rs: var(--result-3);
  background: var(--result-3-soft);
}

.result[data-band='L4'] {
  --rs: var(--result-4);
  background: var(--result-4-soft);
}

.result[data-band='L5'] {
  --rs: var(--result-5);
  background: var(--result-5-soft);
}

.result[data-band='L6'] {
  --rs: var(--result-6);
  background: var(--result-6-soft);
}

.result[data-band='L1'],
.result[data-band='L2'],
.result[data-band='L3'],
.result[data-band='L4'],
.result[data-band='L5'],
.result[data-band='L6'] {
  &::before {
    background: var(--rs);
  }

  .eyebrow {
    color: var(--rs);

    &::before {
      background: var(--rs);
    }
  }

  .rs-mark {
    color: var(--rs);
    background: var(--paper);
  }

  .rs-band {
    color: var(--rs);
  }

  .rs-col-plan .rs-list li::before {
    background: color-mix(in srgb, var(--rs) 16%, #fff);
    color: var(--rs);
  }

  .rs-plan {
    color: var(--rs);
  }
}

/* L1 最要紧：顶栏加厚一档，档位号更重 */
.result[data-band='L1']::before {
  height: 5px;
}

.result[data-band='L7'],
.result[data-band='L8'] {
  --rs: var(--result-on-dark);
  background: #15241d;
  color: var(--ink-inv);

  &::before {
    background: var(--result-7);
  }

  :deep(.ladder) {
    --result-7: var(--result-on-dark);
    --result-8: var(--result-on-dark);
    --result-current: var(--result-on-dark);
  }

  :deep(.ladder-seg:not(.is-on)) {
    background: rgba(255, 255, 255, 0.12);
  }

  :deep(.ladder-scale span) {
    color: rgba(244, 247, 252, 0.5);
    border-top-color: rgba(255, 255, 255, 0.12);
  }

  :deep(.ladder-scale b) {
    color: rgba(244, 247, 252, 0.5);
  }

  :deep(.ladder-scale span.is-now) {
    color: var(--result-on-dark);
    border-top-color: var(--result-on-dark);

    b {
      color: var(--result-on-dark);
    }
  }

  .rs-mark {
    color: var(--result-on-dark);
    background: rgba(255, 255, 255, 0.08);
  }

  .lede,
  .muted,
  .rs-meta,
  .rs-list li {
    color: rgba(244, 247, 252, 0.72);
  }

  .h-sec,
  .h-sub,
  .rs-band,
  .rs-plan {
    color: #fff;
  }

  .eyebrow {
    color: var(--result-on-dark);

    &::before {
      background: var(--result-on-dark);
    }
  }

  .rs-col {
    background: rgba(255, 255, 255, 0.06);
  }

  .rs-list li::before {
    background: rgba(255, 255, 255, 0.12);
    color: rgba(244, 247, 252, 0.78);
  }

  .rs-col-plan .rs-list li::before {
    background: rgba(141, 202, 168, 0.2);
    color: var(--result-on-dark);
  }

  .btn-line {
    background: transparent;
    border-color: var(--line-dark);
    color: var(--ink-inv);
  }
}

.result[data-band='L8']::before {
  background: var(--result-8);
}

.rs-title {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin: 12px 0 10px;
}

.rs-band {
  font-size: clamp(40px, 5vw, 56px);
  font-weight: 700;
  letter-spacing: -0.04em;
  line-height: 0.9;
  color: var(--ink-1);
}

.rs-title .h-sec {
  margin: 0;
}

.rs-meta {
  font-size: 13px;
  color: var(--ink-3);
  margin-bottom: 16px;
}

.rs-ladder {
  max-width: 560px;
  margin-bottom: 22px;
}

.rs-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin: 30px 0;
}

.rs-col {
  padding: 22px 22px 20px;
  border-radius: var(--r);
  background: rgba(255, 255, 255, 0.55);
}

.rs-col .h-sub {
  margin-bottom: 14px;
}

.rs-list {
  counter-reset: rs;
  display: grid;
  gap: 12px;
  margin-bottom: 14px;

  li {
    position: relative;
    padding-left: 28px;
    font-size: 15px;
    color: var(--ink-2);
    line-height: 1.65;
    counter-increment: rs;

    &::before {
      content: counter(rs);
      position: absolute;
      left: 0;
      top: 3px;
      width: 19px;
      height: 19px;
      border-radius: 5px;
      background: var(--bg-2);
      color: var(--ink-2);
      font-family: var(--mono);
      font-size: 11px;
      font-weight: 600;
      display: grid;
      place-items: center;
    }
  }
}

.rs-col-plan .rs-list li::before {
  background: var(--brand-soft);
  color: var(--brand);
}

.rs-plan {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 16px;
  font-weight: 700;
  color: var(--brand);

  i {
    font-style: normal;
    font-size: 13px;
    font-weight: 400;
    color: var(--ink-3);
  }
}

.rs-foot {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding-top: 8px;
}

@media (max-width: 768px) {
  .result {
    padding: 24px 20px;
  }

  .rs-title {
    flex-direction: column;
    gap: 6px;
  }

  .rs-cols {
    grid-template-columns: 1fr;
  }
}
</style>
