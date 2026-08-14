/**
 * 财务单据的状态与枚举字典
 *
 * 状态码与文案跟后端 `finance_state_machine` 一一对应：同一个状态码在不同单据上
 * 说法不同（3 在对账单上是「已结清」、在结算单上是「已收款」），因此按单据分开列，
 * 不做一份"通用"字典。
 *
 * 列表接口都会返回 `statusLabel`，页面优先用它；这里的 MAP 主要给筛选下拉与
 * 标签颜色用。
 */

export interface StatusOption {
  value: number;
  label: string;
  type: string;
}

const toMap = (options: readonly StatusOption[]) =>
  options.reduce<Record<number, { label: string; type: string }>>((acc, o) => {
    acc[o.value] = { label: o.label, type: o.type };
    return acc;
  }, {});

/** 客户对账单：无审批环节，草稿直接确认 */
export const RECON_STATUS_OPTIONS: readonly StatusOption[] = [
  { value: 0, label: '草稿', type: 'info' },
  { value: 2, label: '已确认', type: 'primary' },
  { value: 3, label: '已结清', type: 'success' },
  { value: 4, label: '已撤销', type: 'danger' }
];

export const RECON_STATUS_MAP = toMap(RECON_STATUS_OPTIONS);

/** 客户结算单：走审批，收款后进入已收款 */
export const SETTLE_STATUS_OPTIONS: readonly StatusOption[] = [
  { value: 0, label: '草稿', type: 'info' },
  { value: 1, label: '待审批', type: 'warning' },
  { value: 2, label: '已审批', type: 'primary' },
  { value: 3, label: '已收款', type: 'success' },
  { value: 4, label: '已撤销', type: 'danger' }
];

export const SETTLE_STATUS_MAP = toMap(SETTLE_STATUS_OPTIONS);

/** 承运商对账单：与客户对账单同构，也没有审批环节 */
export const CARRIER_RECON_STATUS_OPTIONS: readonly StatusOption[] = [
  { value: 0, label: '草稿', type: 'info' },
  { value: 2, label: '已确认', type: 'primary' },
  { value: 3, label: '已结清', type: 'success' },
  { value: 4, label: '已撤销', type: 'danger' }
];

export const CARRIER_RECON_STATUS_MAP = toMap(CARRIER_RECON_STATUS_OPTIONS);

/** 承运商结算单：走审批，付款后进入已支付 */
export const CARRIER_SETTLE_STATUS_OPTIONS: readonly StatusOption[] = [
  { value: 0, label: '草稿', type: 'info' },
  { value: 1, label: '待审批', type: 'warning' },
  { value: 2, label: '已审批', type: 'primary' },
  { value: 3, label: '已支付', type: 'success' },
  { value: 4, label: '已撤销', type: 'danger' }
];

export const CARRIER_SETTLE_STATUS_MAP = toMap(CARRIER_SETTLE_STATUS_OPTIONS);

/** 司机工资单：走审批，发放后进入已发放 */
export const PAYROLL_STATUS_OPTIONS: readonly StatusOption[] = [
  { value: 0, label: '草稿', type: 'info' },
  { value: 1, label: '待审批', type: 'warning' },
  { value: 2, label: '已审批', type: 'primary' },
  { value: 3, label: '已发放', type: 'success' },
  { value: 4, label: '已撤销', type: 'danger' }
];

export const PAYROLL_STATUS_MAP = toMap(PAYROLL_STATUS_OPTIONS);

/** 进项发票：核销进度即状态，作废是终态 */
export const VENDOR_INVOICE_STATUS_OPTIONS: readonly StatusOption[] = [
  { value: 0, label: '草稿', type: 'info' },
  { value: 3, label: '已收票', type: 'primary' },
  { value: 6, label: '部分核销', type: 'warning' },
  { value: 5, label: '已核销', type: 'success' },
  { value: 4, label: '已撤销', type: 'danger' },
  { value: 9, label: '已作废', type: 'danger' }
];

export const VENDOR_INVOICE_STATUS_MAP = toMap(VENDOR_INVOICE_STATUS_OPTIONS);

/** 销项发票：开票是主动动作，作废与红冲都是终态 */
export const CUSTOMER_INVOICE_STATUS_OPTIONS: readonly StatusOption[] = [
  { value: 0, label: '草稿', type: 'info' },
  { value: 1, label: '待审批', type: 'warning' },
  { value: 3, label: '已开票', type: 'success' },
  { value: 4, label: '已撤销', type: 'danger' },
  { value: 9, label: '已作废', type: 'danger' }
];

