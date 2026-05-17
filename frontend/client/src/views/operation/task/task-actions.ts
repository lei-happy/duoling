/**
 * 运输任务单 - 语义化动作配置
 *
 * 把"按 status 推进"翻译为"按业务场景命名的动作"，
 * 供台账列表 / 详情抽屉 / 调度工作台共用。
 *
 * 每个 status 在每个时点最多对应 1 个"主动作"。
 */

export type TaskActionKey =
  | 'dispatch' // 派车 (status 0 → 1)
  | 'confirm-load' // 确认装车 (1 → 2)
  | 'depart' // 标记出发 (2 → 3)
  | 'confirm-arrive' // 确认到达 (3 → 4)
  | 'confirm-sign' // 确认签收 (4 → 5)
  | 'create-settlement' // 生成最终结算单（不直接改 task.status，结算单已支付后由后端推进到 6）
  | 'close'; // 关闭任务 (5/6 → 7)

export interface TaskActionConfig {
  key: TaskActionKey;
  label: string;
  buttonType: 'primary' | 'success' | 'warning' | 'info' | 'danger';
  permission: string;
  /** 需要打开弹窗时填，对应 action-*.vue 组件名 */
  dialog?: 'dispatch' | 'confirm-load' | 'confirm-arrive' | 'confirm-sign';
  /** 是否纯 confirm（不打开弹窗，直接 ElMessageBox.confirm） */
  confirm?: boolean;
  /** 是否需要跳转打开费用单创建（生成结算单） */
  openSettlement?: boolean;
}

export const TASK_ACTION_CONFIGS: Record<TaskActionKey, TaskActionConfig> = {
  dispatch: {
    key: 'dispatch',
    label: '派车',
    buttonType: 'primary',
    permission: 'operation:task:dispatch',
    dialog: 'dispatch'
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
  }
};

/**
 * 根据 status 取下一步主动作。
 * - 5 (已签收)：默认主动作是「生成结算单」（财务关心）；
 *   关闭任务作为兜底动作放到下拉/列表的次要位置（caller 自己处理）。
 * - 6 (已结算)：主动作是「关闭任务」。
 * - 0,1,2,3,4：分别对应派车 / 装车 / 出发 / 到达 / 签收。
 * - 7,9：无主动作。
 */
const PRIMARY_BY_STATUS: Record<number, TaskActionKey | null> = {
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
