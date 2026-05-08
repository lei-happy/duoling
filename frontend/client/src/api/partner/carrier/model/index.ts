import type { PageParam } from '@/api';

export interface CarrierSettlement {
  id?: number;
  carrierId?: number;
  accountLabel: string;
  accountType?: number;
  settlementType: number;
  settlementPeriod?: number | null;
  settlementDay?: number | null;
  bankName?: string;
  bankBranch?: string;
  bankAccount?: string;
  bankAccountName?: string;
  swiftCode?: string;
  taxRate?: number | null;
  applicableScope?: string;
  isDefault?: number;
  status?: number;
  sortOrder?: number;
  remark?: string;
  createdAt?: string;
}

export interface Carrier {
  id?: number;
  carrierCode?: string;
  carrierName: string;
  shortName?: string;
  carrierType?: number;
  creditCode?: string;
  idCardNo?: string;
  legalPerson?: string;
  contactPerson?: string;
  contactPhone: string;
  contactEmail?: string;
  province?: string;
  city?: string;
  district?: string;
  address?: string;
  cooperationStartDate?: string | null;
  status?: number;
  linkedTenantCode?: string | null;
  inviteStatus?: number;
  invitedAt?: string | null;
  activatedAt?: string | null;
  ratingScore?: number | null;
  ratingLevel?: number | null;
  lastEvaluatedAt?: string | null;
  remark?: string;
  createdAt?: string;
  settlements?: CarrierSettlement[];
  defaultSettlement?: CarrierSettlement | null;
}

export interface CarrierListItem {
  id: number;
  carrierCode?: string;
  carrierName: string;
  shortName?: string;
  carrierType: number;
  contactPerson?: string;
  contactPhone: string;
  status: number;
  linkedTenantCode?: string | null;
  inviteStatus: number;
  createdAt: string;
  defaultSettlementType?: number | null;
  defaultSettlementLabel?: string | null;
  defaultBankAccountName?: string | null;
}

export interface CarrierParam extends PageParam {
  keyword?: string;
  carrierType?: number;
  status?: number;
  inviteStatus?: number;
  linkedOnly?: boolean;
}

export interface CarrierSelectItem {
  id: number;
  carrierCode?: string;
  carrierName: string;
  shortName?: string;
  carrierType: number;
  linked: boolean;
  linkedTenantCode?: string | null;
  defaultSettlement?: CarrierSettlement | null;
}

export interface CarrierInvitation {
  id: number;
  carrierId: number;
  inviteCode: string;
  invitePhone: string;
  expectedCarrierName: string;
  inviteChannel: string;
  invitePath: string;
  status: number;
  expiresAt: string;
  invitedAt: string;
  inviteeUserId?: number | null;
  forwarderUserId?: number | null;
  forwarderTenantCode?: string | null;
  acceptedTenantCode?: string | null;
  acceptedUserId?: number | null;
  acceptedRole?: number | null;
  targetMatch?: number | null;
  pendingAReview: number;
  aReviewDecision?: number | null;
  revokedReason?: string | null;
}

export interface CarrierInviteRequest {
  channel?: string;
  remark?: string;
}

export interface CarrierInviteResponse {
  carrierId: number;
  inviteId: number;
  inviteCode: string;
  /** 路径 B 链接式邀请的 URL；fast-path 直连互联时为空 */
  inviteUrl: string;
  inviteStatus: number;
  /** B / fast */
  invitePath: string;
  expiresAt?: string | null;
  userExisted: boolean;
  /** fast-path 直连时返回 B 的租户编码 */
  linkedTenantCode?: string | null;
  /** True 表示已通过 fast-path 直接建立互联 */
  fastLinked?: boolean;
}

export interface CarrierInvitePhoneCheckResult {
  phone: string;
  registered: boolean;
  userRealName?: string | null;
  tenantCode?: string | null;
  tenantName?: string | null;
  /** 对方租户当前生效的版本编码（lite/basic/...） */
  tenantVersionCode?: string | null;
  /** True 表示对方是 lite 租户，可直接建立互联 */
  canFastLink?: boolean;
  adminName?: string | null;
  adminPhoneMasked?: string | null;
}

export const INVITE_STATUS_TEXT: Record<number, string> = {
  0: '未邀请',
  1: '邀请中',
  2: '已激活',
  3: '邀请失败',
  4: 'A 端预审待确认',
  5: 'A 已撤回',
  6: 'B 已拒绝',
  7: '代转交中',
  8: 'A 端预审拒绝',
  9: 'B 端解绑'
};

export const CARRIER_TYPE_TEXT: Record<number, string> = {
  0: '公司车队',
  1: '个体司机/小车队',
  2: '其他'
};

export const SETTLEMENT_TYPE_TEXT: Record<number, string> = {
  0: '月结',
  1: '票结',
  2: '预付',
  3: '趟结'
};
