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
