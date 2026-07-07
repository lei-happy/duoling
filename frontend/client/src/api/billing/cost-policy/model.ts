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
  conditionsJson?: ConditionNode | null;
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

/** 条件树节点：分组（logic+children）或叶子（type+op+value…） */
export interface ConditionNode {
  // 分组
  logic?: 'and' | 'or';
  children?: ConditionNode[];
  // 叶子
  type?: string;
  op?: string;
  value?: unknown;
  field?: string;
  negate?: boolean;
  // region_route 叶子
  originRegionId?: number | null;
  destinationRegionId?: number | null;
  bidirectional?: number;
  [key: string]: unknown;
}

/** 条件类型元数据（由后端 registry.describe_all 下发） */
export interface ConditionType {
  key: string;
  label: string;
  valueType: string;
  operators: string[];
  optionSource?: string | null;
  fields?: { value: string; label: string }[];
}

/** 费用类型 / 计价方式 / 条件类型元数据 */
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
  conditionTypes?: ConditionType[];
}

/** 由 legacy 列合成条件树（编辑存量规则且无 conditionsJson 时回显用） */
export function legacyToConditionTree(rule: CostRule): ConditionNode {
  const children: ConditionNode[] = [];
  if (rule.originRegionId != null || rule.destinationRegionId != null) {
    children.push({
      type: 'region_route',
      originRegionId: rule.originRegionId ?? null,
      destinationRegionId: rule.destinationRegionId ?? null,
      bidirectional: rule.isBidirectional ?? 0
    });
  }
  if (rule.seriesId != null) {
    children.push({ type: 'vehicle_series', op: 'eq', value: rule.seriesId });
  } else if (rule.brandId != null) {
    children.push({ type: 'vehicle_brand', op: 'eq', value: rule.brandId });
  }
  return { logic: 'and', children };
}

/** 条件树 → 人类可读摘要串（列表/详情/trace 展示用） */
export function summarizeCondition(
  node?: ConditionNode | null,
  typeMap?: Record<string, ConditionType>
): string {
  if (!node) return '不限';
  // 分组
  if (node.children !== undefined || node.logic !== undefined) {
    const kids = (node.children || [])
      .map((c) => summarizeCondition(c, typeMap))
      .filter((s) => s && s !== '不限');
    if (!kids.length) return '不限';
    const sep = node.logic === 'or' ? ' 或 ' : ' 且 ';
    return kids.length > 1 ? `(${kids.join(sep)})` : kids[0];
  }
  // 叶子
  const label = typeMap?.[node.type || '']?.label || node.type || '条件';
  const neg = node.negate ? '非' : '';
  if (node.type === 'region_route') {
    const dir = node.bidirectional ? '↔' : '→';
    return `${neg}线路[${node.originRegionId ?? '*'}${dir}${node.destinationRegionId ?? '*'}]`;
  }
  const v = Array.isArray(node.value)
    ? (node.value as unknown[]).join('~')
    : String(node.value ?? '');
  const field = node.field ? `.${node.field}` : '';
  return `${neg}${label}${field} ${node.op || ''} ${v}`.trim();
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
