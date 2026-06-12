/**
 * 审批画布流程树 <-> 后端 processConfig 的转换、节点工厂与展示辅助。
 *
 * 画布内部节点结构与后端 processConfig 节点保持一致（见 model/index.ts），
 * 转换层主要负责：补默认值、生成稳定 nodeKey、剥离 UI 临时字段、结构校验。
 */
import { cloneDeep } from 'lodash-es';
import { getUser } from '@/api/system/user';
import type {
  CanvasNode,
  CanvasNodeType,
  ConditionBranch,
  FlowNode,
  InitiatorType,
  ProcessConfig
} from './model';
function stripApproverConfig(
  cfg?: Record<string, any> | null
): Record<string, any> | null {
  if (!cfg) return null;
  const { user_labels, ...rest } = cfg;
  return rest;
}

function stripInitiatorConfig(
  cfg?: Record<string, any> | null
): Record<string, any> | null {
  if (!cfg) return null;
  const { user_labels, ...rest } = cfg;
  return rest;
}

/** 深拷贝节点/分支，供配置抽屉编辑草稿使用 */
export function cloneCanvasNode(node: CanvasNode): CanvasNode {
  return cloneDeep(node);
}

export function cloneConditionBranch(branch: ConditionBranch): ConditionBranch {
  return cloneDeep(branch);
}

/** 将抽屉草稿写回画布上的原节点（保持 childNode 等结构引用不变） */
export function applyCanvasNodeDraft(target: CanvasNode, draft: CanvasNode) {
  target.nodeName = draft.nodeName;
  if (draft.type === 'start') {
    target.initiatorType = draft.initiatorType;
    target.initiatorConfig = draft.initiatorConfig
      ? cloneDeep(draft.initiatorConfig)
      : null;
  }
  if (draft.type === 'approval' || draft.type === 'cc') {
    target.approverType = draft.approverType;
    target.approverConfig = draft.approverConfig
      ? cloneDeep(draft.approverConfig)
      : null;
    target.signType = draft.signType;
    target.emptyStrategy = draft.emptyStrategy;
    target.allowTransfer = draft.allowTransfer;
    target.allowAddsign = draft.allowAddsign;
  }
}

export function applyConditionBranchDraft(
  target: ConditionBranch,
  draft: ConditionBranch
) {
  target.nodeName = draft.nodeName;
  target.condition = draft.condition ? cloneDeep(draft.condition) : null;
}

/** 解析成员姓名并写入 user_labels，供画布节点展示 */
export async function enrichMemberDisplayLabels(root: CanvasNode) {
  const idSet = new Set<number>();
  const walk = (node?: CanvasNode | null) => {
    if (!node) return;
    if (
      (node.type === 'approval' || node.type === 'cc') &&
      node.approverType === 1
    ) {
      (node.approverConfig?.user_ids ?? []).forEach((id) => idSet.add(id));
    }
    if (node.type === 'start' && node.initiatorType === 'user') {
      (node.initiatorConfig?.user_ids ?? []).forEach((id) => idSet.add(id));
    }
    if (node.type === 'condition') {
      (node.conditionNodes || []).forEach((b) => walk(b.childNode));
    }
    walk(node.childNode);
  };
  walk(root);
  if (!idSet.size) return;

  const labelMap = new Map<number, string>();
  await Promise.all(
    [...idSet].map(async (id) => {
      try {
        const u = await getUser(id);
        labelMap.set(id, u.nickname || String(id));
      } catch {
        labelMap.set(id, String(id));
      }
    })
  );

  const assignLabels = (cfg: Record<string, any> | null | undefined) => {
    const ids = cfg?.user_ids ?? [];
    if (!ids.length) return;
    cfg!.user_labels = ids.map((id: number) => labelMap.get(id) ?? String(id));
  };

  const walkAssign = (node?: CanvasNode | null) => {
    if (!node) return;
    if (
      (node.type === 'approval' || node.type === 'cc') &&
      node.approverType === 1
    ) {
      if (!node.approverConfig) node.approverConfig = {};
      assignLabels(node.approverConfig);
    }
    if (node.type === 'start' && node.initiatorType === 'user') {
      if (!node.initiatorConfig) node.initiatorConfig = {};
      assignLabels(node.initiatorConfig);
    }
    if (node.type === 'condition') {
      (node.conditionNodes || []).forEach((b) => walkAssign(b.childNode));
    }
    walkAssign(node.childNode);
  };
  walkAssign(root);
}

