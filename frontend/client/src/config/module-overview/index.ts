import type { ModuleOverviewConfig } from './types';
import operation from './operation';
import capacity from './capacity';
import partner from './partner';
import billing from './billing';
import approval from './approval';
import finance from './finance';
import insight from './insight';
import ecosystem from './ecosystem';
import logCenter from './log-center';
import enterprise from './enterprise';
import openPlatform from './open-platform';
import energy from './energy';

/**
 * 各一级模块的总览配置注册表。
 * 未在此登记的模块，总览页会基于菜单 children 自动兜底渲染。
 */
const configs: Record<string, ModuleOverviewConfig> = {
  operation,
  capacity,
  partner,
  billing,
  approval,
  finance,
  insight,
  ecosystem,
  'log-center': logCenter,
  enterprise,
  'open-platform': openPlatform,
  energy
};

/**
 * 按模块 key 获取总览配置
 * @param key 模块 key（路径去掉前导斜杠，如 operation）
 */
export function resolveOverviewConfig(
  key?: string
): ModuleOverviewConfig | undefined {
  if (!key) {
    return void 0;
  }
  return configs[key];
}

export type { ModuleOverviewConfig } from './types';
