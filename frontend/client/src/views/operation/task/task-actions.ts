/**
 * 运输任务单 - 语义化动作配置
 *
 * 把"按 status 推进"翻译为"按业务场景命名的动作"，
 * 供台账列表 / 详情抽屉 / 调度工作台共用。
 *
 * 每个 status 在每个时点最多对应 1 个"主动作"。
 */

export type TaskActionKey =
  | 'assign-carrier' // 确认承运分配 (status -1 → 0)
  | 'dispatch' // 派车 (status 0 → 1)
  | 'plan-route' // 规划路线（独立动作，不改 status）
  | 'confirm-load' // 确认装车 (1 → 2)
  | 'depart' // 标记出发 (2 → 3)
  | 'confirm-arrive' // 确认到达 (3 → 4)
  | 'confirm-sign' // 确认签收：item 级签收，全部签收后聚合驱动 task 4→5
  | 'close' // 关闭任务 (5 → 7)
  // —— 逆向通道（参考 02.运单与任务单状态机联动设计.md §4.5）
  | 'revert-load' // 撤销装车 (2 → 1)
  | 'revert-depart' // 撤回出发 (3 → 2)
  | 'revert-arrive' // 撤回到达 (4 → 3)
  | 'force-cancel'; // 强制取消（2/3/4 → 9，线下取消）

export interface TaskActionConfig {
  key: TaskActionKey;
  label: string;
  buttonType: 'primary' | 'success' | 'warning' | 'info' | 'danger';
  permission: string;
  /** 需要打开弹窗时填，对应 action-*.vue 组件名 */
  dialog?:
    | 'assign-carrier'
    | 'dispatch'
    | 'plan-route'
    | 'confirm-load'
    | 'confirm-arrive'
    | 'confirm-sign'
    | 'revert'
    | 'force-cancel';
  /** 是否纯 confirm（不打开弹窗，直接 ElMessageBox.confirm） */
  confirm?: boolean;
  /** 是否需要跳转打开费用单创建（生成结算单） */
  openSettlement?: boolean;
  /** 逆向跳转目标态（revert-* 才有） */
  revertTo?: number;
  /** 逆向动作能从哪个状态进入（用于运行时校验） */
  revertFrom?: number;
}

export const TASK_ACTION_CONFIGS: Record<TaskActionKey, TaskActionConfig> = {
  'assign-carrier': {
    key: 'assign-carrier',
    label: '分配承运',
    buttonType: 'primary',
    permission: 'operation:task:dispatch',
    dialog: 'assign-carrier'
  },
  dispatch: {
    key: 'dispatch',
    label: '派车',
    buttonType: 'primary',
    permission: 'operation:task:dispatch',
    dialog: 'dispatch'
  },
  'plan-route': {
    key: 'plan-route',
    label: '规划路线',
    buttonType: 'primary',
    permission: 'operation:task:plan-route',
    dialog: 'plan-route'
  },
  'confirm-load': {
    key: 'confirm-load',
    label: '确认装车',
    buttonType: 'warning',
    permission: 'operation:task:confirm-load',
    dialog: 'confirm-load'
  },
  depart: {
    key: 'depart',
    label: '标记出发',
    buttonType: 'warning',
    permission: 'operation:task:confirm-depart',
    confirm: true
  },
  'confirm-arrive': {
    key: 'confirm-arrive',
    label: '确认到达',
    buttonType: 'success',
    permission: 'operation:task:confirm-arrive',
    dialog: 'confirm-arrive'
  },
  'confirm-sign': {
    key: 'confirm-sign',
    label: '确认签收',
    buttonType: 'success',
    permission: 'operation:task:confirm-sign',
    dialog: 'confirm-sign'
  },
  close: {
    key: 'close',
    label: '关闭任务',
    buttonType: 'info',
    permission: 'operation:task:close',
    confirm: true
  },
  // —— 逆向通道 —— //
  'revert-load': {
    key: 'revert-load',
    label: '撤销装车',
    buttonType: 'warning',
    permission: 'operation:task:revert-load',
    dialog: 'revert',
    revertFrom: 2,
    revertTo: 1
  },
  'revert-depart': {
    key: 'revert-depart',
    label: '撤回出发',
    buttonType: 'warning',
    permission: 'operation:task:revert-depart',
    dialog: 'revert',
    revertFrom: 3,
    revertTo: 2
  },
  'revert-arrive': {
    key: 'revert-arrive',
    label: '撤回到达',
    buttonType: 'warning',
    permission: 'operation:task:revert-arrive',
    dialog: 'revert',
    revertFrom: 4,
    revertTo: 3
  },
  'force-cancel': {
    key: 'force-cancel',
    label: '强制取消',
    buttonType: 'danger',
    permission: 'operation:task:force-cancel',
    dialog: 'force-cancel'
  }
};

