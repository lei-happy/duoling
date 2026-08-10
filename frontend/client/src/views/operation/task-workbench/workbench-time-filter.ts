/**
 * 调度工作台 — 时间维度筛选
 *
 * 维度分两类，混用会让 KPI 卡片互相归零，必须区分对待：
 *
 * - **稳定维度**（进入当前阶段 / 制单时间）：每条任务都有值，放在任何阶段上筛选都成立，
 *   卡片之间可比，也不会把滞留任务藏起来 —— 工作台默认只用这一类。
 * - **节点维度**（分配 / 派车 / 装车 / 交车时间）：任务还没走到该节点时字段为空，
 *   一旦用来筛选就等于「只看已经走到该节点的任务」，前面阶段的卡片会全部变 0。
 *   保留为高级筛选，但**不做默认值**，选中时在筛选栏给出说明。
 */

import { getLastNDaysDates } from '@/utils/date-util';
import type { TaskTimeField } from '@/api/operation/task/model';

export interface TaskTimeFieldOption {
  value: TaskTimeField;
  label: string;
  /** 节点维度：仅统计已走到该节点的任务 */
  nodeScoped?: boolean;
}

export const TASK_TIME_FIELD_OPTIONS: TaskTimeFieldOption[] = [
  { value: 'stageEnteredAt', label: '进入当前阶段' },
  { value: 'createdAt', label: '制单时间' },
  { value: 'assignedAt', label: '分配时间', nodeScoped: true },
  { value: 'dispatchedAt', label: '派车时间', nodeScoped: true },
  { value: 'actualLoadTime', label: '装车时间', nodeScoped: true },
  { value: 'signedAt', label: '交车时间', nodeScoped: true }
];

/**
 * 工作台默认时间维度。
 *
 * 恒为「进入当前阶段」，**不随阶段卡切换**：切换阶段时自动改写时间维度，会让
 * 用户在待派车看到 14 单、切到待装车后同一张卡变成 0（那 14 单还没有派车时间）。
 */
export const DEFAULT_TASK_TIME_FIELD: TaskTimeField = 'stageEnteredAt';

/**
 * 日期面板快捷选项。默认不限时间后，收敛范围全靠用户手选，
 * 给出常用区间免得每次都翻日历。区间口径含今天在内（近 3 天 = 今天−2 至今天）。
 */
export const TIME_RANGE_SHORTCUTS: Array<{
  text: string;
  value: () => Date[];
}> = [
  { text: '近 3 天', value: () => getLastNDaysDates(3) },
  { text: '近 7 天', value: () => getLastNDaysDates(7) },
  { text: '近 30 天', value: () => getLastNDaysDates(30) }
];

export const timeFieldLabel = (field: TaskTimeField): string =>
  TASK_TIME_FIELD_OPTIONS.find((o) => o.value === field)?.label ?? '时间';

export const isNodeScopedTimeField = (field: TaskTimeField): boolean =>
  !!TASK_TIME_FIELD_OPTIONS.find((o) => o.value === field)?.nodeScoped;
