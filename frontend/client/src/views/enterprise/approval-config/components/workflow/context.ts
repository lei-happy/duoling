import type { InjectionKey } from 'vue';
import type { CanvasNode, ConditionBranch } from '@/api/approval/model';

/**
 * 画布上下文：通过 provide/inject 下发给递归的节点组件，
 * 避免在深层递归中逐层透传打开抽屉的回调。
 */
export interface WorkflowContext {
  /** 只读模式（已发布流程查看） */
  readonly: boolean;
  /** 打开审批人 / 抄送人配置抽屉 */
  openNodeConfig: (node: CanvasNode) => void;
  /** 打开条件分支配置抽屉；isDefault 表示是否为「否则」默认分支 */
  openCondition: (branch: ConditionBranch, isDefault: boolean) => void;
}

export const WORKFLOW_CTX: InjectionKey<WorkflowContext> = Symbol(
  'approval-workflow-ctx'
);
