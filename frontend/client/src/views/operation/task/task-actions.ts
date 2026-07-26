/**
 * 运输任务单 - 语义化动作配置
 *
 * 把"按 status 推进"翻译为"按业务场景命名的动作"，
 * 供台账列表 / 详情抽屉 / 调度工作台共用。
 *
 * 每个 status 在每个时点最多对应 1 个"主动作"。
 */

import type { Component } from 'vue';
import type {
  ButtonDropdownItem,
  ButtonItem
} from 'ele-admin-plus/es/ele-buttons/types';
import {
  ArrowLeft,
  Back,
  Box,
  CircleCheck,
  CircleClose,
  Close,
  DArrowLeft,
  Location,
  MapLocation,
  Promotion,
  RefreshLeft,
  SwitchButton,
  User,
  Van,
  View,
  Wallet,
  Warning
} from '@element-plus/icons-vue';
import { DeleteOutlined, EditOutlined } from '@/components/icons';
import { CARRIER_TYPE, TASK_STATUS } from './status-config';

export type TaskActionKey =
  | 'assign-carrier' // 确认承运分配 (status -1 → 0)
  | 'dispatch' // 派车 (status 0 → 1)
  | 'plan-route' // 规划路线（独立动作，不改 status）
  | 'confirm-load' // 确认装车 (1 → 2)
  | 'depart' // 标记出发 (2 → 3)
  | 'confirm-arrive' // 确认到达 (3 → 4)
  | 'confirm-sign' // 确认签收：item 级签收，全部签收后聚合驱动 task 4→5
  | 'close' // 关闭任务 (5 → 7)
  // —— 逆向通道（参考 02.计划与任务单状态机联动设计.md §4.5）
  | 'revert-dispatch' // 撤回派车 (1 → 0)
  | 'revert-load' // 撤销装车 (2 → 1)
  | 'revert-depart' // 撤回出发 (3 → 2)
  | 'revert-arrive' // 撤回到达 (4 → 3)
  | 'revert-sign' // 撤销签收（5 → 4，item 级 3→2 反向聚合驱动）
  | 'force-cancel' // 强制取消（2/3/4 → 9，线下取消）
  // —— 常规辅助通道
  | 'cancel-task' // 常规取消（-1/0/1/2 → 9，释放计划挂接 + 撤销未支付费用单）
  | 'create-finance' // 新建费用单（快捷发起，按节点配置过滤类型）
  | 'edit' // 编辑任务单（仅 -1/0/1）
  | 'delete'; // 删除任务单（仅 -1/0/9）

