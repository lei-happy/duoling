/**
 * 工作台快捷操作 — 注册表
 *
 * 目录由后端下发（运营在 Console「客户端菜单」里勾选"支持快捷操作"并上传图标），
 * 本文件仅维护运行时缓存与工具函数。
 * 详见：doc/04.开发手册/15.快捷操作接入说明.md
 */

import { ref } from 'vue';
import type { QuickActionConfig } from './types';

export const QUICK_ACTION_CONFIG_VERSION = 1;

export const QUICK_ACTION_MAX = 12;

/**
 * 旧版前端硬编码 key -> 新版菜单权限码(menu_code) 映射。
 * 用于兼容历史 workplace_config，避免用户已选项丢失。
 */
const LEGACY_KEY_MAP: Record<string, string> = {
  'waybill.create': 'business:waybill:add',
  'task.create': 'operation:task:add',
  'waybill.list': 'business:waybill:list',
  'task.list': 'operation:task:list',
  'customer.list': 'partner:customer:list',
  'vehicle.list': 'capacity:self_capacity:vehicle:list',
  'contract.list': 'billing:contract:list',
  'carrier.list': 'partner:carrier:list',
  'social-capacity.list': 'capacity:social_capacity:list'
};

/** 将历史 key 归一化为当前 key（menu_code） */
export const normalizeQuickActionKey = (key: string): string =>
  LEGACY_KEY_MAP[key] ?? key;

/** 运行时注册表（由接口填充） */
const registryList = ref<QuickActionConfig[]>([]);
const registryMap = ref(new Map<string, QuickActionConfig>());

/** 写入注册表（拉取接口后调用） */
export const setQuickActionRegistry = (list: QuickActionConfig[]): void => {
  registryList.value = list;
  registryMap.value = new Map(list.map((item) => [item.key, item]));
};

/** 全部注册项 */
export const getQuickActionRegistryList = (): QuickActionConfig[] =>
  registryList.value;

/** 按 key 查找注册项 */
export const getQuickActionConfig = (
  key: string
): QuickActionConfig | undefined => registryMap.value.get(key);

/** 注册表全部 key（用于校验服务端配置） */
export const getRegistryKeys = (): string[] =>
  registryList.value.map((item) => item.key);

/** 默认展示的 key 列表（仍须运行时权限过滤） */
export const getDefaultQuickActionKeys = (): string[] =>
  [...registryList.value]
    .filter((item) => item.defaultVisible)
    .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0))
    .map((item) => item.key);

/** 按 group 分组的可选项 */
export const groupQuickActions = (
  items: QuickActionConfig[]
): Record<string, QuickActionConfig[]> => {
  const groups: Record<string, QuickActionConfig[]> = {};
  for (const item of items) {
    const name = item.group || '常用功能';
    if (!groups[name]) {
      groups[name] = [];
    }
    groups[name].push(item);
  }
  return groups;
};
