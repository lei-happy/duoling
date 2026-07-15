/**
 * 客户端菜单
 */
export interface ClientMenu {
  menuId?: number;
  parentId?: number;
  title?: string;
  path: string;
  component?: string;
  /** 0菜单, 1按钮 */
  menuType?: number;
  sortNumber?: number;
  authority?: string;
  icon?: string;
  /** 0否,1是 */
  hide?: number;
  /** 关联功能编码 */
  featureCode?: string;
  meta?: any;
  createTime?: string;
  children?: ClientMenu[];
  /** 前端表单辅助字段 */
  openType?: number;
  /** 快捷操作：是否支持设为首页快捷操作 */
  quickActionEnabled?: boolean;
  /** 快捷操作：专属图标 URL */
  quickActionIcon?: string;
  /** 快捷操作：显示名称（空则用菜单名） */
  quickActionName?: string;
  /** 快捷操作：图标底色 */
  quickActionColor?: string;
  /** 快捷操作：跳转链接（空则用路由地址，可带 query） */
  quickActionLink?: string;
  /** 快捷操作：管理弹窗分组 */
  quickActionGroup?: string;
  /** 快捷操作：排序权重 */
  quickActionSort?: number;
  /** 快捷操作：新用户默认展示 */
  quickActionDefault?: boolean;
}

/**
 * 客户端菜单搜索参数
 */
export interface ClientMenuParam {
  title?: string;
  path?: string;
  authority?: string;
  featureCode?: string;
  parentId?: number;
}
