/**
 * 审批画布流程树 <-> 后端 processConfig 的转换、节点工厂与展示辅助。
 *
 * 画布内部节点结构与后端 processConfig 节点保持一致（见 model/index.ts），
 * 转换层主要负责：补默认值、生成稳定 nodeKey、剥离 UI 临时字段、结构校验。
 */
import type {
  CanvasNode,
  CanvasNodeType,
  ConditionBranch,
  FlowNode,
  ProcessConfig
} from './model';

/** 审批人类型枚举（对齐后端 constants.py APPROVER_*） */
export interface ApproverTypeOption {
  value: number;
  label: string;
  disabled?: boolean;
  tip?: string;
}
export const APPROVER_TYPES: ApproverTypeOption[] = [
  { value: 1, label: '指定成员' },
  { value: 2, label: '指定角色' },
  { value: 3, label: '指定部门' },
  {
    value: 4,
    label: '部门负责人',
    disabled: true,
    tip: '依赖组织扩展，第2期生效'
  },
  {
    value: 5,
    label: '逐级上级主管',
    disabled: true,
    tip: '依赖组织扩展，第2期生效'
  },
  { value: 6, label: '发起人自选' },
  { value: 7, label: '发起人本人' }
];

export const SIGN_TYPES = [
  { value: 1, label: '或签（一人通过即可）' },
  { value: 2, label: '会签（需全部通过）' },
  { value: 3, label: '依次会签（按顺序逐个）' }
];

export const EMPTY_STRATEGIES = [
  { value: 1, label: '自动通过' },
  { value: 3, label: '报错阻断' }
];

export const CONDITION_OPS = [
  { value: '==', label: '等于' },
  { value: '!=', label: '不等于' },
  { value: '>', label: '大于' },
  { value: '>=', label: '大于等于' },
  { value: '<', label: '小于' },
  { value: '<=', label: '小于等于' },
  { value: 'in', label: '属于' },
  { value: 'not_in', label: '不属于' }
];

let _seq = 0;
/** 生成稳定唯一 nodeKey */
export function genKey(prefix = 'n'): string {
  _seq += 1;
  return `${prefix}_${Date.now().toString(36)}_${_seq}`;
}

export function createStartNode(): CanvasNode {
  return {
    nodeKey: 'start',
    type: 'start',
    nodeName: '发起人',
    childNode: null
  };
}

export function createNode(type: CanvasNodeType): CanvasNode {
  if (type === 'approval') {
    return {
      nodeKey: genKey('ap'),
      type: 'approval',
      nodeName: '审批人',
      approverType: 2,
      approverConfig: null,
      signType: 1,
      emptyStrategy: 3,
      allowTransfer: 1,
      allowAddsign: 1,
      childNode: null
    };
  }
  if (type === 'cc') {
    return {
      nodeKey: genKey('cc'),
      type: 'cc',
      nodeName: '抄送人',
      approverType: 1,
      approverConfig: null,
      signType: 1,
      emptyStrategy: 1,
      allowTransfer: 0,
      allowAddsign: 0,
      childNode: null
    };
  }
  // condition router：默认 2 个分支（条件1 + 否则）
  return {
    nodeKey: genKey('cond'),
    type: 'condition',
    nodeName: '条件分支',
    conditionNodes: [createBranch(1), createBranch(2, true)],
    childNode: null
  };
}

export function createBranch(
  priority: number,
  isDefault = false
): ConditionBranch {
  return {
    nodeKey: genKey('br'),
    nodeName: isDefault ? '其它情况' : `条件${priority}`,
    priority,
    condition: isDefault ? null : { logic: 'and', rules: [] },
    childNode: null
  };
}

/** 后端 processConfig -> 画布根节点；空时回退用旧线性 nodes 构建，再空则给默认起点 */
export function configToTree(
  config?: ProcessConfig | null,
  legacyNodes?: FlowNode[] | null
): CanvasNode {
  if (config && config.root) {
    return normalizeNode(config.root);
  }
  if (legacyNodes && legacyNodes.length) {
    return nodesToTree(legacyNodes);
  }
  return createStartNode();
}

/** 旧线性 nodes -> 画布单链树（节点级条件包装为条件路由） */
export function nodesToTree(nodes: FlowNode[]): CanvasNode {
  const root = createStartNode();
  let head: CanvasNode = root;
  const sorted = [...nodes].sort((a, b) => a.nodeOrder - b.nodeOrder);
  for (const n of sorted) {
    const node: CanvasNode = {
      nodeKey: genKey('n'),
      type: n.nodeType === 2 ? 'cc' : 'approval',
      nodeName: n.nodeName,
      approverType: n.approverType,
      approverConfig: n.approverConfig ?? null,
      signType: n.signType,
      emptyStrategy: n.emptyStrategy,
      allowTransfer: n.allowTransfer,
      allowAddsign: n.allowAddsign,
      childNode: null
    };
    const cond = n.condition;
    if (cond && (cond as any).rules?.length) {
      const router = createNode('condition');
      const branches = router.conditionNodes!;
      branches[0].condition = cond as any;
      branches[0].childNode = node;
      head.childNode = router;
      head = router;
    } else {
      head.childNode = node;
      head = node;
    }
  }
  return root;
}

