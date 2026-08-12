import type { PageParam } from '@/api';

/** 预警实例（后端 biz_task_alert 的一行） */
export interface TaskAlert {
  id: number;
  taskId: number;
  taskNo?: string;
  /** 触发时任务所处阶段（task.status） */
  stage: number;
  stageLabel?: string;
  ruleCode: string;
  ruleName?: string;
  /** 命中的覆盖规则 ID，为空表示用的是默认阈值 */
  ruleId?: number | null;
  /** 1-关注 2-严重 */
  level: number;
  levelLabel?: string;
  /** 0-待处理 1-已处理 2-已忽略 3-已自动消除 */
  status: number;
  statusLabel?: string;
  /** 应完成时间 */
  dueAt?: string;
  overdueMinutes: number;
  triggeredAt?: string;
  /** 由「关注」升级为「严重」的时间 */
  escalatedAt?: string;
  handlerName?: string;
  claimedAt?: string;
  resolvedAt?: string;
  resolveType?: string;
  resolveRemark?: string;
  /** 触发时的现场快照（客户、线路、台数等），规则改了历史仍能解释 */
  snapshot?: Record<string, any> | null;
}

export interface TaskAlertParam extends PageParam {
  stage?: number;
  level?: number;
  status?: number;
  ruleCode?: string;
  keyword?: string;
}

/** 规则类型目录项（内置默认阈值，配置页据此渲染表单） */
export interface TaskAlertRuleCatalogItem {
  ruleCode: string;
  ruleName: string;
  /** deadline-截止型 anchor-锚点型 stagnant-滞留型 execution-执行异常型 */
  kind: 'deadline' | 'anchor' | 'stagnant' | 'execution';
  description: string;
  stages: number[];
  /** 是否需要逐阶段配置（仅滞留类） */
  stageScoped: boolean;
  /** 是否可配内部计划 / 客户要求两路时钟（仅截止型） */
  supportsTimeBasis: boolean;
  defaults: {
    timeBasis: number;
    planEnabled?: boolean;
    requiredEnabled?: boolean;
    anchorOffsetMinutes?: number | null;
    warnAheadMinutes?: number | null;
    criticalAfterMinutes?: number | null;
    warnAheadRequiredMinutes?: number | null;
    criticalAfterRequiredMinutes?: number | null;
    stagnantHours?: Record<string, number> | null;
  };
}

/** 阈值规则（后端 biz_task_alert_rule） */
export interface TaskAlertRule {
  id?: number;
  ruleCode: string;
  ruleName?: string | null;
  /** 仅滞留类规则需要限定阶段 */
  stage?: number | null;

  customerId?: number | null;
  customerType?: number | null;
  originRegionId?: number | null;
  destinationRegionId?: number | null;
  distanceMin?: number | null;
  distanceMax?: number | null;
  brandId?: number | null;
  seriesId?: number | null;
  carrierType?: number | null;

  /** 0-只看内部 1-只看客户 2-两路都看（由两路开关派生） */
  timeBasis: number;
  planEnabled?: boolean;
  requiredEnabled?: boolean;
  anchorOffsetMinutes?: number | null;
  warnAheadMinutes?: number | null;
  criticalAfterMinutes?: number | null;
  warnAheadRequiredMinutes?: number | null;
  criticalAfterRequiredMinutes?: number | null;
  stagnantHours?: number | null;

  priority: number;
  status: number;
  effectiveDate?: string | null;
  expiryDate?: string | null;
  remark?: string | null;

  ruleVersion?: number;
  /** 未限定任何维度 = 租户默认阈值 */
  isDefault?: boolean;
  scopeSummary?: string | null;
  createdAt?: string;
}

export interface TaskAlertRuleParam extends PageParam {
  ruleCode?: string;
  status?: number;
  /** true 只看默认阈值，false 只看覆盖规则，留空取全部 */
  isDefault?: boolean;
}

export interface TaskAlertRuleConflict {
  hasConflict: boolean;
  conflicts: TaskAlertRule[];
  message?: string | null;
}

export interface TaskAlertBatchResult {
  success: number;
  failed?: number;
}
