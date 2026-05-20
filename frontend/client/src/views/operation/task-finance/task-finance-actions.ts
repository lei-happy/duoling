/**
 * 任务单财务费用单 - 语义化动作配置
 *
 * 给定费用单 status，返回当前唯一的「主动作」按钮。
 * 状态机：0 草稿 → 1 待审批 → 2 已审批 → 3 已支付；0/1/2 → 4 已撤销
 */

export type FinanceActionKey =
  | 'submit' // 提交审批 (0 → 1)
  | 'approve' // 审批通过 (1 → 2)
  | 'pay' // 标记已支付 (2 → 3)
  | 'cancel' // 撤销 (0/1/2 → 4)
  | 'edit'; // 编辑（仅 0/1，主动作纯打开编辑视图）

export interface FinanceActionConfig {
  key: FinanceActionKey;
  label: string;
  buttonType: 'primary' | 'success' | 'warning' | 'info' | 'danger';
  permission: string;
  /** 是否需要打开 action-pay 弹窗（仅 pay 用到） */
  dialog?: 'pay';
  /** 是否纯 confirm（如审批通过 / 提交审批 / 撤销） */
  confirm?: boolean;
}

export const FIN_ACTION_CONFIGS: Record<FinanceActionKey, FinanceActionConfig> =
  {
    submit: {
      key: 'submit',
      label: '提交审批',
      buttonType: 'warning',
      permission: 'operation:task-finance:submit',
      confirm: true
    },
    approve: {
      key: 'approve',
      label: '审批通过',
      buttonType: 'primary',
      permission: 'operation:task-finance:approve',
      confirm: true
    },
    pay: {
      key: 'pay',
      label: '标记已支付',
      buttonType: 'success',
      permission: 'operation:task-finance:pay',
      dialog: 'pay'
    },
    cancel: {
      key: 'cancel',
      label: '撤销',
      buttonType: 'danger',
      permission: 'operation:task-finance:cancel',
      confirm: true
    },
    edit: {
      key: 'edit',
      label: '编辑',
      buttonType: 'primary',
      permission: 'operation:task-finance:add'
    }
  };

const PRIMARY_BY_STATUS: Record<number, FinanceActionKey | null> = {
  0: 'submit',
  1: 'approve',
  2: 'pay',
  3: null,
  4: null
};

export const getPrimaryFinanceAction = (
  status: number | null | undefined
): FinanceActionConfig | null => {
  if (status === null || status === undefined) return null;
  const k = PRIMARY_BY_STATUS[status];
  return k ? FIN_ACTION_CONFIGS[k] : null;
};

/** 主动作之外允许的次要动作（用于详情页底部按钮区域） */
export const getSecondaryFinanceActions = (
  status: number | null | undefined
): FinanceActionConfig[] => {
  if (status === null || status === undefined) return [];
  // 0/1/2 都允许撤销
  if (status === 0 || status === 1 || status === 2) {
    return [FIN_ACTION_CONFIGS.cancel];
  }
  return [];
};
