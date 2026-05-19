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
  | 'confirm-sign' // 确认签收 (4 → 5)
  | 'create-settlement' // 生成最终结算单（不直接改 task.status，结算单已支付后由后端推进到 6）
  | 'close' // 关闭任务 (5/6 → 7)
  // —— 逆向通道（参考 02.运单与任务单状态机联动设计.md §4.5）
  | 'revert-load' // 撤销装车 (2 → 1)
  | 'revert-depart' // 撤回出发 (3 → 2)
  | 'revert-arrive' // 撤回到达 (4 → 3)
  | 'revert-sign' // 撤销签收 (5 → 4)
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
  'create-settlement': {
    key: 'create-settlement',
    label: '生成结算单',
    buttonType: 'success',
    permission: 'operation:task-finance:add',
    openSettlement: true
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
  'revert-sign': {
    key: 'revert-sign',
    label: '撤销签收',
    buttonType: 'warning',
    permission: 'operation:task:revert-sign',
    dialog: 'revert',
    revertFrom: 5,
    revertTo: 4
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
 * - 5 (已签收)：默认主动作是「生成结算单」（财务关心）；
 *   关闭任务作为兜底动作放到下拉/列表的次要位置（caller 自己处理）。
 * - 6 (已结算)：主动作是「关闭任务」。
 * - -1,0,1,2,3,4：分别对应分配承运 / 派车 / 装车 / 出发 / 到达 / 签收。
 * - 7,9：无主动作。
 */
const PRIMARY_BY_STATUS: Record<number, TaskActionKey | null> = {
  [-1]: 'assign-carrier',
  0: 'dispatch',
  1: 'confirm-load',
  2: 'depart',
  3: 'confirm-arrive',
  4: 'confirm-sign',
  5: 'create-settlement',
  6: 'close',
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
 * 部分状态除主动作外，还有次要动作（如 5 已签收 既能生成结算单也能直接关闭）。
 * 返回不含主动作的次要动作列表。
 */
export const getSecondaryTaskActions = (
  status: number | null | undefined
): TaskActionConfig[] => {
  if (status === null || status === undefined) return [];
  if (status === 5) return [TASK_ACTION_CONFIGS.close];
  return [];
};

/**
 * 当前状态可用的逆向动作（撤销/强制取消）。
 *
 * 与 §4.5 反向跳转矩阵一致：
 * - 1 → 撤销装车（1→0 在主动作里走"撤回派车"，此处不重复）
 * - 2 → 撤销装车
 * - 3 → 撤回出发；强制取消
 * - 4 → 撤回到达；强制取消
 * - 5 → 撤销签收（撤销结算单走财务侧）
 */
const REVERSE_BY_STATUS: Record<number, TaskActionKey[]> = {
  2: ['revert-load', 'force-cancel'],
  3: ['revert-depart', 'force-cancel'],
  4: ['revert-arrive', 'force-cancel'],
  5: ['revert-sign']
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
