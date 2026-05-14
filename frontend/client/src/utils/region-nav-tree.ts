import type { RegionNavNode } from '@/api/basic-data/region/model';

/**
 * 在行政区划导航树中，按叶子「国标区划码」查找从根到叶的 code 路径（供级联 emitPath 回显）。
 */
export function findRegionCodePath(
  nodes: RegionNavNode[],
  targetCode: string | undefined | null
): string[] | null {
  if (!targetCode) return null;
  for (const n of nodes) {
    if (n.code === targetCode) {
      return [n.code];
    }
    const children = n.children ?? [];
    if (children.length) {
      const sub = findRegionCodePath(children, targetCode);
      if (sub) {
        return [n.code, ...sub];
      }
    }
  }
  return null;
}

/**
 * 根据级联已选 code 路径，取叶子节点（含 biz_region 主键 regionId）。
 */
export function findLeafRegionByCodePath(
  nodes: RegionNavNode[],
  codes: string[] | undefined | null
): RegionNavNode | null {
  if (!codes?.length) return null;
  let current: RegionNavNode | undefined;
  let list = nodes;
  for (const code of codes) {
    current = list.find((n) => n.code === code);
    if (!current) return null;
    list = current.children ?? [];
  }
  return current ?? null;
}

export function leafRegionIdFromCodePath(
  nodes: RegionNavNode[],
  codes: string[] | undefined | null
): number | undefined {
  const leaf = findLeafRegionByCodePath(nodes, codes);
  return leaf?.regionId;
}
