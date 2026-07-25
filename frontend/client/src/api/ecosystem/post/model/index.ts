/**
 * 发布与挂牌管理的入参 / 出参
 *
 * 挂牌本身的类型在 `@/api/ecosystem/hall/model`（`EcoPost`），这里只放
 * 「发布弹层」与「我发布的」用到的表单与结果。
 */

export interface EcoOptionItem {
  value: number;
  label: string;
}

/** 发布弹层的默认值与能力状态 */
export interface EcoPublishOptions {
  /** false 时入口处就要说明原因，别让用户填完整个表单才被拦 */
  hallEnabled: boolean;
  disabledReason?: string | null;
  licenseVerified: boolean;
  /** 免审白名单：发布后直接展示，提示语跟着变 */
  auditWhitelist: boolean;
  validDaysOptions: number[];
  /** 下拉的中文名由后端下发，与大厅筛选同一份，避免两处措辞不一致 */
  priceTypes: EcoOptionItem[];
  cooperationTypes: EcoOptionItem[];
  settleTypes: EcoOptionItem[];
  defaultValidDays: number;
  defaultVisibilityLevel: number;
  defaultContactVisibility: number;
  defaultContactName?: string | null;
  defaultContactPhone?: string | null;
  maskedName?: string | null;
}

/** 发布前试算：这单能不能发、发出去长什么样 */
export interface EcoPublishPreview {
  title: string;
  fromProvince?: string | null;
  fromCity?: string | null;
  fromName?: string | null;
  toProvince?: string | null;
  toCity?: string | null;
  toName?: string | null;
  anyDirection?: number;
  destinations: { province?: string; city?: string }[];
  windowStart?: string | null;
  windowEnd?: string | null;
  totalQuantity?: number | null;
  quantityUnit?: string | null;
  sourceType?: number;
  sourceId?: number | null;
  precheck: {
    /** true 时禁用提交按钮并展示 blockMessage，但这不是错误，别弹窗 */
    blocked: boolean;
    blockMessage?: string | null;
    /** 需要人工看一眼（具体命中哪条规则不回给发布方） */
    needsReview: boolean;
  };
}

/** 两个大厅发布表单的公共项 */
export interface EcoPostFormBase {
  contactName: string;
  contactPhone: string;
  contactBackup?: string | null;
  validDays: number;
  cooperationType: number;
  priceType: number;
  priceAmount?: number | null;
  priceIncludeTax: number;
  priceNegotiable: number;
  visibilityLevel: number;
  contactVisibility: number;
  applyBlockRule: number;
  extraBlockTenants?: string[] | null;
  title?: string | null;
}

/**
 * 发布货源
 *
 * 线路、时间、台数、货物明细都来自任务单，**不在表单里**：这些是运营比对源单的
 * 依据，能让前端传就等于能挂一条与任务单无关的信息。
 */
export interface EcoCargoForm extends EcoPostFormBase {
  settleType?: number | null;
  prepayRatio?: number | null;
  requireTruckTypes?: string[] | null;
  requireSlotMin?: number | null;
  requireSlotMax?: number | null;
  allowSplit: number;
  requireInsurance: number;
  otherRequirements?: string | null;
  timeNegotiable: number;
  freqDesc?: string | null;
}

export interface EcoCargoPublishForm extends EcoCargoForm {
  taskId: number;
}

/**
 * 发布运力
 *
 * 当前所在地与期望流向必须由用户填：运力档案里没有实时位置，
 * 而位置与流向正是找车方的第一决策依据。车辆、司机、板位来自运力档案。
 */
export interface EcoCapacityForm extends EcoPostFormBase {
  /** biz_region 主键，不是区划代码 */
  fromRegionId?: number | null;
  toRegionIds: number[];
  anyDirection: number;
  windowStart?: string | null;
  windowEnd?: string | null;
  departureReadyAt?: string | null;
  pickupRadius?: number | null;
  keepListedAfterDeal: number;
  settleRequire?: number | null;
  slotCount?: number | null;
  platePublic: number;
  goodAtCategories?: string[] | null;
  canInvoice: number;
  invoiceType?: string | null;
  hasInsurance: number;
  servicePromise?: string | null;
}

export interface EcoCapacityPublishForm extends EcoCapacityForm {
  capacityId: number;
}

/** 运力试算入参：比货源多带位置与流向，否则算不出线路与标题 */
export interface EcoCapacityPreviewParam {
  capacityId: number;
  fromRegionId?: number | null;
  toRegionIds?: number[];
  anyDirection?: number;
  windowStart?: string | null;
  windowEnd?: string | null;
  slotCount?: number | null;
}

/** 发布结果 */
export interface EcoPublishResult {
  postId: number;
  postNo: string;
  status: number;
  auditStatus: number;
  /** 免审直通已上架，与「进了审核队列」的后续引导完全不同 */
  autoListed: boolean;
  suspiciousFlags?: string[] | null;
  refSynced?: boolean;
}

/** 编辑 / 状态流转的结果 */
export interface EcoManageResult {
  postId: number;
  postNo: string;
  status: number;
  auditStatus: number;
  /** true 表示改动大到要重新审核，挂牌已从大厅撤回 */
  requireReaudit: boolean;
  changedLabels?: string[] | null;
  /** 停止展示时一并失效的洽谈数 */
  invalidatedIntentCount?: number;
  validUntil?: string | null;
  refSynced?: boolean;
}
