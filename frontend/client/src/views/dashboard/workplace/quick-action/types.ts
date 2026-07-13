/**
 * 工作台快捷操作 — 类型定义
 */

export type QuickActionType = 'route' | 'external';

/** 服务端持久化的工作台配置结构 */
export interface WorkplaceConfig {
  version: number;
  quickActions: string[];
}

export interface QuickActionConfig {
  /** 全局唯一，格式：域.动作，如 waybill.create */
  key: string;
  title: string;
  /** 图标组件名（ele-admin-plus icons） */
  icon: string;
  /** 图标图片地址（设计素材，优先于 icon 渲染；暂未提供时留空用占位图标） */
  image?: string;
  color?: string;
  /** 分组标题，用于管理弹窗 */
  group: string;
  type: QuickActionType;
  /** 路由 path 或外链 URL */
  path: string;
  query?: Record<string, string>;
  /** RBAC 按钮权限码；与菜单 authority 字段对齐 */
  permission?: string | string[];
  /** 产品功能码；与 hasFeature 对齐 */
  feature?: string;
  /** 新用户默认展示（仍须通过权限过滤） */
  defaultVisible?: boolean;
  /** 默认排序权重（越小越靠前） */
  sortOrder?: number;
}

/** 解析后的展示项（注册表 + 运行时 key） */
export interface QuickActionItem extends QuickActionConfig {
  /** router-link 目标 */
  to: string | { path: string; query?: Record<string, string> };
}
