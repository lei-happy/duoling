/**
 * 驾驶员资金账户（往来账）H5 端枚举与展示映射
 *
 * 口径与企业端 client 及需求文档 §3.3 保持一致，避免两端 bizType 文案分叉。
 */

/** 资金流水业务类型（biz_type） */
export const FUND_BIZ_TYPE = {
  PREPAY_REGISTER: 1,
  PREPAY_REVERSE: 2,
  MANUAL_IN: 3,
  MANUAL_OUT: 4,
  ADJUST: 5,
  TASK_DEDUCT: 6,
  TASK_SETTLE_IN: 7
} as const;

export const FUND_BIZ_TYPE_LABELS: Record<number, string> = {
  [FUND_BIZ_TYPE.PREPAY_REGISTER]: '预付登记',
  [FUND_BIZ_TYPE.PREPAY_REVERSE]: '退款入账',
  [FUND_BIZ_TYPE.MANUAL_IN]: '人工入账',
  [FUND_BIZ_TYPE.MANUAL_OUT]: '人工出账',
  [FUND_BIZ_TYPE.ADJUST]: '人工调整',
  [FUND_BIZ_TYPE.TASK_DEDUCT]: '任务抵扣',
  [FUND_BIZ_TYPE.TASK_SETTLE_IN]: '任务结算入账'
};

export function fundBizTypeLabel(v?: number): string {
  return v != null ? (FUND_BIZ_TYPE_LABELS[v] ?? '其他') : '其他';
}

/** 账户状态 */
export const FUND_ACCOUNT_STATUS = {
  NORMAL: 1,
  FROZEN: 0
} as const;
