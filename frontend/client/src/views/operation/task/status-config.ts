/**
 * 任务单状态配置（与后端 task.status 保持一致）
 *
 * 注：6 已结算 已下线（财务结算与 task.status 解耦）；
 * 5 已签收 由 item 全签收聚合驱动，不接受人工 4→5 推进。
 */
export const TASK_STATUS_OPTIONS = [
  { value: -1, label: '待分配', type: 'warning' },
  { value: 0, label: '待派车', type: 'info' },
  { value: 1, label: '已派车', type: 'primary' },
  { value: 2, label: '已装车', type: 'warning' },
  { value: 3, label: '在途', type: 'warning' },
  { value: 4, label: '已到达', type: 'success' },
  { value: 5, label: '已签收', type: 'success' },
  { value: 7, label: '已关闭', type: 'info' },
  { value: 9, label: '已取消', type: 'danger' }
] as const;

export const TASK_STATUS_MAP: Record<number, { label: string; type: string }> =
  TASK_STATUS_OPTIONS.reduce(
    (m, x) => {
      m[x.value] = { label: x.label, type: x.type };
      return m;
    },
    {} as Record<number, { label: string; type: string }>
  );

/** 承运方式 */
export const CARRIER_TYPE_OPTIONS = [
  { value: 1, label: '自有车', type: 'primary' },
  { value: 2, label: '承运商', type: 'success' },
  { value: 3, label: '社会运力', type: 'warning' }
] as const;

export const CARRIER_TYPE_MAP: Record<number, { label: string; type: string }> =
  CARRIER_TYPE_OPTIONS.reduce(
    (m, x) => {
      m[x.value] = { label: x.label, type: x.type };
      return m;
    },
    {} as Record<number, { label: string; type: string }>
  );

/** 段状态 */
export const SEGMENT_STATUS_OPTIONS = [
  { value: 0, label: '待装车', type: 'info' },
  { value: 1, label: '装车中', type: 'warning' },
  { value: 2, label: '在途', type: 'warning' },
  { value: 3, label: '已到达', type: 'success' },
  { value: 4, label: '已卸车', type: 'success' }
] as const;

/** 挂接货物状态 */
export const ITEM_STATUS_OPTIONS = [
  { value: 0, label: '待装车', type: 'info' },
  { value: 1, label: '已装车', type: 'warning' },
  { value: 2, label: '已卸车', type: 'primary' },
  { value: 3, label: '已签收', type: 'success' }
] as const;

/** 承运成本类型 */
export const CARRIER_COST_TYPE_OPTIONS = [
  { value: 1, label: '包车' },
  { value: 2, label: '按台' },
  { value: 3, label: '按吨公里' },
  { value: 4, label: '其他' }
] as const;
