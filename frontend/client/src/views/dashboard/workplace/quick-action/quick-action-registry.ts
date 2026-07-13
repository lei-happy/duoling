/**
 * 工作台快捷操作 — 注册表
 *
 * 新增业务入口时只需在本文件追加 QuickActionConfig，
 * 详见：doc/04.开发手册/15.快捷操作接入说明.md
 */

import type { QuickActionConfig } from './types';

export const QUICK_ACTION_CONFIG_VERSION = 1;

export const QUICK_ACTION_MAX = 12;

/** 全部可注册的快捷操作 */
export const QUICK_ACTION_REGISTRY: QuickActionConfig[] = [
  {
    key: 'waybill.create',
    title: '新建运单',
    icon: 'PlusCircleOutlined',
    color: '#69c0ff',
    group: '运营调度',
    type: 'route',
    path: '/operation/waybill',
    query: { action: 'create' },
    permission: 'business:waybill:add',
    feature: 'biz_waybill',
    defaultVisible: true,
    sortOrder: 10
  },
  {
    key: 'task.create',
    title: '新建配载',
    icon: 'AppstoreAddOutlined',
    color: '#b37feb',
    group: '运营调度',
    type: 'route',
    path: '/operation/task-create',
    permission: 'operation:task:add',
    feature: 'biz_dispatch',
    defaultVisible: true,
    sortOrder: 20
  },
  {
    key: 'waybill.list',
    title: '运单管理',
    icon: 'LogOutlined',
    color: '#5cdbd3',
    group: '运营调度',
    type: 'route',
    path: '/operation/waybill',
    permission: 'business:waybill:list',
    feature: 'biz_waybill',
    defaultVisible: true,
    sortOrder: 30
  },
  {
    key: 'task.list',
    title: '调度任务',
    icon: 'ShoppingOutlined',
    color: '#ff9c6e',
    group: '运营调度',
    type: 'route',
    path: '/operation/task',
    permission: 'operation:task:list',
    feature: 'biz_dispatch',
    defaultVisible: true,
    sortOrder: 40
  },
  {
    key: 'customer.list',
    title: '客户管理',
    icon: 'UserOutlined',
    color: '#95de64',
    group: '客商中心',
    type: 'route',
    path: '/partner/customer',
    permission: 'partner:customer:list',
    defaultVisible: true,
    sortOrder: 50
  },
  {
    key: 'vehicle.list',
    title: '车辆管理',
    icon: 'ControlOutlined',
    color: '#ffc069',
    group: '运力中心',
    type: 'route',
    path: '/capacity/self-capacity/vehicle',
    permission: 'capacity:self_capacity:vehicle:list',
    defaultVisible: true,
    sortOrder: 60
  },
  {
    key: 'contract.list',
    title: '运价合同',
    icon: 'CopyOutlined',
    color: '#ffd666',
    group: '计费中心',
    type: 'route',
    path: '/billing/contract',
    permission: 'billing:contract:list',
    defaultVisible: false,
    sortOrder: 70
  },
  {
    key: 'carrier.list',
    title: '承运商管理',
    icon: 'TagOutlined',
    color: '#ff85c0',
    group: '客商中心',
    type: 'route',
    path: '/partner/carrier',
    permission: 'partner:carrier:list',
    defaultVisible: false,
    sortOrder: 80
  },
  {
    key: 'social-capacity.list',
    title: '社会运力',
    icon: 'MailOutlined',
    color: '#597ef7',
    group: '运力中心',
    type: 'route',
    path: '/capacity/social-capacity/list',
    permission: 'capacity:social_capacity:list',
    feature: 'capacity_social_list',
    defaultVisible: false,
    sortOrder: 90
  }
];

const registryMap = new Map(
  QUICK_ACTION_REGISTRY.map((item) => [item.key, item])
);

/** 按 key 查找注册项 */
export const getQuickActionConfig = (key: string): QuickActionConfig | undefined =>
  registryMap.get(key);

/** 注册表全部 key（用于校验服务端配置） */
export const getRegistryKeys = (): string[] =>
  QUICK_ACTION_REGISTRY.map((item) => item.key);

/** 默认展示的 key 列表（仍须运行时权限过滤） */
export const getDefaultQuickActionKeys = (): string[] =>
  [...QUICK_ACTION_REGISTRY]
    .filter((item) => item.defaultVisible)
    .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0))
    .map((item) => item.key);

/** 按 group 分组的可选项 */
export const groupQuickActions = (
  items: QuickActionConfig[]
): Record<string, QuickActionConfig[]> => {
  const groups: Record<string, QuickActionConfig[]> = {};
  for (const item of items) {
    if (!groups[item.group]) {
      groups[item.group] = [];
    }
    groups[item.group].push(item);
  }
  return groups;
};
