/**
 * 工作台快捷操作 — 类型定义
 */

export type QuickActionType = 'route' | 'external';

/** 服务端持久化的工作台配置结构（用户级偏好袋） */
export interface WorkplaceConfig {
  version: number;
  quickActions: string[];
  /**
   * @deprecated 旧版全局开关；读偏好时仅作未配置模块的回退。
   * 新写入请用 showModuleOverviewByModule。
   */
  showModuleOverview?: boolean;
  /**
   * 按一级模块 key（如 operation、approval）控制是否默认落地总览。
   * 缺省 / true：模块根路径 redirect 到总览；false：redirect 到首个业务子页。
   * 侧栏「总览」入口始终保留，与本字段无关。
   */
  showModuleOverviewByModule?: Record<string, boolean>;
  /** 小程序默认打开的岗位视图 */
  defaultPersona?: string;
}

export interface QuickActionConfig {
  /** 全局唯一，服务端为菜单权限码 menu_code，如 business:waybill:add */
  key: string;
  title: string;
  /** 图标组件名（ele-admin-plus icons，可选；服务端配置优先用 image） */
  icon?: string;
  /** 图标图片地址（上传的专属图标，优先于 icon 渲染；缺省用占位图标） */
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
