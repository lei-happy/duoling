import type { Menu } from '@/api/system/menu/model';

/** 默认仅展开第一层有子节点的项（露出第二层，第三层及以下默认收起） */
export function collectDefaultExpandedKeys(nodes: Menu[]): number[] {
  const keys: number[] = [];
  for (const n of nodes) {
    const hasTreeChildren = (n.children?.length ?? 0) > 0;
    if (hasTreeChildren && n.menuId != null) {
      keys.push(n.menuId);
    }
  }
  return keys;
}

/** 所有可展开的树节点 */
export function collectAllExpandableKeys(nodes: Menu[]): number[] {
  const keys: number[] = [];
  const walk = (list: Menu[]) => {
    for (const n of list) {
      if (n.children?.length && n.menuId != null) {
        keys.push(n.menuId);
        walk(n.children);
      }
    }
  };
  walk(nodes);
  return keys;
}

/** 收集全部菜单 id（整棵树） */
export function collectAllMenuIds(nodes: Menu[]): number[] {
  const ids: number[] = [];
  const walk = (list: Menu[]) => {
    for (const n of list) {
      if (n.menuId != null) {
        ids.push(n.menuId);
      }
      if (n.children?.length) {
        walk(n.children);
      }
    }
  };
  walk(nodes);
  return ids;
}

/** el-tree 过滤：匹配标题、权限标识 */
export function filterAuthNode(value: string, data: Menu): boolean {
  if (!value?.trim()) {
    return true;
  }
  const kw = value.trim().toLowerCase();
  return menuTextMatches(data, kw);
}

function menuTextMatches(data: Menu, kw: string): boolean {
  const title = (data.title || '').toLowerCase();
  const auth = (data.authority || '').toLowerCase();
  return title.includes(kw) || auth.includes(kw);
}

/** 节点自身或任意子孙是否匹配关键词 */
export function menuOrDescendantMatches(node: Menu, filterText: string): boolean {
  const kw = filterText?.trim().toLowerCase();
  if (!kw) {
    return true;
  }
  if (menuTextMatches(node, kw)) {
    return true;
  }
  return (node.children ?? []).some((c) => menuOrDescendantMatches(c, filterText));
}

/** 模块勾选统计（含自身） */
export function countModuleSelection(
  module: Menu,
  checkedSet: ReadonlySet<number>
): { checked: number; total: number } {
  const ids = collectAllMenuIds([module]);
  let checked = 0;
  for (const id of ids) {
    if (checkedSet.has(id)) {
      checked++;
    }
  }
  return { checked, total: ids.length };
}

/**
 * 与 el-tree（非 check-strictly）一致：若父节点在勾选集中，则级联补全全部子孙
 */
export function expandCheckedKeysWithCascade(
  modules: Menu[],
  checked: number[]
): number[] {
  const set = new Set(checked);
  const walk = (node: Menu) => {
    if (node.menuId != null && set.has(node.menuId)) {
      for (const id of collectAllMenuIds([node])) {
        set.add(id);
      }
      return;
    }
    for (const child of node.children ?? []) {
      walk(child);
    }
  };
  for (const m of modules) {
    walk(m);
  }
  return [...set];
}

/**
 * 提交用 id：完全勾选的节点 + 有勾选子孙的祖先（等价于 checked + half-checked）
 */
export function collectSaveMenuIds(
  modules: Menu[],
  checkedSet: ReadonlySet<number>
): number[] {
  const ids: number[] = [];
  const walk = (node: Menu): boolean => {
    let childHit = false;
    for (const child of node.children ?? []) {
      if (walk(child)) {
        childHit = true;
      }
    }
    const selfHit = node.menuId != null && checkedSet.has(node.menuId);
    if (selfHit || childHit) {
      if (node.menuId != null) {
        ids.push(node.menuId);
      }
      return true;
    }
    return false;
  };
  for (const m of modules) {
    walk(m);
  }
  return ids;
}

/**
 * Element Plus Tree：props.class，用于「子级全部为按钮」的父节点打标，配合 CSS 横向排列子节点
 */
export function getRoleAuthTreeNodeClass(data: Menu): string {
  const ch = data.children;
  if (ch?.length && ch.every((c) => c.menuType === 1)) {
    return 'is-role-auth-action-group';
  }
  return '';
}
