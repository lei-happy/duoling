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

/**
 * 按租户库地区主键查找从根到叶的 code 路径。
 */
export function findRegionCodePathById(
  nodes: RegionNavNode[],
  targetId: number | undefined | null
): string[] | null {
  if (targetId == null) return null;
  for (const n of nodes) {
    if (n.regionId === targetId) {
      return [n.code];
    }
    const children = n.children ?? [];
    if (children.length) {
      const sub = findRegionCodePathById(children, targetId);
      if (sub) {
        return [n.code, ...sub];
      }
    }
  }
  return null;
}

const SKIP_NAME_SEGMENTS = new Set(['中国', '中华人民共和国', '市辖区']);

function splitNamePath(raw: string): string[] {
  return raw
    .replace(/[／\\]/g, '/')
    .split('/')
    .map((s) => s.trim())
    .filter((p) => p && !SKIP_NAME_SEGMENTS.has(p));
}

function adminStem(name: string): string {
  return name.replace(
    /(?:特别行政区|维吾尔自治区|壮族自治区|回族自治区|自治区|省|市|区|县|旗)$/g,
    ''
  );
}

function nameMatches(nodeName: string, part: string): boolean {
  if (nodeName === part) return true;
  const a = adminStem(nodeName);
  const b = adminStem(part);
  return !!(a && b && a === b);
}

function isSkippableContainer(node: RegionNavNode): boolean {
  return node.name === '市辖区';
}

function walkNamePath(
  nodes: RegionNavNode[],
  parts: string[]
): string[] | null {
  if (!parts.length) return null;
  const [head, ...rest] = parts;
  for (const n of nodes) {
    if (!nameMatches(n.name, head!)) continue;
    if (!rest.length) return [n.code];
    const children = n.children ?? [];
    if (!children.length) return [n.code];
    const sub = walkNamePath(children, rest);
    if (sub) return [n.code, ...sub];
    const skipped = children.find(isSkippableContainer);
    if (skipped?.children?.length) {
      const via = walkNamePath(skipped.children, rest);
      if (via) return [n.code, skipped.code, ...via];
    }
  }
  return null;
}

/**
 * 按「省/市/区」地名路径回显级联。允许缺省、市辖区中间层。
 */
export function findRegionCodePathByNamePath(
  nodes: RegionNavNode[],
  raw: string | undefined | null
): string[] | null {
  const text = (raw ?? '').trim();
  if (!text) return null;
  const parts = splitNamePath(text);
  if (!parts.length) return null;
  const fromRoot = walkNamePath(nodes, parts);
  if (fromRoot) return fromRoot;
  for (const n of nodes) {
    const children = n.children ?? [];
    if (!children.length) continue;
    const sub = findRegionCodePathByNamePath(children, parts.join('/'));
    if (sub) return [n.code, ...sub];
  }
  return null;
}

export function resolveRegionCodePath(
  nodes: RegionNavNode[],
  hint: {
    code?: string | null;
    regionId?: number | null;
    location?: string | null;
  }
): string[] {
  return (
    findRegionCodePath(nodes, hint.code) ??
    findRegionCodePathById(nodes, hint.regionId) ??
    findRegionCodePathByNamePath(nodes, hint.location) ??
    (hint.code ? [hint.code] : [])
  );
}
