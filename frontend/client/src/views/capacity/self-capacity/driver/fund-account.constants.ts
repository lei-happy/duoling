/**
 * 驾驶员资金账户（往来账）前端枚举与展示映射
 *
 * 与后端 driver_fund_account_service.py 常量、需求文档 §3.3 保持一致，
 * 避免业务码（bizType / 方向 / 状态 / 符号规则）在组件里散落硬编码。
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

/** 业务类型展示文案（覆盖 1~7，含二期系统联动类型） */
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
  return v != null ? (FUND_BIZ_TYPE_LABELS[v] ?? String(v)) : '—';
}

/** 企业端可手工记账的类型（第 1 期开放 1~5） */
export const MANUAL_BIZ_TYPES: number[] = [
  FUND_BIZ_TYPE.PREPAY_REGISTER,
  FUND_BIZ_TYPE.PREPAY_REVERSE,
  FUND_BIZ_TYPE.MANUAL_IN,
  FUND_BIZ_TYPE.MANUAL_OUT,
  FUND_BIZ_TYPE.ADJUST
];

export const MANUAL_BIZ_TYPE_OPTIONS = MANUAL_BIZ_TYPES.map((value) => ({
  value,
  label: FUND_BIZ_TYPE_LABELS[value]
}));

/** 账户状态 */
export const FUND_ACCOUNT_STATUS = {
  NORMAL: 1,
  FROZEN: 0
} as const;

/** 流水方向 */
export const FUND_DIRECTION = {
  IN: 1,
  OUT: 2
} as const;

/** 人工调整强制备注最小长度（对齐后端 MANUAL_REMARK_MIN_LEN） */
export const MANUAL_REMARK_MIN_LEN = 5;

/**
 * 手工业务类型 → 余额变动符号（与后端 _MANUAL_BIZ_SIGN 对齐）。
 * ADJUST（人工调整）不在此表，其符号由用户所选方向决定。
 */
export const MANUAL_BIZ_SIGN: Record<number, number> = {
  [FUND_BIZ_TYPE.PREPAY_REGISTER]: -1,
  [FUND_BIZ_TYPE.PREPAY_REVERSE]: 1,
  [FUND_BIZ_TYPE.MANUAL_IN]: 1,
  [FUND_BIZ_TYPE.MANUAL_OUT]: -1
};

/**
 * 记账预览符号：ADJUST 由方向决定，其余查符号表。
 */
export function resolveManualSign(bizType: number, direction?: number): number {
  if (bizType === FUND_BIZ_TYPE.ADJUST) {
    return direction === FUND_DIRECTION.IN ? 1 : -1;
  }
  return MANUAL_BIZ_SIGN[bizType] ?? -1;
}
