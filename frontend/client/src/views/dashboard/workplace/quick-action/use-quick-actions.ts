/**
 * 工作台快捷操作 — 状态与权限逻辑
 */

import { computed, ref, watch } from 'vue';
import { storeToRefs } from 'pinia';
import type { MenuItem } from 'ele-admin-plus/es/ele-pro-layout/types';
import { useUserStore } from '@/store/modules/user';
import { usePermission } from '@/utils/use-permission';
import {
  getQuickActionRegistry,
  saveWorkplaceConfig
} from '@/api/home/workbench/quick-action';
import { mergeWorkplaceConfig } from '@/utils/workplace-config';
import {
  getDefaultQuickActionKeys,
  getQuickActionConfig,
  getQuickActionRegistryList,
  getRegistryKeys,
  normalizeQuickActionKey,
  setQuickActionRegistry,
  QUICK_ACTION_MAX
} from './quick-action-registry';
import type {
  QuickActionConfig,
  QuickActionItem,
  WorkplaceConfig
} from './types';

const LEGACY_CACHE_KEY = 'workplace-links';

/** 判断 path 是否在用户菜单树中 */
function isPathInUserMenus(path: string, menus?: MenuItem[] | null): boolean {
  if (!menus?.length) {
    return false;
  }
  const normalized = path.replace(/\/+$/, '') || '/';
  let found = false;
  const walk = (items: MenuItem[]) => {
    for (const item of items) {
      const itemPath = (item.path || '').replace(/\/+$/, '') || '/';
      if (itemPath === normalized) {
        found = true;
        return;
      }
      if (item.children?.length) {
        walk(item.children);
      }
    }
  };
  walk(menus);
  return found;
}

function resolveTo(config: QuickActionConfig): QuickActionItem['to'] {
  if (config.query && Object.keys(config.query).length) {
    return { path: config.path, query: config.query };
  }
  return config.path;
}

function toQuickActionItem(config: QuickActionConfig): QuickActionItem {
  return { ...config, to: resolveTo(config) };
}

function buildWorkplaceConfig(
  keys: string[],
  current?: unknown
): WorkplaceConfig {
  return mergeWorkplaceConfig(current, { quickActions: keys });
}

function sanitizeKeys(keys: unknown): string[] {
  if (!Array.isArray(keys)) {
    return [];
  }
  const registryKeys = new Set(getRegistryKeys());
  const seen = new Set<string>();
  const result: string[] = [];
  for (const raw of keys) {
    if (typeof raw !== 'string') {
      continue;
    }
    // 兼容历史 workplace_config 里的旧 key
    const key = normalizeQuickActionKey(raw);
    if (!registryKeys.has(key) || seen.has(key)) {
      continue;
    }
    seen.add(key);
    result.push(key);
    if (result.length >= QUICK_ACTION_MAX) {
      break;
    }
  }
  return result;
}

function parseServerConfig(raw: unknown): string[] {
  if (!raw || typeof raw !== 'object') {
    return [];
  }
  const config = raw as WorkplaceConfig;
  return sanitizeKeys(config.quickActions);
}

export function useQuickActions() {
  const userStore = useUserStore();
  const { menus } = storeToRefs(userStore);
  const { hasPermission, hasAnyPermission } = usePermission();

  const selectedKeys = ref<string[]>([]);
  const initialized = ref(false);
  const pickerVisible = ref(false);

  const isActionAccessible = (config: QuickActionConfig): boolean => {
    if (config.feature && !userStore.hasFeature(config.feature)) {
      return false;
    }
    if (config.permission) {
      return Array.isArray(config.permission)
        ? hasAnyPermission(config.permission)
        : hasPermission(config.permission);
    }
    return isPathInUserMenus(config.path, menus.value);
  };

  const accessibleRegistry = computed(() =>
    getQuickActionRegistryList().filter(isActionAccessible)
  );

  const accessibleKeySet = computed(
    () => new Set(accessibleRegistry.value.map((item) => item.key))
  );

  const displayedItems = computed(() =>
    selectedKeys.value
      .filter((key) => accessibleKeySet.value.has(key))
      .map((key) => getQuickActionConfig(key))
      .filter((item): item is QuickActionConfig => !!item)
      .map(toQuickActionItem)
  );

  const availableToAdd = computed(() =>
    accessibleRegistry.value.filter(
      (item) => !selectedKeys.value.includes(item.key)
    )
  );

  const persist = () => {
    const config = buildWorkplaceConfig(
      selectedKeys.value,
      userStore.info?.workplaceConfig
    );
    saveWorkplaceConfig(config);
    // 仅同步 workplaceConfig，避免 setInfo 整对象替换触发无关 UI（如问候语）刷新
    if (userStore.info) {
      userStore.info.workplaceConfig = config;
    }
  };

  const setSelectedKeys = (keys: string[], save = true) => {
    selectedKeys.value = sanitizeKeys(keys);
    if (save && initialized.value) {
      persist();
    }
  };

  const initFromUser = async () => {
    initialized.value = false;
    try {
      const registry = await getQuickActionRegistry();
      setQuickActionRegistry(registry);
    } catch (e) {
      console.error('加载快捷操作目录失败', e);
      setQuickActionRegistry([]);
    }
    const serverKeys = parseServerConfig(userStore.info?.workplaceConfig);
    if (serverKeys.length) {
      setSelectedKeys(serverKeys, false);
    } else {
      const defaults = getDefaultQuickActionKeys().filter((key) => {
        const config = getQuickActionConfig(key);
        return config && isActionAccessible(config);
      });
      setSelectedKeys(defaults, false);
      if (defaults.length) {
        // initialized 置真后再持久化，避免 setSelectedKeys 二次写入
        initialized.value = true;
        persist();
      }
    }
    localStorage.removeItem(LEGACY_CACHE_KEY);
    initialized.value = true;
  };

  const addAction = (key: string) => {
    if (
      selectedKeys.value.includes(key) ||
      selectedKeys.value.length >= QUICK_ACTION_MAX
    ) {
      return;
    }
    const config = getQuickActionConfig(key);
    if (!config || !isActionAccessible(config)) {
      return;
    }
    setSelectedKeys([...selectedKeys.value, key]);
  };

  const removeAction = (key: string) => {
    setSelectedKeys(selectedKeys.value.filter((k) => k !== key));
  };

  const reorder = (oldIndex: number, newIndex: number) => {
    const temp = [...selectedKeys.value];
    temp.splice(newIndex, 0, temp.splice(oldIndex, 1)[0]);
    setSelectedKeys(temp);
  };

  const reset = () => {
    const defaults = getDefaultQuickActionKeys().filter((key) => {
      const config = getQuickActionConfig(key);
      return config && isActionAccessible(config);
    });
    setSelectedKeys(defaults);
  };

  const openPicker = () => {
    pickerVisible.value = true;
  };

  watch([menus, () => userStore.authorities, () => userStore.features], () => {
    if (!initialized.value) {
      return;
    }
    selectedKeys.value = selectedKeys.value.filter((key) =>
      accessibleKeySet.value.has(key)
    );
  });

  return {
    selectedKeys,
    displayedItems,
    availableToAdd,
    accessibleRegistry,
    pickerVisible,
    quickActionMax: QUICK_ACTION_MAX,
    initFromUser,
    addAction,
    removeAction,
    reorder,
    reset,
    openPicker,
    isActionAccessible
  };
}
