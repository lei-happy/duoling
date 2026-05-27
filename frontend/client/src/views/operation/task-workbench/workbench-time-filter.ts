import type { TaskTimeField } from '@/api/operation/task/model';

export const TASK_TIME_FIELD_OPTIONS: Array<{
  value: TaskTimeField;
  label: string;
}> = [
  { value: 'createdAt', label: '制单时间' },
  { value: 'assignedAt', label: '分配时间' },
  { value: 'dispatchedAt', label: '派车时间' },
  { value: 'actualLoadTime', label: '装车时间' },
  { value: 'signedAt', label: '签收时间' }
];

/** 各阶段卡默认时间维度 */
export const POOL_DEFAULT_TIME_FIELD: Record<string, TaskTimeField> = {
  'pending-assign': 'createdAt',
  'pending-dispatch': 'assignedAt',
  'pending-load': 'dispatchedAt',
  'on-way': 'actualLoadTime',
  'pending-sign': 'signedAt'
};

export const resolveDefaultTimeField = (poolKey?: string): TaskTimeField =>
  (poolKey && POOL_DEFAULT_TIME_FIELD[poolKey]) || 'createdAt';

export const timeFieldLabel = (field: TaskTimeField): string =>
  TASK_TIME_FIELD_OPTIONS.find((o) => o.value === field)?.label ?? '时间';