export const CUSTOMER_INVOICE_STATUS_MAP = toMap(
  CUSTOMER_INVOICE_STATUS_OPTIONS
);

/** 打款批次：6 是部分失败，需要出纳补做失败笔 */
export const PAYMENT_BATCH_STATUS_OPTIONS: readonly StatusOption[] = [
  { value: 0, label: '草稿', type: 'info' },
  { value: 1, label: '待审批', type: 'warning' },
  { value: 2, label: '待执行', type: 'primary' },
  { value: 6, label: '部分失败', type: 'warning' },
  { value: 3, label: '已执行', type: 'success' },
  { value: 4, label: '已撤销', type: 'danger' }
];

export const PAYMENT_BATCH_STATUS_MAP = toMap(PAYMENT_BATCH_STATUS_OPTIONS);

/** 批次内单笔的执行结果 */
export const BATCH_EXEC_STATUS_MAP: Record<
  number,
  { label: string; type: string }
> = {
  0: { label: '待执行', type: 'info' },
  1: { label: '成功', type: 'success' },
  2: { label: '失败', type: 'danger' }
};

/** 应付单大类（打款批次的来源单据） */
export const PAYABLE_DOC_KIND_OPTIONS = [
  { value: 'carrier_settle', label: '承运商结算单' },
  { value: 'driver_payroll', label: '司机工资单' },
  { value: 'task_finance', label: '任务费用单' }
] as const;

/** 银行账户类型 */
export const BANK_ACCOUNT_TYPE_OPTIONS = [
  { value: 1, label: '基本户' },
  { value: 2, label: '一般户' },
  { value: 3, label: '专用户' },
  { value: 4, label: '其他' }
] as const;

/** 银行账户用途 */
export const ACCOUNT_USAGE_SCOPE_OPTIONS = [
  { value: 1, label: '收付通用' },
  { value: 2, label: '仅收款' },
  { value: 3, label: '仅付款' }
] as const;

/** 资金流水方向 */
export const FLOW_DIRECTION_OPTIONS = [
  { value: 1, label: '收款' },
  { value: 2, label: '付款' }
] as const;

/** 经营核算维度：与后端 accounting_constants.DIMENSIONS 一致 */
export const ACCOUNTING_DIMENSION_OPTIONS = [
  { value: 'customer', label: '客户' },
  { value: 'entity', label: '经营主体' },
  { value: 'route', label: '线路' },
  { value: 'vehicle', label: '车辆' },
  { value: 'driver', label: '司机' },
  { value: 'carrier_type', label: '承运类型' }
] as const;

/** 工资模式 */
export const PAYROLL_MODEL_OPTIONS = [
  { value: 1, label: '月薪固定' },
  { value: 2, label: '计件提成' },
  { value: 3, label: '底薪加提成' }
] as const;

/** 工资周期 */
export const PAYROLL_PERIOD_OPTIONS = [
  { value: 1, label: '月薪' },
  { value: 2, label: '周薪' },
  { value: 3, label: '趟薪' }
] as const;

/** 工资项分类：决定加减方向 */
export const PAYROLL_ITEM_CATEGORY_OPTIONS: readonly StatusOption[] = [
  { value: 1, label: '应发项', type: 'success' },
  { value: 2, label: '扣减项', type: 'danger' },
  { value: 3, label: '抵账项', type: 'warning' }
];

export const PAYROLL_ITEM_CATEGORY_MAP = toMap(PAYROLL_ITEM_CATEGORY_OPTIONS);

/** 常用工资项（选了就带默认名称与分类，也允许自定义） */
export const PAYROLL_ITEM_PRESETS = [
  { itemType: 'base_salary', itemName: '底薪', category: 1 },
  { itemType: 'attendance_bonus', itemName: '出勤奖', category: 1 },
  { itemType: 'safety_bonus', itemName: '安全奖', category: 1 },
  { itemType: 'subsidy', itemName: '补贴', category: 1 },
  { itemType: 'social_insurance', itemName: '社保代扣', category: 2 },
  { itemType: 'accident_deduction', itemName: '事故扣款', category: 2 },
  { itemType: 'fine_deduction', itemName: '违章罚款', category: 2 },
  { itemType: 'other_deduction', itemName: '其他扣款', category: 2 },
  { itemType: 'oil_card_offset', itemName: '油卡抵扣', category: 3 },
  { itemType: 'borrow_offset', itemName: '借款抵扣', category: 3 }
] as const;

/** 发票类型 */
export const INVOICE_TYPE_OPTIONS = [
  { value: 1, label: '增值税普通发票' },
  { value: 2, label: '增值税专用发票' },
  { value: 3, label: '电子普通发票' },
  { value: 4, label: '电子专用发票' },
  { value: 5, label: '其他' }
] as const;