export interface TaskActionConfig {
  key: TaskActionKey;
  label: string;
  buttonType: 'primary' | 'success' | 'warning' | 'info' | 'danger';
  permission: string;
  /** 操作列 / 下拉图标 */
  icon: Component;
  /** 需要打开弹窗时填，对应 action-*.vue 组件名 */
  dialog?:
    | 'assign-carrier'
    | 'dispatch'
    | 'plan-route'
    | 'confirm-load'
    | 'confirm-arrive'
    | 'confirm-sign'
    | 'revert'
    | 'revert-sign'
    | 'force-cancel'
    | 'cancel-task';
  /** 是否纯 confirm（不打开弹窗，直接 ElMessageBox.confirm） */
  confirm?: boolean;
  /** 是否需要跳转打开费用单创建（生成结算单） */
  openSettlement?: boolean;
  /** 是否需要打开费用单创建（不预设类型，由节点配置过滤，通常落到预付单） */
  openFinance?: boolean;
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
    icon: User,
    dialog: 'assign-carrier'
  },
  dispatch: {
    key: 'dispatch',
    label: '派车',
    buttonType: 'primary',
    permission: 'operation:task:dispatch',
    icon: Van,
    dialog: 'dispatch'
  },
  'plan-route': {
    key: 'plan-route',
    label: '规划路线',
    buttonType: 'primary',
    permission: 'operation:task:plan-route',
    icon: MapLocation,
    dialog: 'plan-route'
  },
  'confirm-load': {
    key: 'confirm-load',
    label: '确认装车',
    buttonType: 'warning',
    permission: 'operation:task:confirm-load',
    icon: Box,
    dialog: 'confirm-load'
  },
  depart: {
    key: 'depart',
    label: '标记出发',
    buttonType: 'warning',
    permission: 'operation:task:confirm-depart',
    icon: Promotion,
    confirm: true
  },
  'confirm-arrive': {
    key: 'confirm-arrive',
    label: '确认到达',
    buttonType: 'success',
    permission: 'operation:task:confirm-arrive',
    icon: Location,
    dialog: 'confirm-arrive'
  },
  'confirm-sign': {
    key: 'confirm-sign',
    label: '确认签收',
    buttonType: 'success',
    permission: 'operation:task:confirm-sign',
    icon: CircleCheck,
    dialog: 'confirm-sign'
  },
  close: {
    key: 'close',
    label: '关闭任务',
    buttonType: 'info',
    permission: 'operation:task:close',
    icon: SwitchButton,
    confirm: true
  },
  // —— 逆向通道 —— //
  'revert-dispatch': {
    key: 'revert-dispatch',
    label: '撤回派车',
    buttonType: 'warning',
    permission: 'operation:task:revert-dispatch',
    icon: RefreshLeft,
    dialog: 'revert',
    revertFrom: 1,
    revertTo: 0
  },
  'revert-load': {
    key: 'revert-load',
    label: '撤销装车',
    buttonType: 'warning',
    permission: 'operation:task:revert-load',
    icon: DArrowLeft,
    dialog: 'revert',
    revertFrom: 2,
    revertTo: 1
  },
  'revert-depart': {
    key: 'revert-depart',
    label: '撤回出发',
    buttonType: 'warning',
    permission: 'operation:task:revert-depart',
    icon: Back,
    dialog: 'revert',
    revertFrom: 3,
    revertTo: 2
  },
  'revert-arrive': {
    key: 'revert-arrive',
    label: '撤回到达',
    buttonType: 'warning',
    permission: 'operation:task:revert-arrive',
    icon: CircleClose,
    dialog: 'revert',
    revertFrom: 4,
    revertTo: 3
  },
  'revert-sign': {
    key: 'revert-sign',
    label: '撤销签收',
    buttonType: 'warning',
    permission: 'operation:task:revert-sign',
    icon: ArrowLeft,
    dialog: 'revert-sign',
    revertFrom: 5,
    revertTo: 4
  },
  'force-cancel': {
    key: 'force-cancel',
    label: '强制取消',
    buttonType: 'danger',
    permission: 'operation:task:force-cancel',
    icon: Warning,
    dialog: 'force-cancel'
  },
  // —— 常规辅助通道 —— //
  'cancel-task': {
    key: 'cancel-task',
    label: '取消任务',
    buttonType: 'warning',
    permission: 'operation:task:cancel',
    icon: Close,
    dialog: 'cancel-task'
  },
  'create-finance': {
    key: 'create-finance',
    label: '新建费用单',
    buttonType: 'success',
    permission: 'operation:task-finance:add',
    icon: Wallet,
    openFinance: true
  },
  edit: {
    key: 'edit',
    label: '编辑',
    buttonType: 'info',
    permission: 'operation:task:edit',
    icon: EditOutlined
  },
  delete: {
    key: 'delete',
    label: '删除',
    buttonType: 'danger',
    permission: 'operation:task:delete',
    icon: DeleteOutlined,
    confirm: true
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
  [TASK_STATUS.PENDING_ASSIGN]: 'assign-carrier',
  [TASK_STATUS.PENDING_DISPATCH]: 'dispatch',
  [TASK_STATUS.DISPATCHED]: 'confirm-load',
  [TASK_STATUS.LOADED]: 'depart',
  [TASK_STATUS.ON_WAY]: 'confirm-arrive',
  [TASK_STATUS.ARRIVED]: 'confirm-sign',
  [TASK_STATUS.SIGNED]: 'close',
  [TASK_STATUS.CLOSED]: null,
  [TASK_STATUS.CANCELLED]: null
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
 * - 5 → 撤销签收（避免误签收后流程卡死）
 *
 * 说明：5 已签收 由 item 全签收聚合驱动；"撤销签收" 走 item 级
 * （修改对应 item.status 3→2，后端 _aggregate_task_status_from_items
 * 自动把 task 5→4、计划 5→4），不走任务级 revert-status 接口。
 * 已关闭(7)/已取消(9) 为终态，不放开任何逆向。
 */
const REVERSE_BY_STATUS: Record<number, TaskActionKey[]> = {
  [TASK_STATUS.DISPATCHED]: ['revert-dispatch'],
  [TASK_STATUS.LOADED]: ['revert-load', 'force-cancel'],
  [TASK_STATUS.ON_WAY]: ['revert-depart', 'force-cancel'],
  [TASK_STATUS.ARRIVED]: ['revert-arrive', 'force-cancel'],
  [TASK_STATUS.SIGNED]: ['revert-sign']
};

export const getReverseTaskActions = (
  status: number | null | undefined
): TaskActionConfig[] => {
  if (status === null || status === undefined) return [];
  const keys = REVERSE_BY_STATUS[status] ?? [];
  return keys.map((k) => TASK_ACTION_CONFIGS[k]);
};

/**
 * 可就近发起费用单的任务节点（派车后到关闭前；排除待分配/已取消）。
 * 具体在某节点能发起哪类单据，仍由租户「费用单发起节点配置」决定。
 */
export const FINANCE_ENTRY_STATUSES: number[] = [
  TASK_STATUS.PENDING_DISPATCH,
  TASK_STATUS.DISPATCHED,
  TASK_STATUS.LOADED,
  TASK_STATUS.ON_WAY,
  TASK_STATUS.ARRIVED,
  TASK_STATUS.SIGNED,
  TASK_STATUS.CLOSED
];

/** 当前节点是否展示「新建费用单」快捷入口 */
export const shouldShowCreateFinance = (
  status: number | null | undefined
): boolean =>
  status !== null &&
  status !== undefined &&
  FINANCE_ENTRY_STATUSES.includes(status);

/**
 * 行操作聚合：把"详情 + 主按钮 + 更多下拉"所需的全部信息打包给 UI 层。
 *
 * UI 规范：操作列只暴露 2 个按钮（详情 + 主按钮），其余动作（编辑、规划路线、
 * 逆向、取消任务、强制取消、删除）一律收纳到「更多」下拉。
 *
 * 「更多」组装顺序按"修改类 → 流程辅助 → 反向 → 取消 → 删除"递进，保持视觉一致。
 */
export interface TaskRowActions {
  primary: TaskActionConfig | null;
  more: TaskActionConfig[];
}

export const getTaskRowActions = (row: {
  status?: number | null;
  carrierType?: number | null;
  segmentCount?: number | null;
}): TaskRowActions => {
  const primary = getPrimaryTaskAction(row.status ?? null);

  const status = row.status ?? null;
  if (status === null || status === undefined) {
    return { primary, more: [] };
  }

  const more: TaskActionConfig[] = [];

  const canEdit = (
    [
      TASK_STATUS.PENDING_ASSIGN,
      TASK_STATUS.PENDING_DISPATCH,
      TASK_STATUS.DISPATCHED
    ] as number[]
  ).includes(status);
  if (canEdit) more.push(TASK_ACTION_CONFIGS['edit']);

  if (shouldShowPlanRoute(row)) {
    more.push(TASK_ACTION_CONFIGS['plan-route']);
  }

  more.push(...getReverseTaskActions(status));

  // 已装车起已有「强制取消（force-cancel）」专门通道；为避免与常规「取消任务」
  // 在同一行同时出现造成调度员歧义，常规取消仅在 待分配/待派车/已派车 暴露。
  const canCancel = (
    [
      TASK_STATUS.PENDING_ASSIGN,
      TASK_STATUS.PENDING_DISPATCH,
      TASK_STATUS.DISPATCHED
    ] as number[]
  ).includes(status);
  if (canCancel) more.push(TASK_ACTION_CONFIGS['cancel-task']);

  const canDelete = (
    [
      TASK_STATUS.PENDING_ASSIGN,
      TASK_STATUS.PENDING_DISPATCH,
      TASK_STATUS.CANCELLED
    ] as number[]
  ).includes(status);
  if (canDelete) more.push(TASK_ACTION_CONFIGS['delete']);

  return { primary, more };
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
  const st = task.status ?? TASK_STATUS.PENDING_ASSIGN;
  const planRouteStatuses: number[] = [
    TASK_STATUS.PENDING_ASSIGN,
    TASK_STATUS.PENDING_DISPATCH,
    TASK_STATUS.DISPATCHED,
    TASK_STATUS.LOADED
  ];
  if (!planRouteStatuses.includes(st)) return false;
  if (task.carrierType === CARRIER_TYPE.SELF) return true;
  return (task.segmentCount ?? 0) === 0;
};

// ============================================================
// 任务单列表操作列（对齐开发手册 17.列表操作列按钮规范）
// ============================================================

/** 列表专用：详情为只读虚拟项，不进入 TaskActionKey */
export type TaskListActionKey = TaskActionKey | 'detail';

export interface TaskListActionCandidate {
  key: TaskListActionKey;
  title: string;
  icon: Component;
  permission?: string;
  danger?: boolean;
  divided?: boolean;
  /** 业务动作配置；详情为 null */
  action: TaskActionConfig | null;
}

/** 规划路线追加「·未规划」尾巴 */
export const resolveTaskActionTitle = (
  row: { segmentCount?: number | null },
  act: TaskActionConfig
): string => {
  if (act.key === 'plan-route' && (row.segmentCount ?? 0) === 0) {
    return `${act.label}·未规划`;
  }
  return act.label;
};

/**
 * 列表行候选动作（配置顺序）：
 * 主动作 → 详情 → 编辑 → 规划路线 → 新建费用单 → 逆向 → 取消 → 删除
 */
export const collectTaskListActions = (row: {
  status?: number | null;
  carrierType?: number | null;
  segmentCount?: number | null;
}): TaskListActionCandidate[] => {
  const { primary, more } = getTaskRowActions(row);
  const items: TaskListActionCandidate[] = [];

  const pushAct = (act: TaskActionConfig) => {
    items.push({
      key: act.key,
      title: resolveTaskActionTitle(row, act),
      icon: act.icon,
      permission: act.permission,
      danger: act.key === 'delete' || act.key === 'force-cancel',
      divided: act.key === 'delete',
      action: act
    });
  };

  if (primary) pushAct(primary);

  items.push({
    key: 'detail',
    title: '详情',
    icon: View,
    action: null
  });

  const edit = more.find((a) => a.key === 'edit');
  const planRoute = more.find((a) => a.key === 'plan-route');
  const rest = more.filter((a) => a.key !== 'edit' && a.key !== 'plan-route');

  if (edit) pushAct(edit);
  if (planRoute) pushAct(planRoute);
  if (shouldShowCreateFinance(row.status)) {
    pushAct(TASK_ACTION_CONFIGS['create-finance']);
  }
  for (const act of rest) pushAct(act);

  return items;
};

export interface BuildTaskListActionItemsContext {
  hasPermission: (code: string) => boolean;
  onDetail: () => void;
  onAction: (act: TaskActionConfig) => void;
}

/** 槽位算法：可见 ≤2 平铺；≥3 为首项 + 更多（更多悬停展开） */
export const buildTaskListActionItems = (
  row: {
    status?: number | null;
    carrierType?: number | null;
    segmentCount?: number | null;
  },
  ctx: BuildTaskListActionItemsContext
): ButtonItem[] => {
  const visible: ButtonDropdownItem[] = [];
  for (const c of collectTaskListActions(row)) {
    if (c.permission && !ctx.hasPermission(c.permission)) continue;
    visible.push({
      title: c.title,
      icon: c.icon,
      permission: c.permission,
      danger: c.danger,
      divided: c.divided,
      onClick: () => {
        if (c.key === 'detail' || !c.action) {
          ctx.onDetail();
          return;
        }
        ctx.onAction(c.action);
      }
    });
  }

  if (visible.length === 0) return [];
  if (visible.length <= 2) {
    return visible.map((it) => ({
      ...it,
      type: 'link' as const
    })) as ButtonItem[];
  }
  const [primary, ...rest] = visible;
  return [
    { ...primary!, type: 'link' as const },
    { preset: 'more' as const, dropdownItems: rest }
  ] as ButtonItem[];
};

/** 带图标的 link 占用宽度（偏保守，避免裁切「更多」箭头） */
function estimateActionLinkWidth(title: string): number {
  return 20 + title.length * 14 + 12;
}

/**
 * 操作列 minWidth：按「过滤前最坏外显」估算。
 * 最坏：四字主动作（分配承运/确认装车…）+「更多」；或「规划路线·未规划」平铺场景。
 */
export function resolveTaskListActionColumnMinWidth(): number {
  const pad = 28;
  const divider = 17;
  const moreW = 68;
  // 最长外显文案：规划路线·未规划（7）出现在更多内；外显首项最长为四字
  const primaryW = estimateActionLinkWidth('分配承运');
  return primaryW + divider + moreW + pad;
}
