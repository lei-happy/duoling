/**
 * 审批中心前端枚举与展示映射 + 业务摘要差异化渲染注册表
 */

export const INSTANCE_STATUS = {
  RUNNING: 0,
  APPROVED: 1,
  REJECTED: 2,
  WITHDRAWN: 3
} as const;

export function instanceStatusLabel(s?: number): string {
  switch (s) {
    case 0:
      return '审批中';
    case 1:
      return '已通过';
    case 2:
      return '已拒绝';
    case 3:
      return '已撤回';
    default:
      return '—';
  }
}

export function instanceStatusTag(
  s?: number
): 'info' | 'primary' | 'success' | 'danger' | 'warning' {
  switch (s) {
    case 0:
      return 'primary';
    case 1:
      return 'success';
    case 2:
      return 'danger';
    case 3:
      return 'info';
    default:
      return 'info';
  }
}

/** 审批记录动作 action -> 文案 */
export function actionLabel(action?: number): string {
  switch (action) {
    case 1:
      return '提交申请';
    case 2:
      return '同意';
    case 3:
      return '拒绝';
    case 4:
      return '撤回';
    case 5:
      return '转审';
    case 6:
      return '前加签';
    case 7:
      return '后加签';
    case 8:
      return '抄送';
    case 9:
      return '自动通过';
    case 10:
      return '跳过';
    default:
      return '操作';
  }
}

export function actionTimelineType(
  action?: number
): 'primary' | 'success' | 'danger' | 'info' | 'warning' {
  switch (action) {
    case 1:
      return 'primary';
    case 2:
    case 9:
      return 'success';
    case 3:
      return 'danger';
    case 4:
      return 'warning';
    default:
      return 'info';
  }
}

/** 节点状态 */
export function nodeStatusLabel(s?: number): string {
  switch (s) {
    case 0:
      return '未开始';
    case 1:
      return '审批中';
    case 2:
      return '已通过';
    case 3:
      return '已拒绝';
    case 4:
      return '已跳过';
    default:
      return '—';
  }
}

/** 任务状态 */
export function taskStatusLabel(s?: number): string {
  switch (s) {
    case 0:
      return '待处理';
    case 1:
      return '已同意';
    case 2:
      return '已拒绝';
    case 3:
      return '已转审';
    case 4:
      return '已失效';
    default:
      return '—';
  }
}

export function signTypeLabel(s?: number): string {
  switch (s) {
    case 1:
      return '或签';
    case 2:
      return '会签';
    case 3:
      return '依次会签';
    default:
      return '—';
  }
}

/** 业务场景码 -> 展示名 */
const BIZ_TYPE_LABELS: Record<string, string> = {
  social_capacity_audit: '社会运力准入审核'
};
export function bizTypeLabel(bizType?: string): string {
  if (!bizType) return '—';
  return BIZ_TYPE_LABELS[bizType] ?? bizType;
}

/**
 * 业务摘要差异化渲染注册表。
 * 不同 biz_type 的 summary 字段不同；默认按 key/value 平铺，
 * 业务方可在此登记自定义字段顺序/隐藏 title 等。
 */
export interface SummaryField {
  key: string;
  label: string;
}
const SUMMARY_SCHEMAS: Record<string, SummaryField[]> = {
  social_capacity_audit: [
    { key: '运力编号', label: '运力编号' },
    { key: '驾驶员', label: '驾驶员' },
    { key: '联系电话', label: '联系电话' },
    { key: '车牌号', label: '车牌号' },
    { key: '车辆类型', label: '车辆类型' },
    { key: '来源', label: '来源' }
  ]
};

/** 把 summary 对象规整成 [{label, value}]，title 字段不展示在明细里。 */
export function renderSummary(
  bizType: string | undefined,
  summary?: Record<string, any> | null
): Array<{ label: string; value: any }> {
  if (!summary) return [];
  const schema = bizType ? SUMMARY_SCHEMAS[bizType] : undefined;
  if (schema) {
    return schema
      .filter((f) => summary[f.key] !== undefined && summary[f.key] !== null)
      .map((f) => ({ label: f.label, value: summary[f.key] }));
  }
  return Object.entries(summary)
    .filter(([k]) => k !== 'title')
    .map(([k, v]) => ({ label: k, value: v }));
}
