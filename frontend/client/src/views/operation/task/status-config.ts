/**
 * 任务单状态配置（与后端 task.status 保持一致）
 *
 * 注：6 已结算 已下线（财务结算与 task.status 解耦）；
 * 5 已交车 由 item 全交车聚合驱动，不接受人工 4→5 推进。
 */
/** 任务状态码（与后端 task_state_machine 保持一致） */
export const TASK_STATUS = {
  PENDING_ASSIGN: -1,
  PENDING_DISPATCH: 0,
  DISPATCHED: 1,
  LOADED: 2,
  ON_WAY: 3,
  ARRIVED: 4,
  SIGNED: 5,
  CLOSED: 7,
  CANCELLED: 9
} as const;

export const TASK_STATUS_OPTIONS = [
  { value: TASK_STATUS.PENDING_ASSIGN, label: '待分配', type: 'warning' },
  { value: TASK_STATUS.PENDING_DISPATCH, label: '待派车', type: 'info' },
  { value: TASK_STATUS.DISPATCHED, label: '已派车', type: 'primary' },
  { value: TASK_STATUS.LOADED, label: '已装车', type: 'warning' },
  { value: TASK_STATUS.ON_WAY, label: '在途', type: 'warning' },
  { value: TASK_STATUS.ARRIVED, label: '已到达', type: 'success' },
  { value: TASK_STATUS.SIGNED, label: '已交车', type: 'success' },
  { value: TASK_STATUS.CLOSED, label: '已关闭', type: 'info' },
  { value: TASK_STATUS.CANCELLED, label: '已取消', type: 'danger' }
] as const;

export const TASK_STATUS_MAP: Record<number, { label: string; type: string }> =
  TASK_STATUS_OPTIONS.reduce(
    (m, x) => {
      m[x.value] = { label: x.label, type: x.type };
      return m;
    },
    {} as Record<number, { label: string; type: string }>
  );

/** 承运方式码（与后端 CarrierType 保持一致） */
export const CARRIER_TYPE = {
  SELF: 1,
  CARRIER: 2,
  SOCIAL: 3
} as const;

/** 承运方式 */
export const CARRIER_TYPE_OPTIONS = [
  { value: CARRIER_TYPE.SELF, label: '自有车', type: 'primary' },
  { value: CARRIER_TYPE.CARRIER, label: '承运商', type: 'success' },
  { value: CARRIER_TYPE.SOCIAL, label: '社会运力', type: 'warning' }
] as const;

export const CARRIER_TYPE_MAP: Record<number, { label: string; type: string }> =
  CARRIER_TYPE_OPTIONS.reduce(
    (m, x) => {
      m[x.value] = { label: x.label, type: x.type };
      return m;
    },
    {} as Record<number, { label: string; type: string }>
  );

/** 承运方式简要说明（分配承运弹窗方块按钮文案） */
export const CARRIER_TYPE_INTRO: Record<number, string> = {
  [CARRIER_TYPE.SELF]: '公司自有运力，待派车环节再选司机与车牌',
  [CARRIER_TYPE.CARRIER]: '委托合作承运商，本步仅需选定承运商',
  [CARRIER_TYPE.SOCIAL]: '从社会运力池选择司机与车辆，选定后直接进入待装车'
};

/** 承运方式详细说明（分配承运弹窗按钮 hover 提示） */
export const CARRIER_TYPE_DETAIL_HINT: Record<number, string> = {
  [CARRIER_TYPE.SELF]:
    '自有车任务进入「待派车」后，由调度员在派车环节选择具体运力（司机/车牌），此处无需指定。',
  [CARRIER_TYPE.CARRIER]:
    '选定承运商后进入「待派车」，具体运力可在派车环节再绑定。',
  [CARRIER_TYPE.SOCIAL]: '选定社会运力后任务直接进入「待装车」，无需再派车。'
};

/** 调令类型（dispatch_type，与后端 dispatch_order_state_machine 保持一致） */
export const DISPATCH_TYPE_HEAVY = 1; // 重驶：带货主业务段
export const DISPATCH_TYPE_EMPTY = 2; // 空驶
export const DISPATCH_TYPE_INSPECTION = 3; // 年检
export const DISPATCH_TYPE_EMERGENCY = 4; // 应急
export const DISPATCH_TYPE_OTHER = 5; // 其他
/** 默认调令类型（未指定时按"重驶"处理） */
export const DISPATCH_TYPE_DEFAULT = DISPATCH_TYPE_HEAVY;

export const DISPATCH_TYPE_OPTIONS = [
  { value: DISPATCH_TYPE_HEAVY, label: '重驶', type: 'success' },
  { value: DISPATCH_TYPE_EMPTY, label: '空驶', type: 'info' },
  { value: DISPATCH_TYPE_INSPECTION, label: '年检', type: 'warning' },
  { value: DISPATCH_TYPE_EMERGENCY, label: '应急', type: 'danger' },
  { value: DISPATCH_TYPE_OTHER, label: '其他', type: 'info' }
] as const;

export const DISPATCH_TYPE_MAP: Record<
  number,
  { label: string; type: string }
> = DISPATCH_TYPE_OPTIONS.reduce(
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

export const SEGMENT_STATUS_MAP: Record<
  number,
  { label: string; type: string }
> = SEGMENT_STATUS_OPTIONS.reduce(
  (m, x) => {
    m[x.value] = { label: x.label, type: x.type };
    return m;
  },
  {} as Record<number, { label: string; type: string }>
);

/** 挂接货物状态码（与后端 item_state_machine 保持一致） */
export const ITEM_STATUS = {
  PENDING_LOAD: 0,
  LOADED: 1,
  UNLOADED: 2,
  SIGNED: 3,
  CANCELLED: 9
} as const;

/** 挂接货物状态 */
export const ITEM_STATUS_OPTIONS = [
  { value: ITEM_STATUS.PENDING_LOAD, label: '待装车', type: 'info' },
  { value: ITEM_STATUS.LOADED, label: '已装车', type: 'warning' },
  { value: ITEM_STATUS.UNLOADED, label: '已卸车', type: 'primary' },
  { value: ITEM_STATUS.SIGNED, label: '已交车', type: 'success' }
] as const;

export const ITEM_STATUS_MAP: Record<number, { label: string; type: string }> =
  ITEM_STATUS_OPTIONS.reduce(
    (m, x) => {
      m[x.value] = { label: x.label, type: x.type };
      return m;
    },
    {} as Record<number, { label: string; type: string }>
  );

/** 承运成本类型 */
export const CARRIER_COST_TYPE_OPTIONS = [
  { value: 1, label: '包车' },
  { value: 2, label: '按台' },
  { value: 3, label: '按吨公里' },
  { value: 4, label: '其他' }
] as const;
