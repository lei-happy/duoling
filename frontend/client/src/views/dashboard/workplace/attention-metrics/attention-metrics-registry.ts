import type { RouteLocationRaw } from 'vue-router';

/** 今日需关注指标 — 注册表项 */
export interface AttentionMetricConfig {
  /** 全局唯一，格式：域.语义 */
  key: string;
  label: string;
  /** Element Plus 图标组件名 */
  icon: string;
  tagType: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  permission?: string | string[];
  feature?: string;
  sortOrder: number;
  /** 点击跳转目标 */
  route: RouteLocationRaw;
}

/** 全部可注册的今日需关注指标（展示顺序由 sortOrder 决定） */
export const ATTENTION_METRICS_REGISTRY: AttentionMetricConfig[] = [
  {
    key: 'waybill.pending_confirm',
    label: '待确认计划',
    icon: 'DocumentChecked',
    tagType: 'warning',
    permission: 'business:waybill:list',
    feature: 'biz_waybill',
    sortOrder: 10,
    route: { path: '/operation/waybill', query: { pool: 'pending-confirm' } }
  },
  {
    key: 'task.dispatch_transit',
    label: '调度在途',
    icon: 'Promotion',
    tagType: 'primary',
    permission: 'operation:task:list',
    feature: 'biz_dispatch',
    sortOrder: 20,
    route: {
      path: '/operation/task-workbench',
      query: { tab: 'pending-dispatch' }
    }
  },
  {
    key: 'approval.pending',
    label: '待我审批',
    icon: 'Select',
    tagType: 'success',
    sortOrder: 30,
    route: {
      path: '/operation/task-finance-workbench',
      query: { tab: 'pending-review' }
    }
  }
];