export async function syncMemberLabels(
  cfg: Record<string, any>,
  userIds: number[]
) {
  if (!userIds.length) {
    delete cfg.user_labels;
    return;
  }
  const labels = await Promise.all(
    userIds.map(async (id) => {
      try {
        const u = await getUser(id);
        return u.nickname || String(id);
      } catch {
        return String(id);
      }
    })
  );
  cfg.user_labels = labels;
}

function memberSummary(cfg: Record<string, any>): string {
  const ids = cfg.user_ids ?? [];
  if (!ids.length) return '';
  const labels = cfg.user_labels as string[] | undefined;
  if (labels?.length) {
    return labels.join('、');
  }
  return `${ids.length} 名成员`;
}

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
  { value: 4, label: '部门负责人' },
  { value: 5, label: '逐级上级主管' }
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
    initiatorType: 'all',
    initiatorConfig: null,
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
  if (n.type === 'start') {
    n.initiatorType = n.initiatorType || 'all';
    if (n.initiatorType === 'all') n.initiatorConfig = null;
  }
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
  if (node.type === 'start') {
    base.initiatorType = node.initiatorType || 'all';
    base.initiatorConfig =
      base.initiatorType === 'all'
        ? null
        : stripInitiatorConfig(node.initiatorConfig);
  }
  if (node.type === 'approval' || node.type === 'cc') {
    base.approverType = node.approverType;
    base.approverConfig = stripApproverConfig(node.approverConfig);
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

/** 发起人范围摘要文案 */
export function initiatorSummary(node: CanvasNode): string {
  const type: InitiatorType = node.initiatorType || 'all';
  const cfg = node.initiatorConfig || {};
  if (type === 'all') return '所有人';
  if (type === 'user') {
    return cfg.user_ids?.length
      ? memberSummary(cfg)
      : '请设置指定成员';
  }
  if (type === 'role') {
    return cfg.role_ids?.length
      ? `${cfg.role_ids.length} 个指定角色`
      : '请设置指定角色';
  }
  if (type === 'dept') {
    return cfg.dept_ids?.length
      ? `${cfg.dept_ids.length} 个指定部门`
      : '请设置指定部门';
  }
  return '所有人';
}

/** 审批人/抄送人摘要文案 */
export function approverSummary(node: CanvasNode): string {
  const cfg = node.approverConfig || {};
  switch (node.approverType) {
    case 1:
      return memberSummary(cfg);
    case 2:
      return cfg.role_ids?.length ? `${cfg.role_ids.length} 个角色` : '';
    case 3:
      return cfg.dept_ids?.length ? `${cfg.dept_ids.length} 个部门` : '';
    case 4:
      if (cfg.dept_ref === 'initiator' || !cfg.dept_id) {
        return '发起人部门负责人';
      }
      return '指定部门负责人';
    case 5: {
      const level = Number(cfg.level ?? 1);
      return level <= 1 ? '直接上级主管' : `第${level}级上级主管`;
    }
    default:
      return '';
  }
}

/** 条件分支摘要文案 */
export function conditionSummary(
  branch: ConditionBranch,
  fieldOptions?: Array<{ field: string; label: string }>
): string {
  if (!branch.condition || !branch.condition.rules?.length) {
    return '其它条件进入此流程';
  }
  const labelOf = (field: string) =>
    fieldOptions?.find((f) => f.field === field)?.label ?? field;
  const opLabel = (op: string) =>
    CONDITION_OPS.find((o) => o.value === op)?.label || op;
  const joiner = branch.condition.logic === 'or' ? ' 或 ' : ' 且 ';
  return branch.condition.rules
    .map((r) => `${labelOf(r.field)} ${opLabel(r.op)} ${formatValue(r.value)}`)
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
    if (node.type === 'start') {
      const type = node.initiatorType || 'all';
      const cfg = node.initiatorConfig || {};
      if (type === 'user' && !cfg.user_ids?.length)
        errors.push('发起人未设置指定成员');
      else if (type === 'role' && !cfg.role_ids?.length)
        errors.push('发起人未设置指定角色');
      else if (type === 'dept' && !cfg.dept_ids?.length)
        errors.push('发起人未设置指定部门');
    }
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
      else if (
        node.approverType === 4 &&
        cfg.dept_ref === 'dept_id' &&
        !cfg.dept_id
      )
        errors.push(`「${name}」未选择目标部门`);
      else if (
        node.approverType === 5 &&
        (!cfg.level || Number(cfg.level) < 1)
      )
        errors.push(`「${name}」未设置上级层级`);
      else if (node.approverType === 6 || node.approverType === 7)
        errors.push(`「${name}」使用了已停用的审批人类型，请重新选择`);
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
