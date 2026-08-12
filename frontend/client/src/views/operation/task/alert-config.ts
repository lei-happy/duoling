/**
 * 任务预警的前端展示配置
 *
 * **这里只放展示口径，不放判定口径**。级别怎么算、阈值多少，全部由后端
 * `biz_task_alert` 决定，前端只负责把 `alertLevel` / `ruleCode` 翻译成
 * 用户看得懂的中文与颜色。
 */

import type { TaskAlertLevel } from '@/api/operation/task/model';

/** 预警级别（与后端 biz_task_alert.level 一致） */
export const ALERT_LEVEL = {
  NONE: 0,
  WARN: 1,
  CRITICAL: 2
} as const;

export const ALERT_LEVEL_MAP: Record<
  number,
  { label: string; type: 'success' | 'warning' | 'danger' }
> = {
  [ALERT_LEVEL.NONE]: { label: '正常', type: 'success' },
  [ALERT_LEVEL.WARN]: { label: '关注', type: 'warning' },
  [ALERT_LEVEL.CRITICAL]: { label: '严重', type: 'danger' }
};

/** 预警处置状态（与后端 biz_task_alert.status 一致） */
export const ALERT_STATUS_MAP: Record<
  number,
  { label: string; type: 'danger' | 'success' | 'info' }
> = {
  0: { label: '待处理', type: 'danger' },
  1: { label: '已处理', type: 'success' },
  2: { label: '已忽略', type: 'info' },
  3: { label: '已自动消除', type: 'info' }
};

/**
 * 规则码 → 简称。
 *
 * 后端接口大多已带 `ruleName`，这里只服务于**只拿得到规则码**的场景
 * （任务列表行只回传 `alertCodes`，为省带宽不带名称）。
 */
export const ALERT_RULE_NAME: Record<string, string> = {
  ASSIGN_TIMEOUT: '待分配超时',
  DISPATCH_TIMEOUT: '待派车超时',
  LOAD_TIMEOUT: '待装车超时',
  DEPART_TIMEOUT: '装车后滞留未发车',
  ARRIVE_TIMEOUT: '到货超时',
  DELIVER_TIMEOUT: '到场后交车超时',
  STAGE_STAGNANT: '阶段滞留',
  CAPACITY_ABNORMAL: '承运运力状态异常',
  LOAD_MISMATCH: '装车台数不符',
  NO_ROUTE_PLAN: '未规划运输路线'
};

export const alertRuleName = (code: string): string =>
  ALERT_RULE_NAME[code] ?? code;

/**
 * 阶段名（与后端 catalog.STAGE_LABELS 一致）。
 *
 * 刻意不复用 `TASK_STATUS_MAP`：那套是「任务当前是什么状态」（已派车、已装车），
 * 预警语境要的是「这批单子在等什么」（待装车、待发车），说法必须和工作台卡片一致。
 */
export const ALERT_STAGE_LABELS: Record<number, string> = {
  [-1]: '待分配',
  0: '待派车',
  1: '待装车',
  2: '待发车',
  3: '在途',
  4: '待交车'
};

export const alertStageLabel = (stage?: number | null): string =>
  stage == null ? '全部阶段' : (ALERT_STAGE_LABELS[stage] ?? `阶段${stage}`);

/** 判定形态：决定配置页给哪些阈值字段 */
export const ALERT_KIND_HINT: Record<string, string> = {
  deadline: '对照承诺时间判断：快到点还没做完就提醒',
  anchor: '对照上一步动作判断：做完上一步后拖太久就提醒',
  stagnant: '只看在本阶段待了多久，计划时间缺失时靠它兜底',
  execution: '状态本身有问题，一旦发现立刻提醒，没有时间阈值'
};

/** 配置页分组：按调度员心智（盯时效 / 盯卡住 / 盯执行）而不是按数据库 kind */
export const ALERT_KIND_GROUPS: {
  key: string;
  title: string;
  hint: string;
  accent: 'primary' | 'warning' | 'danger';
  kinds: Array<'deadline' | 'anchor' | 'stagnant' | 'execution'>;
}[] = [
  {
    key: 'sla',
    title: '时效设置',
    hint: '对照承诺时间或上一步动作。快到点还没做完，工作台就会亮「关注 / 严重」。',
    accent: 'primary',
    kinds: ['deadline', 'anchor']
  },
  {
    key: 'stagnant',
    title: '阶段滞留',
    hint: '只看任务在本阶段待了多久。计划时间缺失时，靠它兜底，避免漏报。',
    accent: 'warning',
    kinds: ['stagnant']
  },
  {
    key: 'execution',
    title: '执行异常',
    hint: '状态本身有问题，一旦发现立刻提醒，没有时间阈值可调。',
    accent: 'danger',
    kinds: ['execution']
  }
];

