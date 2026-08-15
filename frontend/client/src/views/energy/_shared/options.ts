export const ENERGY_TYPES = [
  { value: 'OIL', label: '油品', unit: 'L' },
  { value: 'GAS', label: '燃气', unit: 'kg' },
  { value: 'ELECTRIC', label: '电力', unit: 'kWh' },
  { value: 'OTHER', label: '其他', unit: '' }
];

export const SUPPLIER_TYPES = [
  { value: 1, label: '石油石化' },
  { value: 2, label: '燃气' },
  { value: 3, label: '充电' },
  { value: 4, label: '能源平台' },
  { value: 5, label: '民营油站' },
  { value: 9, label: '其他' }
];

export const ACCOUNT_TYPES = [
  { value: 'PREPAID', label: '预付账户' },
  { value: 'POSTPAID', label: '后付/月结' },
  { value: 'CREDIT', label: '授信账户' },
  { value: 'CARD_POOL', label: '卡资金池' },
  { value: 'VIRTUAL', label: '虚拟账户' }
];

export const CARD_TYPES = [
  { value: '实体卡', label: '实体卡' },
  { value: '虚拟卡', label: '虚拟卡' }
];

export const CARD_STATUSES = [
  { value: 5, label: '未激活' },
  { value: 1, label: '正常' },
  { value: 2, label: '冻结' },
  { value: 4, label: '挂失' },
  { value: 0, label: '停用' },
  { value: 3, label: '已注销' }
];

export const ACCOUNT_STATUSES = [
  { value: 1, label: '正常' },
  { value: 2, label: '冻结' },
  { value: 0, label: '停用' },
  { value: 3, label: '已关闭' }
];

export const SOURCE_CHANNELS = [
  { value: 1, label: '供应商直连' },
  { value: 2, label: 'Excel 导入' },
  { value: 3, label: '手工录入' },
  { value: 4, label: '司机垫付（仅台账）' },
  { value: 5, label: '月结账单' }
];

export const MATCH_STATUSES = [
  { value: 'MATCHED', label: '已匹配' },
  { value: 'PARTIAL', label: '部分匹配' },
  { value: 'UNMATCHED', label: '未匹配' },
  { value: 'CONFLICT', label: '冲突' }
];

export const RECHARGE_STATUSES: Record<number, string> = {
  0: '草稿',
  1: '待审批',
  2: '已审批',
  3: '已入账',
  4: '已撤销',
  5: '已结清'
};

export const RECHARGE_STATUS_OPTIONS = Object.entries(RECHARGE_STATUSES).map(
  ([value, label]) => ({ value: Number(value), label })
);

export const RECON_DOC_STATUSES = [
  { value: 0, label: '待核销' },
  { value: 5, label: '已核销' }
];

export const EXCEPTION_STATUSES = [
  { value: 'pending', label: '待处理' },
  { value: 'processed', label: '已处理' },
  { value: 'ignored', label: '已忽略' }
];

export const SYNC_MODES = [
  { value: 'manual', label: '手工' },
  { value: 'cron', label: '定时' },
  { value: 'interval', label: '间隔拉取' }
];

export const CONNECTOR_CODES = [
  { value: 'excel', label: 'Excel 账单导入' },
  { value: 'manual', label: '手工录入' },
  { value: 'http_api', label: 'HTTP 对接' }
];

export const RISK_LEVELS = [
  { value: 'LOW', label: '低' },
  { value: 'MEDIUM', label: '中' },
  { value: 'HIGH', label: '高' }
];

export const RECON_RESULTS: Record<string, string> = {
  MATCHED: '已匹配',
  MISSING_INTERNAL: '系统缺失',
  MISSING_EXTERNAL: '账单缺失',
  AMOUNT_DIFF: '金额不符',
  QTY_DIFF: '数量不符',
  DUPLICATED: '重复'
};

export const RECON_PROCESS: Record<string, string> = {
  pending: '待处理',
  confirmed: '已确认',
  ignored: '已忽略'
};

export const EXCEPTION_TYPES: Record<string, string> = {
  OVER_TANK: '超油箱容量',
  REPEAT_FILL: '短时间重复加注',
  ABNORMAL_PRICE: '异常单价',
  ABNORMAL_CONSUMPTION: '异常油耗',
  UNBOUND_VEHICLE: '未匹配车辆',
  UNBOUND_DRIVER: '未匹配司机'
};

export function labelOf(
  options: Array<{ value: string | number; label: string }>,
  value: string | number | undefined
) {
  return options.find((o) => o.value === value)?.label ?? (value ?? '-');
}

export function asPage<T>(res: any): { list: T[]; count: number } {
  return {
    list: res?.list ?? [],
    count: Number(res?.count ?? res?.total ?? 0)
  };
}

export function formatMoney(n: unknown, digits = 2) {
  const v = Number(n);
  if (Number.isNaN(v)) return '-';
  return v.toLocaleString('zh-CN', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  });
}
