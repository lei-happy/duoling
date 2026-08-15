import {
  DIM_ORDER,
  GROUPS,
  QUESTION_IDS,
  type DimKey
} from './question-bank';
import { STAGE_ORDER, type StageKey } from './stages';

/**
 * 计分与判档 —— 与《管理者精读版》同一套函数，改动前必须同步两边。
 */

/**
 * 各维题数不同（A/B 三题、C/D 两题），统一折算到 20 分制，
 * 保证与 20 题完整版的落档结果一致。
 */
const DIM_FACTOR: Record<DimKey, number> = {
  A: 20 / 12,
  B: 20 / 12,
  C: 20 / 8,
  D: 20 / 8
};

/** 题目 ID → 所属维度 */
const DIM_OF_QUESTION: Record<string, DimKey> = Object.fromEntries(
  GROUPS.flatMap((g) => g.questions.map((q) => [q.id, g.dim]))
);

export type DimScores = Record<DimKey, number>;

export interface ScoreResult {
  /** 四维得分，各 0–20 */
  dims: DimScores;
  /** 总分 0–80 */
  total: number;
  /** 已作答题数 */
  answered: number;
  /** 未作答的题目 ID */
  missing: string[];
  complete: boolean;
}

/** 按总分初判档位 */
export function stageByTotal(total: number): StageKey {
  if (total <= 18) return 's1';
  if (total <= 28) return 's2';
  if (total <= 38) return 's3';
  if (total <= 48) return 's4';
  if (total <= 56) return 's5';
  if (total <= 64) return 's6';
  if (total <= 72) return 's7';
  return 's8';
}

/** 取两个档位中较低的那个 */
function capStage(current: StageKey, maxAllowed: StageKey): StageKey {
  return STAGE_ORDER.indexOf(current) > STAGE_ORDER.indexOf(maxAllowed)
    ? maxAllowed
    : current;
}

/**
 * 判档：先按总分落档，答完后再按短板维度封顶。
 *
 * 封顶的意义是"木桶效应"——业务都没在线上跑，总分再高也谈不上智能化。
 * 未答完时只做总分初判，用于作答途中的实时预估。
 */
export function judgeStage(
  dims: DimScores,
  total: number,
  complete: boolean
): StageKey {
  let key = stageByTotal(total);
  if (!complete) {
    return key;
  }

  const { A, B, C, D } = dims;

  if (A <= 6) key = capStage(key, 's1');
  else if (A <= 10) key = capStage(key, 's2');
  else if (A <= 12) key = capStage(key, 's3');

  if (B <= 8) key = capStage(key, 's3');
  else if (B <= 11) key = capStage(key, 's4');

  if (C <= 8) key = capStage(key, 's5');
  else if (C <= 12) key = capStage(key, 's6');

  if (D <= 10) key = capStage(key, 's6');
  else if (D <= 13) key = capStage(key, 's7');

  // L8 要求四维都过硬，任一维偏科就退到 L7
  if (key === 's8' && (A < 14 || B < 14 || C < 14 || D < 14)) {
    key = 's7';
  }

  return key;
}

/** 分数最低的维度，用于「先补最弱一环」 */
export function weakestDim(dims: DimScores): DimKey {
  return DIM_ORDER.reduce(
    (weak, d) => (dims[d] < dims[weak] ? d : weak),
    DIM_ORDER[0]
  );
}

/** 把作答记录折算成四维分与总分 */
export function computeScores(answers: Record<string, string>): ScoreResult {
  const raw: DimScores = { A: 0, B: 0, C: 0, D: 0 };
  const missing: string[] = [];
  let answered = 0;

  QUESTION_IDS.forEach((id) => {
    const value = answers[id];
    if (value === undefined || value === '') {
      missing.push(id);
      return;
    }
    answered += 1;
    raw[DIM_OF_QUESTION[id]] += Number(value);
  });

  const dims = { A: 0, B: 0, C: 0, D: 0 } as DimScores;
  DIM_ORDER.forEach((d) => {
    dims[d] = Math.round(raw[d] * DIM_FACTOR[d]);
  });

  const total = DIM_ORDER.reduce((sum, d) => sum + dims[d], 0);

  return { dims, total, answered, missing, complete: missing.length === 0 };
}

/** 档位键转成刻度尺上的 1–8 序号 */
export function stageIndex(key: StageKey): number {
  return STAGE_ORDER.indexOf(key) + 1;
}
