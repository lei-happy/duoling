<template>
  <div>
    <!-- 画像题：不计分，只帮顾问判断你是谁 -->
    <section class="q-group">
      <header class="q-group-head">
        <span class="tag tag-brand">画像 · 不计分</span>
        <p class="muted">先告诉顾问你是谁、卡在哪，后面 10 题才用来量水位</p>
      </header>
      <ul class="q-list">
        <li v-for="(q, i) in PROFILE" :id="`q-${q.id}`" :key="q.id" class="q">
          <div class="q-head">
            <span class="q-no num">{{ pad(i + 1) }}</span>
            <p class="q-text">{{ q.text }}</p>
          </div>
          <div
            class="q-choices"
            :data-cols="q.choices.length"
            role="radiogroup"
            :aria-label="`画像第 ${pad(i + 1)} 题`"
          >
            <label v-for="c in q.choices" :key="c.value" class="ch">
              <input
                type="radio"
                :name="q.id"
                :value="c.value"
                :checked="profile[q.id] === c.value"
                @change="emit('pick-profile', q.id, c.value)"
              />
              <span class="ch-box">{{ c.label }}</span>
            </label>
          </div>
        </li>
      </ul>
    </section>

    <!-- 计分题：四维共 10 题 -->
    <section v-for="group in GROUPS" :key="group.dim" class="q-group">
      <header class="q-group-head">
        <span class="tag tag-brand">{{ group.dim }} · {{ group.title }}</span>
        <p class="muted">{{ group.note }}</p>
      </header>
      <ul class="q-list">
        <li
          v-for="q in group.questions"
          :id="`q-${q.id}`"
          :key="q.id"
          class="q"
          :class="{ 'is-missing': missing.includes(q.id) }"
        >
          <div class="q-head">
            <span class="q-no num">{{ pad(numberOf(q.id)) }}</span>
            <p class="q-text">{{ q.text }}</p>
          </div>
          <div
            class="q-choices"
            role="radiogroup"
            :aria-label="`第 ${pad(numberOf(q.id))} 题作答`"
          >
            <label v-for="c in CHOICES" :key="c.value" class="ch">
              <input
                type="radio"
                :name="q.id"
                :value="c.value"
                :checked="answers[q.id] === c.value"
                @change="emit('pick', q.id, c.value)"
              />
              <span class="ch-box">
                <b class="num">{{ c.value }}</b>
                {{ c.label }}
              </span>
            </label>
          </div>
          <p v-if="missing.includes(q.id)" class="q-missing-tip">
            这题还没选，选一档才能算出水位
          </p>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import {
  CHOICES,
  GROUPS,
  PROFILE,
  QUESTION_IDS
} from './question-bank';

defineProps<{
  answers: Record<string, string>;
  profile: Record<string, string>;
  missing: string[];
}>();

const emit = defineEmits<{
  pick: [questionId: string, value: string];
  'pick-profile': [questionId: string, value: string];
}>();

function pad(n: number) {
  return String(n).padStart(2, '0');
}

/** 计分题从 04 起编号，接在 3 道画像题之后 */
function numberOf(id: string) {
  return PROFILE.length + QUESTION_IDS.indexOf(id) + 1;
}
</script>

<style scoped lang="scss">
.q-group + .q-group {
  margin-top: 34px;
}

.q-group-head {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding-bottom: 12px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--line);
}

.q-list {
  display: grid;
  gap: 14px;
}

.q {
  background: var(--paper);
  border: 1px solid transparent;
  border-radius: var(--r-lg);
  padding: 20px 22px;
  transition:
    border-color var(--dur-hover) var(--ease),
    box-shadow var(--dur-hover) var(--ease);

  /* 漏答：红边 + 就地说明，比顶部弹一句"请填完整"好找得多 */
  &.is-missing {
    border-color: #d9453d;
    box-shadow: 0 0 0 3px rgba(217, 69, 61, 0.12);
  }
}

.q-head {
  display: flex;
  gap: 14px;
  margin-bottom: 16px;
}

.q-no {
  font-size: 12px;
  color: var(--ink-3);
  padding-top: 3px;
  flex-shrink: 0;
}

.q-text {
  font-size: 16px;
  line-height: 1.65;
}

.q-missing-tip {
  margin-top: 10px;
  padding-left: 34px;
  font-size: 13px;
  color: #d9453d;
}

.q-choices {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  padding-left: 34px;

  &[data-cols='3'] {
    grid-template-columns: repeat(3, 1fr);
    max-width: 560px;
  }

  &[data-cols='4'] {
    grid-template-columns: repeat(4, 1fr);
  }

  &[data-cols='5'] {
    grid-template-columns: repeat(5, 1fr);
  }
}

.ch {
  position: relative;
  display: block;
  cursor: pointer;

  input {
    position: absolute;
    inset: 0;
    opacity: 0;
    cursor: pointer;
  }
}

.ch-box {
  display: block;
  padding: 9px 4px;
  text-align: center;
  border: 1px solid var(--line);
  border-radius: var(--r);
  background: var(--bg);
  font-size: 13px;
  color: var(--ink-2);
  transition:
    border-color var(--dur-hover) var(--ease),
    background var(--dur-hover) var(--ease),
    color var(--dur-hover) var(--ease);

  b {
    display: block;
    font-size: 11px;
    font-weight: 500;
    color: var(--ink-3);
    margin-bottom: 2px;
  }
}

.ch input:checked + .ch-box {
  border-color: var(--brand);
  background: var(--brand-soft);
  color: var(--brand);
  font-weight: 600;

  b {
    color: var(--brand);
  }
}

.ch input:focus-visible + .ch-box {
  outline: 2px solid var(--brand);
  outline-offset: 2px;
}

@media (hover: hover) and (pointer: fine) {
  .q:hover {
    border-color: var(--ink-4);
  }

  .ch:hover .ch-box {
    border-color: var(--brand);
    background: var(--paper);
  }
}

@media (max-width: 768px) {
  .q {
    padding: 18px 16px;
  }

  .q-choices {
    gap: 5px;
    padding-left: 0;
  }

  .q-choices[data-cols='3'],
  .q-choices[data-cols='4'] {
    grid-template-columns: 1fr;
  }

  .q-missing-tip {
    padding-left: 0;
  }

  .ch-box {
    padding: 8px 2px;
    font-size: 11px;
  }
}

/* 小屏五档改纵向：点击区域够大，文字不挤成一列一个字 */
@media (max-width: 480px) {
  .q-choices,
  .q-choices[data-cols='5'] {
    grid-template-columns: 1fr;
    gap: 6px;
  }

  .ch-box {
    display: flex;
    align-items: center;
    gap: 10px;
    text-align: left;
    padding: 10px 12px;
    font-size: 14px;

    b {
      margin-bottom: 0;
      min-width: 14px;
    }
  }
}
</style>
