/** 设计对接模块 */
export interface DesignModule {
  id: number;
  title: string;
  product_line: string;
  description?: string | null;
  priority: number;
  status: number;
  /** 相对仓库 prototype/ 的 HTML 路径 */
  prototype_path?: string | null;
  figma_url?: string | null;
  pm_user_id?: number | null;
  pm_name?: string | null;
  designer_user_id?: number | null;
  designer_name?: string | null;
  developer_user_id?: number | null;
  developer_name?: string | null;
  sort_order: number;
  created_by?: number | null;
  updated_by?: number | null;
  created_at: string;
  updated_at: string;
}

/** 查询参数 */
export interface DesignModuleParam {
  page?: number;
  limit?: number;
  status?: number | null;
  priority?: number | null;
  product_line?: string | null;
  keyword?: string | null;
  view?: 'list' | 'board';
}

/** 创建/更新 */
export interface DesignModuleForm {
  title: string;
  product_line?: string;
  description?: string | null;
  priority?: number;
  status?: number;
  prototype_path?: string | null;
  figma_url?: string | null;
  pm_user_id?: number | null;
  pm_name?: string | null;
  designer_user_id?: number | null;
  designer_name?: string | null;
  developer_user_id?: number | null;
  developer_name?: string | null;
}

/** 排序项 */
export interface DesignModuleSortItem {
  id: number;
  sort_order: number;
  status?: number;
}

/** 原型目录树节点（与文档树结构一致） */
export interface PrototypeTreeNode {
  title: string;
  key: string;
  isLeaf: boolean;
  children?: PrototypeTreeNode[];
}
