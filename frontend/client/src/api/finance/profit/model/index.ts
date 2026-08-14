/** 经营核算（财务确认口径，与经营驾驶舱的理论值口径不同） */

export interface AccountingKpi {
  period: string;
  periodLabel: string;
  periodStart: string;
  periodEnd: string;
  taxMode: string;
  outputTaxRate: number;
  confirmedRevenue: number;
  realizedRevenue: number;
  revenueExclTax: number;
  costInclTax: number;
  costExclTax: number;
  grossProfitInclTax: number;
  grossProfitExclTax: number;
  grossMarginRate?: number | null;
  noInvoiceCost: number;
  missingInvoiceTaxLoss: number;
  unallocatedCost: number;
  revenueDocCount: number;
  costDocCount: number;
}

export interface DimensionRow {
  dimension: string;
  dimensionValue: string;
  dimensionLabel?: string;
  revenue: number;
  revenueExclTax: number;
  cost: number;
  costExclTax: number;
  grossProfit: number;
  grossMarginRate?: number | null;
}

export interface DrillDoc {
  docKind: string;
  docKindLabel?: string;
  docId: number;
  docNo?: string;
  counterparty?: string;
  waybillNo?: string;
  amount: number;
  docAmount?: number;
  amountExclTax?: number;
  periodEnd?: string;
}

export interface DrillDownResult {
  dimension: string;
  dimensionValue: string;
  dimensionLabel?: string;
  periodLabel?: string;
  revenueDocs: DrillDoc[];
  costDocs: DrillDoc[];
  revenueTotal: number;
  costTotal: number;
}

export interface InterEntityRow {
  waybillId: number;
  waybillNo?: string;
  taskId: number;
  taskNo?: string;
  quantity: number;
  revenueEntityId?: number;
  costEntityId?: number;
  revenueAmount: number;
}

export interface InterEntitySummary {
  enterpriseId: number;
  transferOutAmount: number;
  transferInAmount: number;
  count: number;
}

export interface InterEntityResult {
  periodLabel?: string;
  rows: InterEntityRow[];
  byEntity: InterEntitySummary[];
}
