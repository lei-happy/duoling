/**
 * 界面示意（mock）面板的数据形状。
 *
 * 这些截图式的区块在产品能力页和首页反复出现，用数据描述比手写一堆
 * div 更容易保证四条主线之间的视觉一致。它们纯装饰，渲染时对读屏隐藏。
 */

export interface MockKpi {
  label: string;
  value: string;
  tone?: 'up' | 'down';
}

export interface MockNode {
  text: string;
  state?: 'done' | 'live';
}

export interface MockRow {
  /** 表头行：灰底、等宽字体 */
  head?: boolean;
  /** 整行只有一段长文本时铺满，不走四列网格 */
  full?: boolean;
  cells: string[];
  /** 需要等宽数字对齐的列下标 */
  nums?: number[];
  tag?: { text: string; kind?: 'brand' | 'pro' };
}

/** 各字段按声明顺序渲染：流程条 → 指标 → 柱图 → 表格 → 尾部流程条/指标 */
export interface MockPanel {
  title: string;
  flow?: MockNode[];
  kpis?: MockKpi[];
  bars?: number[];
  rows?: MockRow[];
  rows2?: MockRow[];
  flowTail?: MockNode[];
  kpisTail?: MockKpi[];
}
