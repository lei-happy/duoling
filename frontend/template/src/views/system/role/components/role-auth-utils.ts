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
  const title = (data.title || '').toLowerCase();
  const auth = (data.authority || '').toLowerCase();
  return title.includes(kw) || auth.includes(kw);
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
