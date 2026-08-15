<template>
  <div>
    <!-- Hero -->
    <section class="band band-tight band-paper">
      <div class="wrap">
        <div class="sec-head sec-head--wide hero-head">
          <span class="eyebrow">3 道画像 + 10 题 · 约 3 分钟</span>
          <h1 class="h-hero hero-title">
            你的企业，<span class="hl">卡在哪一层？</span>
          </h1>
          <p class="lede">
            信息化、数字化、智能化、数智化不是四个价位的软件，而是四层能力。底座没打好就上
            AI，钱多半花在演示上。先花两分钟量一下水位，再决定接下来 90 天先补什么。
          </p>
          <p class="muted hero-note">
            每题五档，按你企业的真实情况选。四个维度各自折算成 20 分，满分 80
            分；短板会封顶你的档位，所以总分高但某一维很弱，不会被判成高阶段。
          </p>
        </div>
      </div>
    </section>

    <!-- 作答区 -->
    <section class="band band-soft band-line">
      <div class="wrap check-layout">
        <CheckGauge
          :scores="scores"
          :stage="stage"
          :stage-label="stageLabel"
          :submit-label="submitLabel"
          :ladder-index="ladderIndex"
          :weak="weak"
          @submit="onSubmit"
          @reset="onReset"
        />

        <div>
          <QuestionList
            :answers="answers"
            :profile="profile"
            :missing="missing"
            @pick="pick"
            @pick-profile="pickProfile"
          />

          <ResultPanel
            v-if="submitted"
            :stage="stage"
            :scores="scores"
            :weak="weak"
          />
        </div>
      </div>
    </section>

    <!-- 留资 -->
    <section id="lead" class="band band-paper">
      <div class="wrap lead">
        <div>
          <span class="eyebrow">下一步</span>
          <h2 class="h-sec lead-title">
            要一份针对你企业的诊断，而不是一份通用报告
          </h2>
          <p class="lede">
            留下联系方式，顾问会带着完整版《企业数智化转型路径》和 20
            题深度自检表联系你，按你的车辆规模、线路结构和现有系统，给一份能落地的 90
            天清单。
          </p>
          <ul class="lead-list">
            <li v-for="(step, i) in LEAD_STEPS" :key="step.title">
              <span class="num">{{ String(i + 1).padStart(2, '0') }}</span>
              <span><b>{{ step.title }}</b>：{{ step.desc }}</span>
            </li>
          </ul>
          <p class="muted lead-more">
            想先自己读一遍？完整 20 题深度自检与四阶段辨析，见
            <RouterLink class="btn-text" to="/transformation">
              数智化转型 <span class="arrow">→</span>
            </RouterLink>
          </p>
        </div>

        <LeadForm
          :stage-label="stageForLead"
          :band="leadStage.band"
          :stage-name="leadStage.name"
          :total-score="leadStage.total"
          :dims="leadStage.dims"
          :profile-answers="{ ...profile }"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick } from 'vue';
import { RouterLink } from 'vue-router';
import CheckGauge from '@/features/self-check/CheckGauge.vue';
import QuestionList from '@/features/self-check/QuestionList.vue';
import ResultPanel from '@/features/self-check/ResultPanel.vue';
import LeadForm from '@/features/lead/LeadForm.vue';
import { useSelfCheck } from '@/features/self-check/useSelfCheck';
import type { DimScores } from '@/features/self-check/scoring';

const {
  answers,
  profile,
  missing,
  submitted,
  scores,
  stage,
  ladderIndex,
  weak,
  stageLabel,
  submitLabel,
  stageForLead,
  pick,
  pickProfile,
  submit,
  reset
} = useSelfCheck();

const LEAD_STEPS = [
  {
    title: '先看现状',
    desc: '现有系统盘点、系统外操作清单、数据口径问题。'
  },
  {
    title: '再定顺序',
    desc: '按短板决定先补在线、补数据，还是补智能。'
  },
  {
    title: '最后算账',
    desc: '每一项投入对应哪个经营指标，多久能验证。'
  }
];

interface LeadStage {
  band?: string;
  name?: string;
  total?: number;
  dims?: DimScores;
}

/** 只在做完自测后才把结果带进留资，半途的预估档位对销售没有参考价值 */
const leadStage = computed<LeadStage>(() =>
  submitted.value
    ? {
        band: stage.value.band,
        name: stage.value.name,
        total: scores.value.total,
        dims: scores.value.dims
      }
    : {}
);

/** 吸顶导航约 64px，锚点滚动留出余量 */
const SCROLL_OFFSET = 88;

function scrollToEl(el: Element | null) {
  if (!el) {
    return;
  }
  const top = el.getBoundingClientRect().top + window.scrollY - SCROLL_OFFSET;
  window.scrollTo({
    top,
    behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches
      ? 'auto'
      : 'smooth'
  });
}

async function onSubmit() {
  const result = submit();
  await nextTick();

  // 没答完就滚到第一道漏题，答完了滚到结果区
  scrollToEl(
    result.ok
      ? document.getElementById('check-result')
      : document.getElementById(`q-${result.firstMissing}`)
  );
}

function onReset() {
  reset();
  scrollToEl(document.querySelector('.check-layout'));
}
</script>

<style scoped lang="scss">
.hero-head {
  max-width: none;
  margin-bottom: 0;
}

.hero-title {
  font-size: clamp(30px, 3.6vw, 46px);
  margin: 16px 0;
}

.hero-note {
  margin-top: 16px;
}

.check-layout {
  display: grid;
  grid-template-columns: 328px 1fr;
  gap: 44px;
  align-items: start;
}

/* --------------------------------------------------------------- 留资 */

.lead {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 48px;
  align-items: start;
}

.lead-title {
  margin: 14px 0 16px;
}

.lead-list {
  display: grid;
  gap: 16px;
  margin-top: 26px;

  li {
    display: flex;
    gap: 12px;
    font-size: 15px;
    color: var(--ink-2);
  }

  b {
    color: var(--ink-1);
    font-weight: 600;
  }

  .num {
    color: var(--brand);
    font-size: 13px;
    padding-top: 3px;
  }
}

.lead-more {
  margin-top: 26px;
}

@media (max-width: 1024px) {
  .check-layout,
  .lead {
    grid-template-columns: 1fr;
    gap: 28px;
  }
}
</style>