/**
 * 根据 status 取下一步主动作。
 * - -1,0,1,2,3,4：分别对应分配承运 / 派车 / 装车 / 出发 / 到达 / 签收。
 * - 4→5 已签收：由 item 全签收聚合触发，"确认签收"在 status=4 阶段操作。
 * - 5 (已签收)：主动作是「关闭任务」；结算单走财务工作台，不在主动作中暴露。
 * - 7,9：无主动作。
 */
const PRIMARY_BY_STATUS: Record<number, TaskActionKey | null> = {
  [-1]: 'assign-carrier',
  0: 'dispatch',
  1: 'confirm-load',
  2: 'depart',
  3: 'confirm-arrive',
  4: 'confirm-sign',
  5: 'close',
  7: null,
  9: null
};

export const getPrimaryTaskAction = (
  status: number | null | undefined
): TaskActionConfig | null => {
  if (status === null || status === undefined) return null;
  const k = PRIMARY_BY_STATUS[status];
  return k ? TASK_ACTION_CONFIGS[k] : null;
};

/**
 * 部分状态除主动作外，还有次要动作。
 * 当前任务侧无额外次要动作；财务相关入口（生成结算单等）一律由财务工作台触发。
 */
export const getSecondaryTaskActions = (
  status: number | null | undefined
): TaskActionConfig[] => {
  if (status === null || status === undefined) return [];
  return [];
};

/**
 * 当前状态可用的逆向动作（撤销/强制取消）。
 *
 * 与 §4.5 反向跳转矩阵一致：
 * - 2 → 撤销装车；强制取消
 * - 3 → 撤回出发；强制取消
 * - 4 → 撤回到达；强制取消
 *
 * 说明：5 已签收 由 item 全签收聚合驱动，回退路径走 item 级"撤销签收"
 * （修改对应 item.status 3→2），不在任务级 revert 列表里暴露。
 */
const REVERSE_BY_STATUS: Record<number, TaskActionKey[]> = {
  2: ['revert-load', 'force-cancel'],
  3: ['revert-depart', 'force-cancel'],
  4: ['revert-arrive', 'force-cancel']
};

export const getReverseTaskActions = (
  status: number | null | undefined
): TaskActionConfig[] => {
  if (status === null || status === undefined) return [];
  const keys = REVERSE_BY_STATUS[status] ?? [];
  return keys.map((k) => TASK_ACTION_CONFIGS[k]);
};

/**
 * 是否应展示「规划路线」入口。
 *
 * 触发条件：
 * - 任务状态 ∈ {待派车/已派车/已装车}（plan_route 接口允许的范围）
 * - 且 (自有车) 必出现；(承运商/社会运力) 仅在尚未规划过路线（segmentCount=0）时出现，作为可选补录
 */
export const shouldShowPlanRoute = (task: {
  status?: number | null;
  carrierType?: number | null;
  segmentCount?: number | null;
}): boolean => {
  const st = task.status ?? -1;
  if (![-1, 0, 1, 2].includes(st)) return false;
  if (task.carrierType === 1) return true;
  return (task.segmentCount ?? 0) === 0;
};
