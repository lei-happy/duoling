/** 一个账龄桶的金额与笔数 */
export interface AgingBucketCell {
  bucket: number;
  label: string;
  amount: number;
  count: number;
}

/** 客户维度账龄汇总行 */
export interface AgingCustomerRow {
  customerId: number;
  customerName?: string;
  enterpriseId?: number;
  creditStatus: number;
  creditStatusLabel?: string;
  creditLimit?: number;
  unpaidAmount: number;
  overdueAmount: number;
  maxOverdueDays: number;
  settleCount: number;
  exceeded: boolean;
  exceededAmount: number;
  bucketSummary: AgingBucketCell[];
}

/** 客户展开后的结算单明细 */
export interface AgingSettleDetail {
  settleId: number;
  docNo: string;
  customerId: number;
  customerName?: string;
  enterpriseId?: number;
  status: number;
  plannedAmount: number;
  receivedAmount: number;
  unpaidAmount: number;
  dueDate?: string;
  dueDateOverridden: boolean;
  overdueDays: number;
  bucket: number;
  bucketLabel?: string;
  periodStart?: string;
  periodEnd?: string;
}

export interface AgingPageResult {
  list: AgingCustomerRow[];
  count: number;
  total: number;
  page: number;
  page_size: number;
  baseDate: string;
  buckets: number[];
  bucketLabels: string[];
}

export interface AgingSummary {
  baseDate: string;
  buckets: number[];
  bucketLabels: string[];
  kpi: {
    totalUnpaid: number;
    notDueAmount: number;
    overdueAmount: number;
    lastBucketLabel: string;
    lastBucketAmount: number;
    customerCount: number;
    exceededCustomerCount: number;
    settleCount: number;
  };
  bucketDistribution: AgingBucketCell[];
  byEnterprise: {
    enterpriseId?: number;
    unpaidAmount: number;
    overdueAmount: number;
  }[];
}

export interface AgingDetailResult {
  baseDate: string;
  buckets: number[];
  bucketLabels: string[];
  customer?: AgingCustomerRow | null;
  list: AgingSettleDetail[];
  count: number;
}

/** 单客户预警摘要：0-无 1-提醒 2-警示 3-高危，任何等级都不阻断业务 */
export interface CustomerCreditBrief extends AgingCustomerRow {
  alertLevel: number;
  alertLevelLabel?: string;
  alertMessage?: string;
  buckets: number[];
  bucketLabels: string[];
}

export interface AgingParam {
  page?: number;
  limit?: number;
  customerId?: number;
  enterpriseId?: number;
  creditStatus?: number;
  keyword?: string;
  bucket?: number;
  onlyOverdue?: boolean;
  onlyExceeded?: boolean;
  baseDate?: string;
}
