/**
 * 驾驶员列表 - 行内操作配置
 *
 * 顺序对齐菜单按钮 sort_order；槽位算法见开发手册「17.列表操作列按钮规范」。
 */

import type { Component } from 'vue';
import type {
  ButtonDropdownItem,
  ButtonItem
} from 'ele-admin-plus/es/ele-buttons/types';
import { Key, Switch, Wallet } from '@element-plus/icons-vue';
import { DeleteOutlined, EditOutlined } from '@/components/icons';
import type { Driver } from '@/api/capacity/self-capacity/driver/model';

export type DriverRowActionKey =
  | 'edit'
  | 'fund-account'
  | 'hr-status'
  | 'reset-password'
  | 'remove';

export interface DriverActionDef {
  key: DriverRowActionKey;
  title: string;
  icon: Component;
  permission?: string;
  danger?: boolean;
  divided?: boolean;
  /** 行状态不满足时跳过 */
  visible?: (row: Driver) => boolean;
}

/** 与菜单 capacity:self_capacity:driver:* 的 sort_order 对齐 */
export const DRIVER_ROW_ACTIONS: DriverActionDef[] = [
  {
    key: 'edit',
    title: '编辑',
    icon: EditOutlined,
    permission: 'capacity:self_capacity:driver:edit'
  },
  {
    key: 'fund-account',
    title: '资金账户',
    icon: Wallet,
    permission: 'capacity:self_capacity:driver:fund-account'
  },
  {
    key: 'hr-status',
    title: '调整人事状态',
    icon: Switch
  },
  {
    key: 'reset-password',
    title: '重置登录密码',
    icon: Key,
    visible: (row) => !!row.userId
  },
  {
    key: 'remove',
    title: '删除',
    icon: DeleteOutlined,
    permission: 'capacity:self_capacity:driver:delete',
    divided: true,
    danger: true
  }
];

export interface BuildDriverActionItemsContext {
  hasPermission: (code: string) => boolean;
  onEdit: (row: Driver) => void;
  onFundAccount: (row: Driver) => void;
  onHrStatus: (row: Driver) => void;
  onResetPassword: (row: Driver) => void;
  onRemove: (row: Driver) => void;
}

function estimateActionLinkWidth(title: string): number {
  return 20 + title.length * 14 + 12;
}

/** 操作列 minWidth：最坏外显为「编辑」+「更多」 */
export function resolveDriverActionColumnMinWidth(): number {
  const pad = 28;
  const divider = 17;
  const moreW = 68;
  return estimateActionLinkWidth('编辑') + divider + moreW + pad;
}

/** 槽位算法：可见 ≤2 平铺；≥3 为首项 + 更多（更多悬停展开） */
export function buildDriverActionItems(
  row: Driver,
  ctx: BuildDriverActionItemsContext
): ButtonItem[] {
  const handlers: Record<DriverRowActionKey, (r: Driver) => void> = {
    edit: ctx.onEdit,
    'fund-account': ctx.onFundAccount,
    'hr-status': ctx.onHrStatus,
    'reset-password': ctx.onResetPassword,
    remove: ctx.onRemove
  };

  const visible: ButtonDropdownItem[] = [];
  for (const a of DRIVER_ROW_ACTIONS) {
    if (a.permission && !ctx.hasPermission(a.permission)) continue;
    if (a.visible && !a.visible(row)) continue;
    visible.push({
      title: a.title,
      icon: a.icon,
      permission: a.permission,
      danger: a.danger,
      divided: a.divided,
      onClick: () => handlers[a.key](row)
    });
  }

  if (visible.length === 0) return [];
  if (visible.length <= 2) {
    return visible.map((it) => ({
      ...it,
      type: 'link' as const
    })) as ButtonItem[];
  }
  const [primary, ...rest] = visible;
  return [
    { ...primary!, type: 'link' as const },
    { preset: 'more' as const, dropdownItems: rest }
  ] as ButtonItem[];
}
