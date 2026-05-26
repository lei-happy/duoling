import type { PageParam } from '@/api';

/** 车辆信息 */
export interface SocialCapacityVehicleInfo {
  plateNumber?: string;
  plateCategory?: string;
  vehicleType?: string;
  brand?: string;
  model?: string;
  color?: string;
  vin?: string;
  engineNo?: string;
  loadCapacity?: number;
  volumeCapacity?: number;
  length?: number;
  width?: number;
  height?: number;
  axleCount?: number;
  hasTrailer?: number;
  trailerPlate?: string;
  trailerType?: string;
  trailerLoadCapacity?: number;
  registrationDate?: string;
  inspectionExpire?: string;
  insuranceExpire?: string;
  transportLicenseNo?: string;
  transportLicenseExpire?: string;
  vehicleLicensePhoto?: string;
  vehicleLicenseBackPhoto?: string;
  transportLicensePhoto?: string;
  vehiclePhoto?: string;
}

/** 驾驶员信息 */
export interface SocialCapacityDriverInfo {
  name?: string;
  gender?: number;
  phone?: string;
  idCard?: string;
  birthDate?: string;
  avatar?: string;
  licenseType?: string;
  licenseNo?: string;
  licenseIssueDate?: string;
  licenseExpire?: string;
  licenseClass?: string;
  qualificationNo?: string;
  qualificationExpire?: string;
  licensePhoto?: string;
  qualificationPhoto?: string;
  idCardFrontPhoto?: string;
  idCardBackPhoto?: string;
  emergencyContact?: string;
  emergencyPhone?: string;
  homeAddress?: string;
}

/** 结算账户 */
export interface SocialCapacityAccount {
  id?: number;
  socialCapacityId?: number;
  accountType?: number;
  accountLabel?: string;
  accountName?: string;
  accountNo?: string;
  bankName?: string;
  bankBranch?: string;
  holderIdCard?: string;
  isDefault?: number;
  status?: number;
  remark?: string;
  createdAt?: string;
  updatedAt?: string;
}

/** 默认结算账户摘要 */
export interface SocialCapacityAccountBrief {
  id?: number;
  accountType?: number;
  accountLabel?: string;
  accountName?: string;
  accountNo?: string;
  bankName?: string;
  isDefault?: number;
  status?: number;
}

/** 审核 / 状态流水 */
export interface SocialCapacityAuditChange {
  group?: string;
  field?: string;
  label?: string;
  before?: string;
  after?: string;
}

export interface SocialCapacityAuditAttachment {
  requestType?: 'profile_change' | 'status_change';
  changeType?: 'initial' | 'modify' | 'unchanged';
  changes?: SocialCapacityAuditChange[];
  snapshot?: Record<string, Record<string, unknown>>;
  statusChange?: {
    from?: number;
    to?: number;
    fromLabel?: string;
    toLabel?: string;
    remark?: string;
  };
}

export interface SocialCapacityAudit {
  id?: number;
  socialCapacityId?: number;
  action?: number;
  beforeStatus?: number;
  afterStatus?: number;
  operatorUserId?: number;
  operatorName?: string;
  remark?: string;
  attachment?: SocialCapacityAuditAttachment | null;
  approvalFlowInstId?: number;
  createdAt?: string;
}

/** 列表项（分页用） */
export interface SocialCapacityListItem {
  id?: number;
  socialCode?: string;
  driverName?: string;
  driverPhone?: string;
  plateNumber?: string;
  plateCategory?: string;
  vehicleTypeLabel?: string;
  source?: string;
  approvalStatus?: number;
  status?: number;
  ratingScore?: number;
  ratingLevel?: number;
  defaultAccount?: SocialCapacityAccountBrief;
  createdAt?: string;
  updatedAt?: string;
}

/** 详情 */
export interface SocialCapacityDetail extends SocialCapacityListItem {
  driverIdCard?: string;
  sourceRemark?: string;
  referrerUserId?: number;
  approvalUserId?: number;
  approvalTime?: string;
  approvalRemark?: string;
  statusRemark?: string;
  lastEvaluatedAt?: string;
  evaluationSummary?: unknown;
  orderCount?: number;
  lastDispatchedAt?: string;
  createdUserId?: number;
  updatedUserId?: number;
  remark?: string;
  vehicle?: SocialCapacityVehicleInfo;
  driver?: SocialCapacityDriverInfo;
  accounts?: SocialCapacityAccountBrief[];
  lastAudit?: SocialCapacityAudit;
}

/** 创建 / 编辑提交体 */
export interface SocialCapacityForm {
  source?: string;
  sourceRemark?: string;
  referrerUserId?: number;
  remark?: string;
  vehicle?: SocialCapacityVehicleInfo;
  driver?: SocialCapacityDriverInfo;
}

export interface SocialCapacityParam extends PageParam {
  keyword?: string;
  approvalStatus?: number;
  status?: number;
  source?: string;
  ratingLevel?: number;
  sort?: string;
  order?: string;
}

/** 调度选择器输出 */
export interface SocialCapacitySelectItem {
  id?: number;
  socialCode?: string;
  driverName?: string;
  driverPhone?: string;
  plateNumber?: string;
  vehicleType?: string;
  loadCapacity?: number;
  ratingLevel?: number;
  defaultAccount?: SocialCapacityAccountBrief;
}

/** 状态变更体 */
export interface SocialCapacityStatusBody {
  status: number;
  remark?: string;
}

/** 审核 / 撤回 / 提交体 */
export interface SocialCapacityActionBody {
  remark?: string;
}

/** 结算账户提交体 */
export interface SocialCapacityAccountForm {
  accountType?: number;
  accountLabel?: string;
  accountName?: string;
  accountNo?: string;
  bankName?: string;
  bankBranch?: string;
  holderIdCard?: string;
  isDefault?: number;
  status?: number;
  remark?: string;
}
