import type { PageParam } from '@/api';

/**
 * 服务平台挂牌（大厅卡片 / 详情 / 我发布的，共用一个类型）
 *
 * 字段可见性由后端按查看方层级裁剪（见 08.接口契约.md §2）：同一个接口，
 * 未认证企业拿到的 `fromName`、`priceAmount`、`windowStart` 就是 null。
 * 所以这里几乎所有字段都是可选的，界面必须按「拿不到就不显示这一行」来写，
 * 不能假设它一定有值。
 */
export interface EcoPost {
  id: number;
  postNo: string;
  postType: number;
  title: string;
  status: number;
  isTop?: number;

  /** 发布方脱敏名（所有层级可见），如「杭州**物流」 */
  ownerMaskedName?: string;
  /** 发布方全称，按挂牌的可见范围配置下发 */
  ownerTenantName?: string | null;

  fromProvince?: string;
  fromCity?: string;
  fromDistrict?: string | null;
  fromName?: string | null;
  toProvince?: string;
  toCity?: string;
  toDistrict?: string | null;
  toName?: string | null;
  /** 1-接受任意流向（运力） */
  anyDirection?: number;
  /** regionCode 只在发布方看自己的挂牌时下发，用于编辑弹层回填 */
  destinations?: { province?: string; city?: string; regionCode?: number }[];

  totalQuantity?: number;
  quantityUnit?: string;
  remainingQuantity?: number;

  priceType?: number;
  /** 认证层可见的具体报价 */
  priceAmount?: string | null;
  /** 匿名层看到的价格区间，如「1.2 万 ~ 1.5 万」 */
  priceRange?: string | null;
  priceNegotiable?: number;
  priceIncludeTax?: number;
  cooperationType?: number;

  windowStart?: string | null;
  windowEnd?: string | null;
  listedAt?: string | null;
  validUntil?: string | null;
  lastActiveAt?: string | null;

  viewCount?: number | null;
  intentCount?: number | null;

  credit?: EcoCredit;
  /** 查看方层级：1-匿名 2-认证 3-洽谈 4-成交 5-发布方 */
  viewerLevel?: number;
  isMine?: boolean;

  // ---- 货源扩展 ----
  cargoCategory?: number;
  vehicleCondition?: number | null;
  cargoName?: string | null;
  cargoWeight?: number | null;
  cargoVolume?: number | null;
  packageType?: string | null;
  cargoItems?: EcoCargoItem[] | null;
  requireTruckTypes?: string[] | null;
  requireSlotMin?: number | null;
  requireSlotMax?: number | null;
  allowSplit?: number;
  requireInsurance?: number;
  referenceMileage?: number | null;
  segmentCount?: number | null;
  timeNegotiable?: number;
  freqDesc?: string | null;
  viaPoints?: string[] | null;
  otherRequirements?: string | null;
  settleType?: number | null;
  prepayRatio?: number | null;
  arriveTime?: string | null;

  // ---- 运力扩展 ----
  postGranularity?: number;
  truckType?: string | null;
  slotCount?: number | null;
  truckLength?: number | null;
  ratedLoad?: number | null;
  truckQuantity?: number | null;
  hasTrailer?: number;
  goodAtCategories?: string[] | null;
  canInvoice?: number;
  invoiceType?: string | null;
  hasInsurance?: number;
  servicePromise?: string | null;
  /** 是否公开完整车牌。只对发布方下发：他自己总能看到完整车牌，
   *  只看 plateNumber 有值会把编辑弹层的勾选一律回填成「已公开」 */
  platePublic?: number;
  plateNumber?: string | null;
  plateMasked?: string | null;
  trailerPlateNumber?: string | null;
  driverDisplay?: string | null;
  driverYears?: number | null;
  driverOrderCount?: number | null;
  departureReadyAt?: string | null;
  pickupRadius?: number | null;
  settleRequire?: number | null;

  // ---- 详情才有：联系方式 ----
  contactName?: string | null;
  contactPhone?: string | null;
  contactBackup?: string | null;
  /** true 表示还没解锁，界面显示遮罩位而不是空白 */
  contactLocked?: boolean;

  // ---- 详情且仅发布方可见 ----
  sourceType?: number;
  sourceId?: number | null;
  /** 出发地区划代码，以及详情接口按它翻出来的租户库地区 ID（编辑回填用） */
  fromRegionCode?: number | null;
  fromRegionId?: number | null;
  toRegionIds?: number[];
  sourceChanged?: number;
  sourceChangedAt?: string | null;
  applyBlockRule?: number;
  extraBlockTenants?: string[] | null;
  visibilityLevel?: number;
  contactVisibility?: number;
  keepListedAfterDeal?: number;
  delistReason?: number | null;
  delistRemark?: string | null;
  viewerStats?: EcoViewerStats | null;
  auditStatus?: number;
  auditReason?: string | null;
  auditAt?: string | null;
  precheckFlags?: string[] | null;
}

export interface EcoCargoItem {
  brand?: string;
  series?: string;
  quantity?: number;
}

/**
 * 发布方信誉
 *
 * 样本不足时后端不给数字、只给 `isNewcomer`：2 单里失败 1 单会显示 50% 完成率，
 * 读起来像劣质承运商，实际只是刚加入。
 */
export interface EcoCredit {
  isNewcomer?: boolean;
  dealCompletedCount?: number;
  completeRate?: number | null;
  avgScore?: number | null;
  topTags?: string[] | null;
  avgRespondMinutes?: number | null;
}

/** 热度反馈，仅发布方在自己挂牌详情里可见 */
export interface EcoViewerStats {
  days: number;
  viewerTenantCount: number;
  viewCount: number;
  topProvinces: { province: string; tenantCount: number }[];
  intentCount: number;
}

/** 大厅分页出参 */
export interface EcoPostPage {
  list: EcoPost[];
  total: number;
  count: number;
  page: number;
  pageSize: number;
}

/** 「我发布的」分页出参：多一份页签角标 */
export interface EcoMyPostPage extends EcoPostPage {
  statusCounts?: Record<string, number>;
}

/** 大厅筛选条件 */
export interface EcoHallParam extends PageParam {
  keyword?: string;
  fromProvince?: string;
  fromCity?: string;
  toProvinces?: string[];
  toCity?: string;
  windowStartFrom?: string;
  windowStartTo?: string;
  quantityMin?: number;
  quantityMax?: number;
  truckTypes?: string[];
  slotMin?: number;
  slotMax?: number;
  cargoCategory?: number;
  priceType?: number;
  onlyVerified?: boolean;
  onlyHighCredit?: boolean;
  /** 默认 true：大厅里不该出现自己发的信息 */
  excludeMine?: boolean;
  sortBy?: string;
}

export interface EcoOption {
  value: number | string;
  label: string;
}

/** 大厅筛选项元数据（由后端下发，前端不再各写一份枚举） */
export interface EcoHallFilters {
  postType: number;
  sortOptions: EcoOption[];
  priceTypes: EcoOption[];
  cooperationTypes: EcoOption[];
  settleTypes: EcoOption[];
  validDaysOptions: number[];
  cargoCategories?: EcoOption[];
}

/** 「我发布的」筛选条件 */
export interface EcoMyPostParam extends PageParam {
  postType?: number;
  /** 页签键：draft / auditing / rejected / listed / dealing / finished / delisted */
  statusGroup?: string;
  keyword?: string;
}