/** 时间基准（deadline 类规则用；由两路开关派生，兼容旧数据） */
export const TIME_BASIS_OPTIONS = [
  { value: 0, label: '内部计划时间', hint: '只看自己排的计划装车/到货时间' },
  {
    value: 1,
    label: '客户要求时间',
    hint: '只看计划单上客户要求的装车/送达时间'
  },
  {
    value: 2,
    label: '两路都看',
    hint: '内部计划和客户要求各算一遍，谁先碰到阈值听谁的'
  }
] as const;

export const TIME_BASIS_MAP: Record<number, string> = TIME_BASIS_OPTIONS.reduce(
  (m, x) => {
    m[x.value] = x.label;
    return m;
  },
  {} as Record<number, string>
);

export const clocksFromTimeBasis = (basis?: number | null) => ({
  planEnabled: basis == null || basis === 0 || basis === 2,
  requiredEnabled: basis == null || basis === 1 || basis === 2
});

export const deriveTimeBasis = (plan: boolean, required: boolean): number =>
  plan && required ? 2 : required ? 1 : 0;

/**
 * 分钟数转成「X 天 X 小时」这类口语说法。
 * 列表里给调度员看的是「拖了多久」，精确到分钟没有意义，只保留两级单位。
 */
export const formatDurationMinutes = (minutes?: number | null): string => {
  const m = Math.max(0, Math.floor(minutes ?? 0));
  if (!m) return '--';
  if (m < 60) return `${m} 分钟`;
  const hours = Math.floor(m / 60);
  if (hours < 24) {
    const rest = m % 60;
    return rest ? `${hours} 小时 ${rest} 分` : `${hours} 小时`;
  }
  const days = Math.floor(hours / 24);
  const restHours = hours % 24;
  return restHours ? `${days} 天 ${restHours} 小时` : `${days} 天`;
};

export const isAlerting = (level?: TaskAlertLevel): boolean =>
  (level ?? 0) > ALERT_LEVEL.NONE;

/**
 * 阈值配置用的时长说法。0 表示「一到点就算」，不能写成「--」。
 */
export const formatThresholdMinutes = (minutes?: number | null): string => {
  const m = Math.max(0, Math.floor(minutes ?? 0));
  if (!m) return '即刻';
  return formatDurationMinutes(m);
};

export interface ThresholdSummaryInput {
  kind: string;
  warnAheadMinutes?: number | null;
  criticalAfterMinutes?: number | null;
  warnAheadRequiredMinutes?: number | null;
  criticalAfterRequiredMinutes?: number | null;
  anchorOffsetMinutes?: number | null;
  stagnantHours?: number | null;
  planEnabled?: boolean;
  requiredEnabled?: boolean;
}

const clockPhrase = (warn?: number | null, crit?: number | null): string => {
  const w = formatThresholdMinutes(warn);
  const c = formatThresholdMinutes(crit);
  const warnText = w === '即刻' ? '不提前关注' : `提前 ${w} 关注`;
  const critText = c === '即刻' ? '到期即严重' : `超时 ${c} 转严重`;
  return `${warnText}，${critText}`;
};

/** 把一条规则的阈值收成一句人话，列表和卡片页共用 */
export const summarizeThreshold = (input: ThresholdSummaryInput): string => {
  if (input.kind === 'execution') return '命中即提醒';
  if (input.kind === 'stagnant') {
    const hours = input.stagnantHours;
    if (hours == null) return '未设置';
    const extra = formatThresholdMinutes(input.criticalAfterMinutes);
    return extra === '即刻'
      ? `停留超过 ${hours} 小时即严重`
      : `停留超过 ${hours} 小时关注，再拖 ${extra} 转严重`;
  }
  if (input.kind === 'deadline') {
    const planOn = input.planEnabled !== false;
    const reqOn = input.requiredEnabled !== false;
    const parts: string[] = [];
    if (planOn) {
      parts.push(
        `内部${clockPhrase(input.warnAheadMinutes, input.criticalAfterMinutes)}`
      );
    }
    if (reqOn) {
      parts.push(
        `客户${clockPhrase(input.warnAheadRequiredMinutes, input.criticalAfterRequiredMinutes)}`
      );
    }
    if (!parts.length) return '两路都已关掉';
    return parts.join('；');
  }
  const parts: string[] = [];
  if (input.kind === 'anchor' && input.anchorOffsetMinutes != null) {
    parts.push(`允许停留 ${formatThresholdMinutes(input.anchorOffsetMinutes)}`);
  }
  parts.push(clockPhrase(input.warnAheadMinutes, input.criticalAfterMinutes));
  return parts.join('，');
};
