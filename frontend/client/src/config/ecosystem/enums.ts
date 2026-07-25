/**
 * 服务平台状态字典
 *
 * 与后端 `app/modules/console/models/ecosystem/constants.py` 一一对应，
 * 改动时两侧必须同步（后端那份文件的注释里也写了这条路径）。
 *
 * 下拉可选项（计价方式、结算方式、货物类别、排序方式…）不在这里维护：
 * 那些由 `/filters` 与 `/publish/options` 下发，前端再抄一份就会出现
 * 「后端加了一个选项、界面上没有」的情况。这里只放**渲染时必须就地取用**
 * 的映射：状态标签的颜色与文案、Tab 顺序、可执行动作的判定。
 */

/** 挂牌类型 */
export const PostType = {
  CARGO: 1,
  CAPACITY: 2
} as const;

/** 挂牌状态 */
export const PostStatus = {
  DRAFT: 0,
  AUDITING: 1,
  REJECTED: 2,
  LISTED: 3,
  LOCKED: 4,
  FULFILLING: 5,
  FINISHED: 6,
  DELISTED: 7,
  CANCELLED: 9
} as const;

/** 审核状态 */
export const AuditStatus = {
  NOT_SUBMITTED: 0,
  PENDING: 1,
  APPROVED: 2,
  REJECTED: 3,
  WHITELIST_PASS: 4,
  SPOT_CHECKED: 5
} as const;

/** 计价方式 */
export const PriceType = {
  PACKAGE: 1,
  PER_UNIT: 2,
  PER_KM: 3,
  NEGOTIABLE: 4
} as const;

/** 合作方式 */
export const CooperationType = {
  ONCE: 1,
  LONG_TERM: 2
} as const;

/** 结算方式 */
export const SettleType = {
  CASH: 1,
  MONTHLY: 2,
  PREPAY: 3
} as const;

/** 货物类别 */
export const CargoCategory = {
  VEHICLE: 1,
  GENERAL: 2,
  OTHER: 3
} as const;

/** 信息可见层级 */
export const VisibilityLevel = {
  ANONYMOUS: 1,
  CERTIFIED: 2,
  NEGOTIATING: 3,
  DEALT: 4
} as const;

/** 下架原因 */
export const DelistReason = {
  BY_OWNER: 1,
  EXPIRED: 2,
  FORCED: 3,
  SOURCE_INVALID: 4,
  DEALT: 5
} as const;

/** 挂牌状态标签：文案 + Element Plus 的 tag 类型 */
export const POST_STATUS_META: Record<
  number,
  { label: string; type: 'primary' | 'success' | 'info' | 'warning' | 'danger' }
> = {
  [PostStatus.DRAFT]: { label: '草稿', type: 'info' },
  [PostStatus.AUDITING]: { label: '待审核', type: 'warning' },
  [PostStatus.REJECTED]: { label: '未通过', type: 'danger' },
  [PostStatus.LISTED]: { label: '展示中', type: 'success' },
  [PostStatus.LOCKED]: { label: '已定合作方', type: 'primary' },
  [PostStatus.FULFILLING]: { label: '履约中', type: 'primary' },
  [PostStatus.FINISHED]: { label: '已完成', type: 'info' },
  [PostStatus.DELISTED]: { label: '已停止展示', type: 'info' },
  [PostStatus.CANCELLED]: { label: '已取消', type: 'info' }
};

export const DELIST_REASON_LABELS: Record<number, string> = {
  [DelistReason.BY_OWNER]: '你主动停止了展示',
  [DelistReason.EXPIRED]: '展示时间到期，自动下架',
  [DelistReason.FORCED]: '平台下架',
  [DelistReason.SOURCE_INVALID]: '源单已变更或取消',
  [DelistReason.DEALT]: '已达成合作，自动下架'
};

/** 「我发布的」页签。键名与后端 statusCounts 一致 */
export const MY_POST_TABS: { key: string; label: string }[] = [
  { key: '', label: '全部' },
  { key: 'listed', label: '展示中' },
  { key: 'auditing', label: '待审核' },
  { key: 'rejected', label: '未通过' },
  { key: 'draft', label: '草稿' },
  { key: 'dealing', label: '进行中' },
  { key: 'finished', label: '已完成' },
  { key: 'delisted', label: '已停止' }
];

/** 展示天数，后端 VALID_DAYS_OPTIONS 的兜底值（正常走接口下发） */
export const VALID_DAYS_FALLBACK = [1, 3, 7, 15, 30];
export const DEFAULT_VALID_DAYS = 7;

/** 允许发布方编辑的状态，与后端 PostStatus.EDITABLE 对齐 */
export const EDITABLE_STATUSES: number[] = [
  PostStatus.DRAFT,
  PostStatus.REJECTED,
  PostStatus.LISTED,
  PostStatus.DELISTED
];

/** 可提交审核的状态：草稿与被驳回 */
export const SUBMITTABLE_STATUSES: number[] = [
  PostStatus.DRAFT,
  PostStatus.REJECTED
];

export function postStatusMeta(status?: number | null) {
  return (
    POST_STATUS_META[Number(status ?? -1)] ?? { label: '未知', type: 'info' }
  );
}

/** 计价方式 + 金额 → 一句可直接展示的报价 */
export function priceText(
  priceType?: number | null,
  priceAmount?: string | number | null,
  negotiable?: number | null
): string {
  if (priceType === PriceType.NEGOTIABLE || priceAmount == null) {
    return '价格面议';
  }
  const unit =
    priceType === PriceType.PER_UNIT
      ? '元/台'
      : priceType === PriceType.PER_KM
        ? '元/公里'
        : '元包车';
  const amount = Number(priceAmount);
  const shown = Number.isFinite(amount)
    ? amount.toLocaleString('zh-CN')
    : String(priceAmount);
  return `${shown} ${unit}${negotiable ? '（可议）' : ''}`;
}
