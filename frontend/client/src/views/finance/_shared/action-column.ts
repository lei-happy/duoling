import type {
  ButtonDropdownItem,
  ButtonItem
} from 'ele-admin-plus/es/ele-buttons/types';

/** 槽位算法：可见 ≤2 平铺；≥3 为首项 + 更多（更多悬停展开） */
export function buildActionColumnItems(
  visible: ButtonDropdownItem[]
): ButtonItem[] {
  if (visible.length === 0) return [];
  if (visible.length <= 2) {
    return visible.map((it) => ({ ...it, type: 'link' as const }));
  }
  const [primary, ...rest] = visible;
  return [
    { ...primary!, type: 'link' },
    { preset: 'more', dropdownItems: rest }
  ];
}

/** 操作列 minWidth：首项 +「更多」的保守宽度 */
export function resolveMoreActionColumnWidth(primaryTitle = '详情') {
  const pad = 28;
  const divider = 17;
  const moreW = 68;
  const primaryW = 20 + primaryTitle.length * 14 + 12;
  return primaryW + divider + moreW + pad;
}
