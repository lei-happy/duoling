/**
 * 用户 workplace_config 合并与读取工具。
 * 工作台快捷操作与模块总览偏好共用同一 JSON，写回时必须 merge，避免互相覆盖。
 */
import type { WorkplaceConfig } from '@/views/dashboard/workplace/quick-action/types';
import { QUICK_ACTION_CONFIG_VERSION } from '@/views/dashboard/workplace/quick-action/quick-action-registry';

/**
 * 某模块是否默认落地总览。
 * 优先级：按模块 map → 旧版全局布尔 → 默认 true。
 */
export function isShowModuleOverviewEnabled(
  config: unknown,
  moduleKey: string
): boolean {
  if (!moduleKey) {
    return true;
  }
  if (!config || typeof config !== 'object') {
    return true;
  }
  const c = config as WorkplaceConfig;
  const map = c.showModuleOverviewByModule;
  if (map && typeof map === 'object' && !Array.isArray(map)) {
    const hit = map[moduleKey];
    if (typeof hit === 'boolean') {
      return hit;
    }
  }
  if (typeof c.showModuleOverview === 'boolean') {
    return c.showModuleOverview;
  }
  return true;
}

function normalizeOverviewByModule(
  raw: unknown
): Record<string, boolean> | undefined {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
    return undefined;
  }
  const result: Record<string, boolean> = {};
  Object.entries(raw as Record<string, unknown>).forEach(([key, value]) => {
    if (typeof key === 'string' && key.trim() && typeof value === 'boolean') {
      result[key] = value;
    }
  });
  return result;
}

/**
 * 合并写入 workplace_config。
 * patch 中未出现的字段保留 current 原值；
 * `showModuleOverviewByModule` 按 key 浅合并。
 */
export function mergeWorkplaceConfig(
  current: unknown,
  patch: Partial<WorkplaceConfig>
): WorkplaceConfig {
  const base =
    current && typeof current === 'object'
      ? (current as Partial<WorkplaceConfig>)
      : {};
  const version =
    typeof patch.version === 'number'
      ? patch.version
      : typeof base.version === 'number'
        ? base.version
        : QUICK_ACTION_CONFIG_VERSION;
  const quickActions = Array.isArray(patch.quickActions)
    ? patch.quickActions
    : Array.isArray(base.quickActions)
      ? base.quickActions
      : [];
  const merged: WorkplaceConfig = {
    version,
    quickActions
  };

  const baseMap = normalizeOverviewByModule(base.showModuleOverviewByModule);
  const patchMap = normalizeOverviewByModule(patch.showModuleOverviewByModule);
  if (patchMap || baseMap) {
    merged.showModuleOverviewByModule = {
      ...(baseMap || {}),
      ...(patchMap || {})
    };
  }

  // 旧版全局字段：仅在未写新 map 时继续保留，供未单独配置的模块回退
  if (patch.showModuleOverview !== undefined) {
    merged.showModuleOverview = !!patch.showModuleOverview;
  } else if (typeof base.showModuleOverview === 'boolean') {
    merged.showModuleOverview = base.showModuleOverview;
  }

  const defaultPersona =
    typeof patch.defaultPersona === 'string'
      ? patch.defaultPersona
      : typeof base.defaultPersona === 'string'
        ? base.defaultPersona
        : undefined;
  if (defaultPersona) {
    merged.defaultPersona = defaultPersona;
  }

  return merged;
}

/** 仅更新某一模块的总览落地偏好（写入 showModuleOverviewByModule） */
export function setModuleOverviewPreference(
  current: unknown,
  moduleKey: string,
  enabled: boolean
): WorkplaceConfig {
  return mergeWorkplaceConfig(current, {
    showModuleOverviewByModule: { [moduleKey]: enabled }
  });
}
