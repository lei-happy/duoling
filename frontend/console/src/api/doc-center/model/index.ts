/**
 * 文档目录树节点
 */
export interface DocTreeNode {
  /** 显示标题 */
  title: string;
  /** 相对路径（作为唯一标识） */
  key: string;
  /** 是否为叶子节点（md 文件） */
  isLeaf: boolean;
  /** 子节点 */
  children?: DocTreeNode[];
}

/**
 * 文档内容
 */
export interface DocContent {
  /** 文件相对路径 */
  path: string;
  /** Markdown 原始内容 */
  content: string;
}
