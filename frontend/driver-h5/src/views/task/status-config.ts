/**
 * 任务状态配置（与后端 task.status 一致）
 *
 * -1 待分配 → 0 待派车 → 1 已派车 → 2 已装车 → 3 在途 → 4 已到达
 *                                                          → 5 已签收（聚合态）→ 7 已关闭
 *                                                                               9 已取消
 *
 * v2：5 由聚合驱动（不接受 4→5 外部推进）；6 已结算枚举已下线
 */

type TagLevel = 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';

export interface TaskStatusInfo {
  label: string;
  level: TagLevel;
}

const STATUS_MAP: Record<number, TaskStatusInfo> = {
  [-1]: { label: '待分配', level: 'default' },
  0: { label: '待派车', level: 'warning' },
  1: { label: '已派车', level: 'primary' },
  2: { label: '已装车', level: 'primary' },
  3: { label: '在途', level: 'info' },
  4: { label: '已到达', level: 'info' },
  5: { label: '已签收', level: 'success' },
  7: { label: '已关闭', level: 'default' },
  9: { label: '已取消', level: 'danger' }
};

export function getTaskStatusInfo(status: number): TaskStatusInfo {
  return STATUS_MAP[status] ?? { label: '未知', level: 'default' };
}

/** 司机端可见的任务状态（无 -1/0 待分配 / 待派车，因为还没派给驾驶员） */
export const VISIBLE_STATUS_TABS: { label: string; value?: number }[] = [
  { label: '全部' },
  { label: '待装车', value: 1 },
  { label: '已装车', value: 2 },
  { label: '在途', value: 3 },
  { label: '已到达', value: 4 },
  { label: '已签收', value: 5 }
];

/** 司机端 item 状态 */
const ITEM_STATUS_MAP: Record<number, TaskStatusInfo> = {
  0: { label: '待装车', level: 'warning' },
  1: { label: '已装车', level: 'primary' },
  2: { label: '已卸车', level: 'info' },
  3: { label: '已签收', level: 'success' }
};

export function getItemStatusInfo(status: number): TaskStatusInfo {
  return ITEM_STATUS_MAP[status] ?? { label: '未知', level: 'default' };
}

/** 当前状态下可执行的司机动作 */
export interface DriverAction {
  key: 'confirm-load' | 'depart' | 'confirm-arrive' | 'sign-items';
  label: string;
  level?: 'primary' | 'success' | 'warning' | 'danger';
}

export function getAvailableActions(status: number): DriverAction[] {
  switch (status) {
    case 1:
      return [{ key: 'confirm-load', label: '确认装车', level: 'primary' }];
    case 2:
      return [{ key: 'depart', label: '确认出发', level: 'primary' }];
    case 3:
      return [{ key: 'confirm-arrive', label: '确认到达', level: 'primary' }];
    case 4:
      return [{ key: 'sign-items', label: '逐单签收', level: 'success' }];
    default:
      return [];
  }
}

/** 财务状态 */
export const FINANCE_DOC_TYPE: Record<number, string> = {
  1: '预付单',
  2: '补款单',
  3: '结算单'
};

export const FINANCE_STATUS: Record<number, TaskStatusInfo> = {
  0: { label: '草稿', level: 'default' },
  1: { label: '待审批', level: 'warning' },
  2: { label: '已审批', level: 'info' },
  3: { label: '已支付', level: 'success' },
  4: { label: '已撤销', level: 'default' }
};

export const PAY_METHOD: Record<number, string> = {
  1: '银行转账',
  2: '油卡',
  3: '油气款',
  4: '现金',
  5: '微信',
  6: '支付宝'
};
