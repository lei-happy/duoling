/** 挂牌摘要（队列行里展示的部分） */
export interface AuditPost {
  id: number;
  postNo: string;
  /** 1-货源 2-运力 3-服务 */
  postType: number;
  postTypeLabel: string;
  title: string;
  status: number;
  statusLabel: string;
  auditStatus: number;
  auditStatusLabel: string;
  isTop?: number;
  ownerTenantCode: string;
  ownerTenantName?: string | null;
  publisherName?: string | null;
  fromProvince?: string | null;
  fromCity?: string | null;
  fromDistrict?: string | null;
  toProvince?: string | null;
  toCity?: string | null;
  toDistrict?: string | null;
  anyDirection?: number;
  windowStart?: string | null;
  windowEnd?: string | null;
  totalQuantity?: number | null;
  quantityUnit?: string | null;
  priceType?: number | null;
  priceAmount?: number | null;
  cooperationType?: number | null;
  sourceType?: number | null;
  sourceChanged?: number | null;
  precheckFlagCount: number;
  precheckFlags: string[];
  submittedAt?: string | null;
  listedAt?: string | null;
  validUntil?: string | null;
  auditAt?: string | null;
  auditReason?: string | null;
  viewCount?: number | null;
  intentCount?: number | null;
  createdAt?: string | null;
}

/** 货源扩展 */
export interface AuditCargoExt {
  cargoCategory?: number | null;
  cargoItems?: any;
  vehicleCondition?: number | null;
  cargoName?: string | null;
  cargoWeight?: number | null;
  cargoVolume?: number | null;
  packageType?: string | null;
  viaPoints?: any;
  referenceMileage?: number | null;
  segmentCount?: number | null;
  requireTruckTypes?: any;
  requireSlotMin?: number | null;
  requireSlotMax?: number | null;
  allowSplit?: number | null;
  requireInsurance?: number | null;
  otherRequirements?: string | null;
  arriveTime?: string | null;
  timeNegotiable?: number | null;
  settleType?: number | null;
  prepayRatio?: number | null;
  freqDesc?: string | null;
}

/** 运力扩展（driverName 只在审核台可见） */
export interface AuditCapacityExt {
  postGranularity?: number | null;
  truckType?: string | null;
  slotCount?: number | null;
  truckLength?: number | null;
  ratedLoad?: number | null;
  truckQuantity?: number | null;
  plateNumber?: string | null;
  plateMasked?: string | null;
  platePublic?: number | null;
  hasTrailer?: number | null;
  trailerPlateNumber?: string | null;
  driverName?: string | null;
  driverDisplay?: string | null;
  driverYears?: number | null;
  driverOrderCount?: number | null;
  departureReadyAt?: string | null;
  pickupRadius?: number | null;
  goodAtCategories?: any;
  canInvoice?: number | null;
  invoiceType?: string | null;
  hasInsurance?: number | null;
  servicePromise?: string | null;
  settleRequire?: string | null;
}

/** 挂牌全字段（审核详情，未脱敏） */
export interface AuditPostFull extends AuditPost {
  ownerMaskedName?: string | null;
  publisherUserId?: number | null;
  fromName?: string | null;
  toName?: string | null;
  fromRegionCode?: string | null;
  toRegionCode?: string | null;
  remainingQuantity?: number | null;
  priceIncludeTax?: number | null;
  priceNegotiable?: number | null;
  keepListedAfterDeal?: number | null;
  contactName?: string | null;
  contactPhone?: string | null;
  contactBackup?: string | null;
  visibilityLevel?: number | null;
  contactVisibility?: number | null;
  applyBlockRule?: number | null;
  extraBlockTenants?: any;
  validFrom?: string | null;
  topUntil?: string | null;
  delistReason?: number | null;
  delistRemark?: string | null;
  viewerCount?: number | null;
  dealCount?: number | null;
  lastActiveAt?: string | null;
  auditBy?: number | null;
  destinations?: {
    province?: string | null;
    city?: string | null;
    regionCode?: string | null;
    sortOrder?: number | null;
  }[];
  cargo?: AuditCargoExt;
  capacity?: AuditCapacityExt;
}

/** 时效：等待时长与紧急度（后端按工作时段算好，前端不要自己减时间） */
export interface AuditSla {
  waitedMinutes: number;
  /** 0-正常 1-即将超时 2-已超时 */
  urgency: number;
  urgencyLabel: string;
  deadline?: string | null;
  isOverdue: boolean;
}

/** 队列行 */
export interface AuditQueueRow extends AuditSla {
  post: AuditPost;
}

/** 预检结论 */
export interface AuditPrecheck {
  flags: string[];
  flagCount: number;
  hasBlocking: boolean;
}

/** 源单核验。sourceConsistent 为 null 表示手工发布、无从核验 */
export interface AuditSourceCheck {
  hasSource: boolean;
  sourceType?: number | null;
  sourceId?: number | null;
  snapshotAt?: string | null;
  sourceChanged?: number | null;
  sourceChangedAt?: string | null;
  sourceConsistent: boolean | null;
  hint: string;
}