function normalizeNode(node: CanvasNode): CanvasNode {
  const n: CanvasNode = { ...node };
  if (!n.nodeKey) n.nodeKey = genKey();
  if (n.type === 'condition') {
    n.conditionNodes = (n.conditionNodes || []).map((b) => ({
      ...b,
      nodeKey: b.nodeKey || genKey('br'),
      childNode: b.childNode ? normalizeNode(b.childNode) : null
    }));
  }
  n.childNode = n.childNode ? normalizeNode(n.childNode) : null;
  return n;
}

/** 画布根节点 -> 后端 processConfig（深拷贝 + 剥离 UI 字段） */
export function treeToConfig(root: CanvasNode): ProcessConfig {
  return { version: 1, root: stripNode(root) };
}

function stripNode(node: CanvasNode): CanvasNode {
  const base: CanvasNode = {
    nodeKey: node.nodeKey,
    type: node.type,
    nodeName: node.nodeName,
    childNode: node.childNode ? stripNode(node.childNode) : null
  };
  if (node.type === 'approval' || node.type === 'cc') {
    base.approverType = node.approverType;
    base.approverConfig = node.approverConfig ?? null;
    base.signType = node.signType;
    base.emptyStrategy = node.emptyStrategy;
    base.allowTransfer = node.allowTransfer;
    base.allowAddsign = node.allowAddsign;
  }
  if (node.type === 'condition') {
    base.conditionNodes = (node.conditionNodes || []).map((b, idx) => ({
      nodeKey: b.nodeKey,
      nodeName: b.nodeName,
      priority: idx + 1,
      condition: b.condition && b.condition.rules?.length ? b.condition : null,
      childNode: b.childNode ? stripNode(b.childNode) : null
    }));
  }
  return base;
}

/** 审批人/抄送人摘要文案 */
export function approverSummary(node: CanvasNode): string {
  const cfg = node.approverConfig || {};
  switch (node.approverType) {
    case 1:
      return cfg.user_ids?.length ? `${cfg.user_ids.length} 名成员` : '';
    case 2:
      return cfg.role_ids?.length ? `${cfg.role_ids.length} 个角色` : '';
    case 3:
      return cfg.dept_ids?.length ? `${cfg.dept_ids.length} 个部门` : '';
    case 4:
      return '部门负责人';
    case 5:
      return '逐级上级主管';
    case 6:
      return '发起人自选';
    case 7:
      return '发起人本人';
    default:
      return '';
  }
}

/** 条件分支摘要文案 */
export function conditionSummary(branch: ConditionBranch): string {
  if (!branch.condition || !branch.condition.rules?.length) {
    return '其它条件进入此流程';
  }
  const opLabel = (op: string) =>
    CONDITION_OPS.find((o) => o.value === op)?.label || op;
  const joiner = branch.condition.logic === 'or' ? ' 或 ' : ' 且 ';
  return branch.condition.rules
    .map((r) => `${r.field} ${opLabel(r.op)} ${formatValue(r.value)}`)
    .join(joiner);
}

function formatValue(v: any): string {
  if (Array.isArray(v)) return `[${v.join(', ')}]`;
  return String(v ?? '');
}

/** 结构校验：返回错误信息（空=通过），用于发布前提示 */
export function validateTree(root: CanvasNode): string[] {
  const errors: string[] = [];
  let hasApproval = false;
  const walk = (node?: CanvasNode | null) => {
    if (!node) return;
    if (node.type === 'approval') {
      hasApproval = true;
      const cfg = node.approverConfig || {};
      const name = node.nodeName || '审批节点';
      if (node.approverType === 1 && !cfg.user_ids?.length)
        errors.push(`「${name}」未选择审批成员`);
      else if (node.approverType === 2 && !cfg.role_ids?.length)
        errors.push(`「${name}」未选择审批角色`);
      else if (node.approverType === 3 && !cfg.dept_ids?.length)
        errors.push(`「${name}」未选择审批部门`);
    }
    if (node.type === 'cc') {
      const cfg = node.approverConfig || {};
      const name = node.nodeName || '抄送节点';
      if (node.approverType === 1 && !cfg.user_ids?.length)
        errors.push(`「${name}」未选择抄送成员`);
    }
    if (node.type === 'condition') {
      (node.conditionNodes || []).forEach((b, idx) => {
        const isLast = idx === node.conditionNodes!.length - 1;
        if (!isLast && !b.condition?.rules?.length) {
          errors.push(`「${b.nodeName}」未设置条件`);
        }
        walk(b.childNode);
      });
    }
    walk(node.childNode);
  };
  walk(root);
  if (!hasApproval) errors.push('流程至少需要一个审批节点');
  return errors;
}
