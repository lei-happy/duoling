/** 成本政策 */
export interface CostPolicy {
  id?: number;
  policyNo: string;
  policyName: string;
  scopeType: number; // 0-全局 1-承运商 2-司机 3-运力
  scopeId?: number | null;
  carrierType?: number | null; // 1-自有车 2-承运商 3-社会运力
  effectiveDate: string;
  expiryDate?: string | null;
  status?: number; // 0-草稿 1-生效 2-已过期 3-已终止
  priority?: number;
  versionNo?: number;
  remark?: string | null;
  createdAt?: string;
  ruleCount?: number;
  activeRuleCount?: number;
  rules?: CostRule[];
}

export interface CostPolicyParam {
  keyword?: string;
  scopeType?: number;
  carrierType?: number;
  status?: number;
  page?: number;
  limit?: number;
}

/** 成本费用规则 */
export interface CostRule {
  id?: number;
  policyId?: number;
  feeType: string;
  feeName?: string | null;
  direction: number; // 1-加项 2-扣减项
  pricingMethod: string;
  qtyDimension?: string | null;
  multiplyByQty?: number;
  unitPrice: number;
  distanceKm?: number | null;
  minAmount?: number | null;
  maxAmount?: number | null;
  roundMode?: number;
  tiersJson?: TierSeg[] | null;
  percentBase?: string | null;
  ratePercent?: number | null;
  payeeType: number;
  originRegionId?: number | null;
  originCode?: string | null;
  origin?: string | null;
  destinationRegionId?: number | null;
  destinationCode?: string | null;
  destination?: string | null;
  isBidirectional?: number;
  brandId?: number | null;
  seriesId?: number | null;
  priceType?: number;
  priority?: number;
  ruleVersion?: number;
  status?: number;
  effectiveDate?: string | null;
  expiryDate?: string | null;
  remark?: string | null;
  createdAt?: string;
}

export interface TierSeg {
  upTo: number | null;
  unitPrice: number;
}

/** 费用类型 / 计价方式元数据 */
export interface CostMeta {
  feeTypes: {
    code: string;
    name: string;
    isRequired: boolean;
    payeeTypeDefault: number;
    pricingMethodDefault?: string;
    directionDefault?: number;
  }[];
  pricingMethods: {
    value: string;
    label: string;
    qtyDimension: string | null;
  }[];
}

/** 费用中心：跨政策规则（含所属政策信息） */
export interface CostRuleWithPolicy extends CostRule {
  policyName?: string;
  policyNo?: string;
  policyScopeType?: number;
  policyScopeId?: number | null;
  policyCarrierType?: number | null;
  policyStatus?: number;
  policyEffectiveDate?: string | null;
  policyExpiryDate?: string | null;
}

/** 费用中心筛选参数 */
export interface CostRuleCenterParam {
  feeType?: string;
  scopeType?: number;
  carrierType?: number;
  status?: number;
  keyword?: string;
}

/** 任务成本试算 / 结果 */
export interface TaskCostItem {
  feeType: string;
  feeName?: string | null;
  direction: number;
  payeeType?: number | null;
  pricingMethod?: string | null;
  unitPrice?: number | null;
  quantity?: number | null;
  distanceKm?: number | null;
  amount: number;
  matchedPolicyId?: number | null;
  matchedRuleId?: number | null;
  matchedRuleVersion?: number | null;
  matchScore?: number | null;
  calcStatus: string;
  errorType?: string | null;
  errorMessage?: string | null;
  matchTrace?: Record<string, unknown> | null;
}

export interface TaskCostResult {
  taskId: number;
  totalCostAmount: number;
  totalAdditionAmount: number;
  totalDeductionAmount: number;
  calcStatus: string;
  carrierType?: number | null;
  payeeType?: number | null;
  payeeId?: number | null;
  payeeName?: string | null;
  errorMessage?: string | null;
  items: TaskCostItem[];
  calcTime?: string | null;
  calcEngineVersion?: string | null;
}

export interface TaskCostPreviewRequest {
  taskId?: number;
  carrierType?: number | null;
  capacityId?: number | null;
  carrierId?: number | null;
  driverId?: number | null;
  originRegionId?: number | null;
  destinationRegionId?: number | null;
  totalQuantity?: number | null;
  vehicles?: {
    brandId?: number | null;
    seriesId?: number | null;
    vehicleBrand?: string | null;
    vehicleModel?: string | null;
    quantity: number;
  }[];
  distanceKm?: number | null;
  transportDate?: string | null;
}