/** 发布方档案 */
export interface AuditTenantContext {
  tenantCode: string;
  tenantName?: string | null;
  maskedName?: string | null;
  licenseVerified?: number | null;
  transportLicenseVerified?: number | null;
  realnameVerified?: number | null;
  hallEnabled?: number | null;
  auditWhitelist?: number | null;
  whitelistSource?: number | null;
  whitelistAt?: string | null;
  whitelistRevokedAt?: string | null;
  whitelistRevokeReason?: string | null;
  publishRestrictedUntil?: string | null;
  intentRestrictedUntil?: string | null;
  publishCount?: number | null;
  listedCount?: number | null;
  pendingCount?: number | null;
  passRate?: number | null;
  rejectCount?: number | null;
  rejectCountRecent?: number | null;
  forceDelistCount?: number | null;
  forceDelistCountRecent?: number | null;
  spotCheckFailCount?: number | null;
  dealCount?: number | null;
  dealCompletedCount?: number | null;
  reportValidCount?: number | null;
  reportValidCountRecent?: number | null;
  firstPublishAt?: string | null;
  recentPosts?: {
    id: number;
    postNo: string;
    postType: number;
    title: string;
    status: number;
    statusLabel: string;
    auditStatus: number;
    createdAt?: string | null;
  }[];
}

/** 审核流水 */
export interface AuditTrailItem {
  id: number;
  action: number;
  actionLabel: string;
  fromStatus?: number | null;
  fromStatusLabel?: string | null;
  toStatus?: number | null;
  toStatusLabel?: string | null;
  operatorType?: number | null;
  operatorTypeLabel?: string | null;
  operatorName?: string | null;
  operatorTenantCode?: string | null;
  reasonCode?: number | null;
  reasonLabel?: string | null;
  reason?: string | null;
  changedFields?: any;
  createdAt?: string | null;
}

/** 免审白名单资格判定 */
export interface AuditEligibility {
  tenantCode: string;
  /** 自动准入结论 */
  eligible: boolean;
  /** 人工能否拍（认证、大厅能力这类硬条件不满足时为 false） */
  manualAllowed: boolean;
  summary?: string | null;
  items: {
    code: string;
    label: string;
    passed: boolean;
    detail?: string | null;
    blocking: boolean;
  }[];
}

/** 审核详情：判断依据一次给全 */
export interface AuditDetail {
  post: AuditPostFull;
  precheck: AuditPrecheck;
  sourceCheck: AuditSourceCheck;
  ownerContext: AuditTenantContext;
  whitelistEligibility: AuditEligibility;
  auditTrail: AuditTrailItem[];
  sla?: AuditSla | null;
}

/** 租户档案（白名单页与审核详情共用一份结构） */
export interface AuditTenantProfile {
  tenant: AuditTenantContext;
  eligibility: AuditEligibility;
}

/** 积压统计 */
export interface AuditBacklog {
  pending: number;
  pendingOverdue: number;
  pendingFlagged: number;
  spotCheckPending: number;
  spotCheckOverdue: number;
  slaMinutes: number;
  warnMinutes: number;
}

/** 队列查询参数（三个队列共用） */
export interface AuditPostParam {
  page?: number;
  limit?: number;
  postType?: number;
  tenantCode?: string;
  keyword?: string;
  flaggedOnly?: boolean;
  overdueOnly?: boolean;
  statuses?: number[];
  auditStatuses?: number[];
  submittedFrom?: string;
  submittedTo?: string;
}

/** 下拉元数据 */
export interface AuditOption {
  value: number | string;
  label: string;
}

export interface AuditRejectReason extends AuditOption {
  value: number;
  /** 不填补充说明时租户会收到的文案 */
  template?: string | null;
  /** 该原因必须自己写说明 */
  reasonRequired: boolean;
}

export interface AuditOptions {
  rejectReasons: AuditRejectReason[];
  postStatuses: AuditOption[];
  auditStatuses: AuditOption[];
  postTypes: AuditOption[];
  precheckFlags: AuditOption[];
  batchApproveLimit: number;
  spotCheckHours: number;
}

/** 单条审核动作的结果 */
export interface AuditActionResult {
  postId: number;
  postNo: string;
  status: number;
  statusLabel: string;
  auditStatus: number;
  auditStatusLabel: string;
  changed: boolean;
  /** 企业端角标是否已同步；false 不代表审核失败 */
  refSynced: boolean;
  whitelistRevoked: boolean;
  invalidatedIntentCount: number;
}

/** 批量通过结果，部分失败也走成功响应 */
export interface AuditBatchResult {
  successCount: number;
  succeeded: number[];
  failed: { postId: number; postNo?: string | null; message: string }[];
}

/** 白名单成员 */
export interface WhitelistMember {
  tenantCode: string;
  tenantName?: string | null;
  whitelistAt?: string | null;
  whitelistSource?: number | null;
  whitelistSourceLabel?: string | null;
  whitelistBy?: number | null;
  whitelistRevokedAt?: string | null;
  whitelistRevokeReason?: string | null;
  publishCount?: number | null;
  listedCount?: number | null;
  dealCount?: number | null;
  dealCompletedCount?: number | null;
  forceDelistCount?: number | null;
  reportValidCount?: number | null;
}

export interface WhitelistParam {
  page?: number;
  limit?: number;
  keyword?: string;
}

export interface WhitelistResult {
  tenantCode: string;
  auditWhitelist: number;
  source?: number | null;
  changed: boolean;
}
