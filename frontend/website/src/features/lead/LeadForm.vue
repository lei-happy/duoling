<template>
  <form class="lead-form" novalidate @submit.prevent="onSubmit">
    <p v-if="stageLabel" class="lead-echo">
      已带入你的测评结果：{{ stageLabel }}
    </p>

    <div class="lead-grid">
      <label class="field">
        <span>企业名称</span>
        <input
          v-model.trim="form.company_name"
          class="input"
          type="text"
          autocomplete="organization"
          placeholder="如：华东某轿运企业"
          :aria-invalid="!!errors.company_name"
        />
        <span v-if="errors.company_name" class="field-error">
          {{ errors.company_name }}
        </span>
      </label>

      <label class="field">
        <span>联系人</span>
        <input
          v-model.trim="form.contact_person"
          class="input"
          type="text"
          autocomplete="name"
          placeholder="您的称呼"
          :aria-invalid="!!errors.contact_person"
        />
        <span v-if="errors.contact_person" class="field-error">
          {{ errors.contact_person }}
        </span>
      </label>

      <label class="field">
        <span>手机号</span>
        <input
          v-model.trim="form.contact_phone"
          class="input"
          type="tel"
          inputmode="numeric"
          maxlength="11"
          autocomplete="tel"
          placeholder="接收诊断结果"
          :aria-invalid="!!errors.contact_phone"
        />
        <span v-if="errors.contact_phone" class="field-error">
          {{ errors.contact_phone }}
        </span>
      </label>

      <label class="field">
        <span>自有板车数量</span>
        <select v-model="form.fleet_size" class="input">
          <option v-for="o in FLEET_OPTIONS" :key="o.value" :value="o.value">
            {{ o.label }}
          </option>
        </select>
      </label>
    </div>

    <label class="field">
      <span>
        当前最头疼的一件事
        <span class="hint">选填</span>
      </span>
      <input
        v-model.trim="form.pain_point"
        class="input"
        type="text"
        maxlength="255"
        placeholder="如：外协运费对账每月要三个人算一周"
      />
    </label>

    <!-- 蜜罐：真人看不见也 tab 不到，只有自动填表脚本会填 -->
    <div class="honeypot" aria-hidden="true">
      <label>
        请留空
        <input v-model="form.website" type="text" tabindex="-1" autocomplete="off" />
      </label>
    </div>

    <button
      type="submit"
      class="btn btn-primary btn-lg lead-submit"
      :disabled="submitting"
    >
      {{ submitting ? '正在提交，请稍候…' : '获取我的诊断报告' }}
      <span v-if="!submitting" class="arrow">→</span>
    </button>

    <p v-if="feedback" class="lead-feedback" :class="`is-${feedback.kind}`">
      {{ feedback.text }}
    </p>
    <p class="form-note">我们只用这些信息联系你，不会对外提供。</p>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRoute } from 'vue-router';
import { submitLead } from '@/api';
import type { DimScores } from '@/features/self-check/scoring';

/**
 * 留资表单。
 *
 * 自测做完了就把档位和四维分一起带走——销售拿着分数打电话，
 * 比只拿一个手机号有用得多。没做自测也能直接留，不强制先答题。
 */

const props = defineProps<{
  /** 展示用完整档位文案，如「L4 · 数字化推进期」；自测完成后才有 */
  stageLabel?: string;
  /** 档位号 L1–L8 */
  band?: string;
  stageName?: string;
  totalScore?: number;
  dims?: DimScores;
  /** 画像题 P1–P3 作答 */
  profileAnswers?: Record<string, string>;
}>();

const FLEET_OPTIONS = [
  { value: 'lt10', label: '10 台以内' },
  { value: '10-30', label: '10–30 台' },
  { value: '30-100', label: '30–100 台' },
  { value: 'gt100', label: '100 台以上' }
];

const MOBILE_RE = /^1[3-9]\d{9}$/;

const route = useRoute();

const form = reactive({
  company_name: '',
  contact_person: '',
  contact_phone: '',
  fleet_size: '30-100',
  pain_point: '',
  website: ''
});

const errors = reactive<Record<string, string>>({});
const submitting = ref(false);
const feedback = ref<{ kind: 'ok' | 'error'; text: string } | null>(null);

function validate(): boolean {
  Object.keys(errors).forEach((k) => delete errors[k]);

  if (form.company_name.length < 2) {
    errors.company_name = '请填写企业名称，顾问按企业规模准备资料';
  }
  if (!form.contact_person) {
    errors.contact_person = '请填写称呼，方便顾问联系时称呼你';
  }
  if (!MOBILE_RE.test(form.contact_phone)) {
    errors.contact_phone = '请填写 11 位手机号，我们只用它给你回电';
  }
  return Object.keys(errors).length === 0;
}

async function onSubmit() {
  feedback.value = null;
  if (!validate()) {
    return;
  }

  submitting.value = true;
  try {
    const message = await submitLead({
      company_name: form.company_name,
      contact_person: form.contact_person,
      contact_phone: form.contact_phone,
      fleet_size: form.fleet_size,
      pain_point: form.pain_point || undefined,
      profile_answers: props.profileAnswers,
      stage_band: props.band,
      stage_name: props.stageName,
      total_score: props.totalScore,
      dim_a: props.dims?.A,
      dim_b: props.dims?.B,
      dim_c: props.dims?.C,
      dim_d: props.dims?.D,
      source_page: route.path,
      website: form.website
    });
    feedback.value = { kind: 'ok', text: message };
    form.pain_point = '';
  } catch {
    feedback.value = {
      kind: 'error',
      text: '提交没能完成，请稍后再试；若一直不成功，也可以直接打电话找我们。'
    };
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped lang="scss">
.lead-form {
  background: var(--paper);
  border-radius: var(--r-lg);
  padding: 30px;
  box-shadow: var(--shadow);
}

/* 从自测带过来的档位，让用户确认"系统记得我刚才答了什么" */
.lead-echo {
  display: block;
  margin-bottom: 16px;
  padding: 9px 12px;
  border-radius: var(--r);
  background: var(--brand-soft);
  color: var(--brand);
  font-size: 13px;
  font-weight: 600;
}

.lead-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 16px;
}

.lead-submit {
  width: 100%;
}

.lead-feedback {
  margin-top: 12px;
  font-size: 14px;
  line-height: 1.6;

  &.is-ok {
    color: var(--ok);
  }

  &.is-error {
    color: #d9453d;
  }
}

@media (max-width: 768px) {
  .lead-form {
    padding: 24px 20px;
  }

  .lead-grid {
    grid-template-columns: 1fr;
  }
}
</style>