/** 进项票供应商类型 */
export const VENDOR_TYPE_OPTIONS = [
  { value: 1, label: '承运商' },
  { value: 2, label: '社会运力' },
  { value: 3, label: '其他供应商' }
] as const;

/** 发票验真状态 */
export const VERIFY_STATUS_MAP: Record<
  number,
  { label: string; type: string }
> = {
  0: { label: '未验真', type: 'info' },
  1: { label: '已验真', type: 'success' },
  2: { label: '验真不符', type: 'danger' }
};

/** 付款方式（应付侧，与后端 PayMethod 一致） */
export const PAY_METHOD_OPTIONS = [
  { value: 1, label: '银行转账' },
  { value: 2, label: '油卡' },
  { value: 3, label: '油气款' },
  { value: 4, label: '现金' },
  { value: 5, label: '微信' },
  { value: 6, label: '支付宝' }
] as const;

/** 计费基础（对账行金额的推导口径） */
export const BILLING_BASE_OPTIONS = [
  { value: 1, label: '按台' },
  { value: 2, label: '按吨' },
  { value: 3, label: '按趟' },
  { value: 4, label: '固定金额' }
] as const;

/** 收款方式 */
export const RECEIVE_METHOD_OPTIONS = [
  { value: 1, label: '银行转账' },
  { value: 2, label: '现金' },
  { value: 3, label: '支票' },
  { value: 4, label: '承兑汇票' },
  { value: 5, label: '平台代收' }
] as const;

/** 差异处置动作（对账工作台与详情页共用） */
export const DIFF_RESOLVE_OPTIONS = [
  { value: 1, label: '已回灌' },
  { value: 2, label: '已协商确认' },
  { value: 3, label: '已强制放行' },
  { value: 4, label: '已失效' }
] as const;

/** 手工登记差异的类型 */
export const DIFF_TYPE_OPTIONS = [
  { value: 1, label: '漏挂' },
  { value: 2, label: '重挂' },
  { value: 3, label: '资格不符' },
  { value: 4, label: '台数不符' },
  { value: 5, label: '里程不符' },
  { value: 6, label: '金额不符' },
  { value: 7, label: '扣减不符' },
  { value: 8, label: '状态回退' }
] as const;

/** 信用状态 */
export const CREDIT_STATUS_OPTIONS: readonly StatusOption[] = [
  { value: 0, label: '已停用', type: 'danger' },
  { value: 1, label: '正常', type: 'success' },
  { value: 2, label: '受限', type: 'warning' }
];

export const CREDIT_STATUS_MAP = toMap(CREDIT_STATUS_OPTIONS);

/** 预警等级：任何等级都只提示、不阻断 */
export const ALERT_LEVEL_MAP: Record<number, { label: string; type: string }> =
  {
    0: { label: '正常', type: 'success' },
    1: { label: '提醒', type: 'info' },
    2: { label: '警示', type: 'warning' },
    3: { label: '高危', type: 'danger' }
  };

/**
 * 单据审计事件类型（与后端 `FinanceEventType` 号段一致）
 *
 * 号段由 `00.模块总览` §6.3 统一分配，这里只做展示翻译。
 */
export const EVENT_TYPE_LABELS: Record<number, string> = {
  1: '创建',
  2: '提交审批',
  3: '审批通过',
  4: '审批驳回',
  5: '退回草稿',
  6: '收付款',
  7: '撤销收付款',
  8: '撤销',
  9: '强制撤销',
  10: '核销',
  11: '锁定',
  12: '解锁',
  13: '开票',
  14: '作废',
  15: '红冲',
  16: '金额调整',
  17: '登记差异',
  18: '关闭差异',
  19: '强制确认',
  20: '回灌重算',
  21: '批量打款',
  22: '到账认领',
  23: '核销冲销',
  24: '进项票登记',
  25: '票款核对',
  26: '信用预警',
  27: '余额校准',
  28: '打款失败'
};

/** 金额展示：空值给占位符，避免表格里出现 0 与"没有"混淆 */
export function formatMoney(v?: number | null, emptyText = '--'): string {
  if (v === null || v === undefined || Number.isNaN(Number(v)))
    return emptyText;
  return Number(v).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

/** 数量展示：整数不带小数尾巴 */
export function formatQuantity(v?: number | null): string {
  if (v === null || v === undefined) return '--';
  const n = Number(v);
  return Number.isInteger(n) ? String(n) : n.toFixed(2);
}
