import { computed, reactive, ref } from 'vue';
import { PROFILE, QUESTION_IDS } from './question-bank';
import { STAGE } from './stages';
import {
  computeScores,
  judgeStage,
  stageIndex,
  weakestDim
} from './scoring';

/**
 * 自测页的作答状态。
 *
 * 分两组：画像题不计分，只随留资一起提交；计分题参与四维折算与判档。
 * 作答途中就实时给出预估档位，用户能看到指针在动，不用等提交。
 */
export function useSelfCheck() {
  /** 计分题作答，题目 ID → 选中值（字符串形式的 0–4） */
  const answers = reactive<Record<string, string>>({});
  /** 画像题作答 */
  const profile = reactive<Record<string, string>>({});
  /** 提交时未作答的题目，用于高亮 */
  const missing = ref<string[]>([]);
  /** 结果区是否已展开 */
  const submitted = ref(false);

  const scores = computed(() => computeScores(answers));

  const stageKey = computed(() =>
    judgeStage(scores.value.dims, scores.value.total, scores.value.complete)
  );

  const stage = computed(() => STAGE[stageKey.value]);

  /** 刻度尺档位：一题没答时为 null，整条尺子保持灰色 */
  const ladderIndex = computed(() =>
    scores.value.answered > 0 ? stageIndex(stageKey.value) : null
  );

  const weak = computed(() => weakestDim(scores.value.dims));

  /** 侧栏顶部那句状态文案 */
  const stageLabel = computed(() => {
    if (scores.value.complete) {
      return stage.value.name;
    }
    return scores.value.answered === 0
      ? '还没开始作答'
      : `作答中，预估${stage.value.short}`;
  });

  const submitLabel = computed(() =>
    scores.value.complete
      ? '查看我的水位与建议'
      : `查看结果（还剩 ${QUESTION_IDS.length - scores.value.answered} 题）`
  );

  /** 完成后带入留资表单的档位文案，如「L4 · 数字化推进期」 */
  const stageForLead = computed(() =>
    submitted.value ? `${stage.value.band} · ${stage.value.name}` : ''
  );

  function pick(questionId: string, value: string) {
    answers[questionId] = value;
    missing.value = missing.value.filter((id) => id !== questionId);
  }

  function pickProfile(questionId: string, value: string) {
    profile[questionId] = value;
  }

  /**
   * 提交。没答完不出档位，只标出还缺哪几题——给一个空档位比给一个错档位更糟。
   * 返回值告诉调用方该滚到结果区还是滚到第一道漏题。
   */
  function submit(): { ok: boolean; firstMissing?: string } {
    if (!scores.value.complete) {
      missing.value = [...scores.value.missing];
      return { ok: false, firstMissing: missing.value[0] };
    }
    missing.value = [];
    submitted.value = true;
    return { ok: true };
  }

  function reset() {
    QUESTION_IDS.forEach((id) => delete answers[id]);
    PROFILE.forEach((q) => delete profile[q.id]);
    missing.value = [];
    submitted.value = false;
  }

  return {
    answers,
    profile,
    missing,
    submitted,
    scores,
    stage,
    stageKey,
    ladderIndex,
    weak,
    stageLabel,
    submitLabel,
    stageForLead,
    pick,
    pickProfile,
    submit,
    reset
  };
}

export type SelfCheckStore = ReturnType<typeof useSelfCheck>;
