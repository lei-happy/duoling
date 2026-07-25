<template>
  <el-dialog
    :title="dialogTitle"
    :model-value="visible"
    width="920px"
    draggable
    destroy-on-close
    :close-on-click-modal="false"
    class="flow-version-dialog"
    @update:model-value="updateVisible"
  >
    <div v-loading="loading" class="version-panel">
      <el-empty
        v-if="!loading && !logs.length"
        description="暂无版本历史"
        :image-size="80"
      />

      <el-scrollbar v-else max-height="560px">
        <div class="version-timeline">
          <div
            v-for="(row, index) in logs"
            :key="row.id"
            class="version-item"
            :class="{
              'is-active': expandedId === row.id,
              [`is-${row.changeType}`]: true
            }"
          >
            <div class="version-rail">
              <div class="version-dot">
                <span>{{ row.version }}</span>
              </div>
              <div v-if="index < logs.length - 1" class="version-line"></div>
            </div>

            <div class="version-card">
              <button
                type="button"
                class="version-head"
                @click="toggleExpand(row)"
              >
                <div class="version-head-main">
                  <span class="version-badge">v{{ row.version }}</span>
                  <el-tag
                    :type="changeTypeTag(row.changeType)"
                    size="small"
                    effect="light"
                    round
                  >
                    {{ changeTypeText(row.changeType) }}
                  </el-tag>
                  <span class="version-remark">
                    {{ row.remark || changeTypeDesc(row.changeType) }}
                  </span>
                </div>
                <div class="version-head-meta">
                  <span class="meta-chip">
                    {{ operatorLabel(row.operatorId) }}
                  </span>
                  <span class="meta-chip">
                    {{ formatDateTime(row.createdAt) }}
                  </span>
                  <el-icon
                    class="expand-icon"
                    :class="{ open: expandedId === row.id }"
                  >
                    <ArrowDown />
                  </el-icon>
                </div>
              </button>

              <div v-if="expandedId === row.id" class="version-body">
                <template v-if="parseSnapshot(row)">
                  <div class="snapshot-meta">
                    <div
                      v-for="item in snapshotMeta(row)"
                      :key="item.label"
                      class="meta-item"
                    >
                      <span class="meta-label">{{ item.label }}</span>
                      <span class="meta-value">{{ item.value }}</span>
                    </div>
                  </div>

                  <div class="snapshot-flow">
                    <div class="flow-title">
                      <span>当时流程节点</span>
                      <span class="flow-count">
                        {{ stepsOf(row).length }} 个节点
                      </span>
                    </div>
                    <div v-if="stepsOf(row).length" class="flow-pipeline">
                      <template
                        v-for="(step, stepIndex) in stepsOf(row)"
                        :key="`${row.id}-${stepIndex}`"
                      >
                        <div class="flow-step" :class="`type-${step.type}`">
                          <div class="step-type">{{ step.typeLabel }}</div>
                          <div class="step-name">{{ step.name }}</div>
                          <div class="step-summary">{{ step.summary }}</div>
                        </div>
                        <div
                          v-if="stepIndex < stepsOf(row).length - 1"
                          class="flow-arrow"
                        ></div>
                      </template>
                    </div>
                    <div v-else class="flow-empty">该版本未配置流程节点</div>
                  </div>
                </template>
                <div v-else class="snapshot-empty">该版本无快照数据</div>
              </div>
            </div>
          </div>
        </div>
      </el-scrollbar>
    </div>

    <template #footer>
      <el-button @click="updateVisible(false)">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, watch, computed } from 'vue';
  import { ArrowDown } from '@element-plus/icons-vue';
  import { listFlowVersionHistory } from '@/api/approval';
  import type {
    CanvasNode,
    FlowVersionLog,
    ProcessConfig
  } from '@/api/approval/model';
  import {
    approverSummary,
    configToTree,
    initiatorSummary
  } from '@/api/approval/transform';
  import { bizTypeLabel } from '@/views/approval/constants';
  import { formatDateTime } from '@/utils/date-util';
  import { getUser } from '@/api/system/user';

  interface FlowStepView {
    type: 'start' | 'approval' | 'cc' | 'condition';
    typeLabel: string;
    name: string;
    summary: string;
  }

  interface SnapshotMetaItem {
    label: string;
    value: string;
  }

  const props = defineProps<{
    visible: boolean;
    flowId: number | null;
    flowName?: string;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
  }>();

  const loading = ref(false);
  const logs = ref<FlowVersionLog[]>([]);
  const expandedId = ref<number | null>(null);
  const operatorNameMap = ref<Record<number, string>>({});
  const stepsCache = new Map<number, FlowStepView[]>();
  const snapshotCache = new Map<number, Record<string, any> | null>();

  const dialogTitle = computed(() =>
    props.flowName ? `${props.flowName} · 版本历史` : '审批流程版本历史'
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const changeTypeText = (t?: string) => {
    if (t === 'publish') return '发布';
    if (t === 'disable') return '停用';
    if (t === 'enable') return '启用';
    return t || '变更';
  };

  const changeTypeDesc = (t?: string) => {
    if (t === 'publish') return '发布流程';
    if (t === 'disable') return '停用流程';
    if (t === 'enable') return '重新启用流程';
    return '流程变更';
  };

  const changeTypeTag = (
    t?: string
  ): 'success' | 'danger' | 'warning' | 'info' => {
    if (t === 'publish') return 'success';
    if (t === 'disable') return 'danger';
    if (t === 'enable') return 'warning';
    return 'info';
  };

  const operatorLabel = (id?: number) => {
    if (id == null) return '操作人未知';
    return operatorNameMap.value[id] || `操作人 #${id}`;
  };

  const parseSnapshot = (row: FlowVersionLog): Record<string, any> | null => {
    if (snapshotCache.has(row.id)) {
      return snapshotCache.get(row.id) ?? null;
    }
    const raw = row.snapshot;
    if (raw == null) {
      snapshotCache.set(row.id, null);
      return null;
    }
    try {
      const obj = typeof raw === 'string' ? JSON.parse(raw) : raw;
      const parsed =
        obj && typeof obj === 'object' ? (obj as Record<string, any>) : null;
      snapshotCache.set(row.id, parsed);
      return parsed;
    } catch {
      snapshotCache.set(row.id, null);
      return null;
    }
  };

  const yesNo = (v: unknown) => (Number(v) === 1 ? '是' : '否');

  const snapshotMeta = (row: FlowVersionLog): SnapshotMetaItem[] => {
    const snap = parseSnapshot(row);
    if (!snap) return [];
    return [
      {
        label: '流程名称',
        value: String(snap.flowName || props.flowName || '—')
      },
      { label: '审批场景', value: bizTypeLabel(snap.bizType) },
      { label: '优先级', value: String(snap.priority ?? '—') },
      { label: '默认流程', value: yesNo(snap.isDefault) },
      { label: '允许撤回', value: yesNo(snap.allowWithdraw) },
      {
        label: '备注',
        value: snap.remark ? String(snap.remark) : '—'
      }
    ];
  };

  const flattenCanvasSteps = (root?: CanvasNode | null): FlowStepView[] => {
    const steps: FlowStepView[] = [];
    const walk = (node?: CanvasNode | null) => {
      if (!node) return;
      if (node.type === 'start') {
        steps.push({
          type: 'start',
          typeLabel: '发起人',
          name: node.nodeName || '发起人',
          summary: initiatorSummary(node)
        });
      } else if (node.type === 'approval') {
        steps.push({
          type: 'approval',
          typeLabel: '审批人',
          name: node.nodeName || '审批人',
          summary: approverSummary(node) || '未设置审批人'
        });
      } else if (node.type === 'cc') {
        steps.push({
          type: 'cc',
          typeLabel: '抄送人',
          name: node.nodeName || '抄送人',
          summary: approverSummary(node) || '未设置抄送人'
        });
      } else if (node.type === 'condition') {
        const branches = node.conditionNodes || [];
        steps.push({
          type: 'condition',
          typeLabel: '条件分支',
          name: node.nodeName || '条件分支',
          summary: branches.map((b) => b.nodeName).join(' / ') || '未配置分支'
        });
        branches.forEach((b) => walk(b.childNode));
      }
      walk(node.childNode);
    };
    walk(root);
    return steps;
  };

  const stepsOf = (row: FlowVersionLog): FlowStepView[] => {
    if (stepsCache.has(row.id)) {
      return stepsCache.get(row.id)!;
    }
    const snap = parseSnapshot(row);
    if (!snap) {
      stepsCache.set(row.id, []);
      return [];
    }
    const config = (snap.processConfig || null) as ProcessConfig | null;
    const legacyNodes = Array.isArray(snap.nodes) ? snap.nodes : null;
    const root = configToTree(config, legacyNodes);
    const steps = flattenCanvasSteps(root);
    stepsCache.set(row.id, steps);
    return steps;
  };

  const toggleExpand = (row: FlowVersionLog) => {
    expandedId.value = expandedId.value === row.id ? null : row.id;
  };

  const resolveOperators = async (rows: FlowVersionLog[]) => {
    const ids = [
      ...new Set(
        rows
          .map((r) => r.operatorId)
          .filter((id): id is number => typeof id === 'number' && id > 0)
      )
    ];
    await Promise.all(
      ids.map(async (id) => {
        if (operatorNameMap.value[id]) return;
        try {
          const u = await getUser(id);
          operatorNameMap.value[id] = u.nickname || `用户 #${id}`;
        } catch {
          operatorNameMap.value[id] = `用户 #${id}`;
        }
      })
    );
  };

  const loadLogs = async (id: number) => {
    loading.value = true;
    stepsCache.clear();
    snapshotCache.clear();
    expandedId.value = null;
    try {
      const data = await listFlowVersionHistory(id);
      logs.value = data ?? [];
      if (logs.value.length) {
        expandedId.value = logs.value[0].id;
      }
      await resolveOperators(logs.value);
    } catch {
      logs.value = [];
    } finally {
      loading.value = false;
    }
  };

  watch(
    () => props.visible,
    (val) => {
      if (val && props.flowId) {
        loadLogs(props.flowId);
      } else if (!val) {
        logs.value = [];
        expandedId.value = null;
        stepsCache.clear();
        snapshotCache.clear();
      }
    }
  );
</script>

<style scoped lang="scss">
  .version-panel {
    min-height: 200px;
  }

  .version-timeline {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 4px 4px 8px;
  }

  .version-item {
    display: grid;
    grid-template-columns: 44px minmax(0, 1fr);
    gap: 12px;
    align-items: stretch;
  }

  .version-rail {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .version-dot {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: 12px;
    font-weight: 700;
    color: #fff;
    background: #909399;
    box-shadow: 0 0 0 4px rgba(144, 147, 153, 0.12);
    z-index: 1;
    flex-shrink: 0;
  }

  .version-item.is-publish .version-dot {
    background: #67c23a;
    box-shadow: 0 0 0 4px rgba(103, 194, 58, 0.14);
  }

  .version-item.is-disable .version-dot {
    background: #f56c6c;
    box-shadow: 0 0 0 4px rgba(245, 108, 108, 0.14);
  }

  .version-item.is-enable .version-dot {
    background: #e6a23c;
    box-shadow: 0 0 0 4px rgba(230, 162, 60, 0.14);
  }

  .version-line {
    width: 2px;
    flex: 1;
    min-height: 16px;
    margin-top: 4px;
    background: linear-gradient(
      180deg,
      var(--el-border-color) 0%,
      transparent 100%
    );
  }

  .version-card {
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    background: var(--el-bg-color);
    overflow: hidden;
    transition:
      border-color 0.2s,
      box-shadow 0.2s;
    margin-bottom: 10px;
  }

  .version-item.is-active .version-card {
    border-color: color-mix(in srgb, var(--el-color-primary) 45%, transparent);
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
  }

  .version-head {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 14px 16px;
    border: 0;
    background: transparent;
    cursor: pointer;
    text-align: left;
    color: inherit;

    &:hover {
      background: var(--el-fill-color-extra-light);
    }
  }

  .version-head-main {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    flex: 1;
  }

  .version-badge {
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: var(--el-text-color-primary);
    flex-shrink: 0;
  }

  .version-remark {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--el-text-color-regular);
    font-size: 13px;
  }

  .version-head-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .meta-chip {
    white-space: nowrap;
  }

  .expand-icon {
    transition: transform 0.2s ease;
    font-size: 14px;

    &.open {
      transform: rotate(180deg);
    }
  }

  .version-body {
    padding: 0 16px 16px;
    border-top: 1px dashed var(--el-border-color-lighter);
    animation: version-body-in 0.22s ease;
  }

  @keyframes version-body-in {
    from {
      opacity: 0;
      transform: translateY(-4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .snapshot-meta {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
    padding-top: 14px;
  }

  .meta-item {
    padding: 10px 12px;
    border-radius: 8px;
    background: var(--el-fill-color-extra-light);
    min-width: 0;
  }

  .meta-label {
    display: block;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-bottom: 4px;
  }

  .meta-value {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .snapshot-flow {
    margin-top: 14px;
    padding: 14px;
    border-radius: 10px;
    background:
      linear-gradient(
        180deg,
        color-mix(in srgb, var(--el-color-primary) 4%, transparent),
        transparent 48px
      ),
      var(--el-fill-color-blank);
    border: 1px solid var(--el-border-color-extra-light);
  }

  .flow-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .flow-count {
    font-size: 12px;
    font-weight: 500;
    color: var(--el-text-color-secondary);
  }

  .flow-pipeline {
    display: flex;
    align-items: stretch;
    gap: 0;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .flow-step {
    flex: 0 0 148px;
    min-height: 88px;
    border-radius: 8px;
    background: #fff;
    border: 1px solid var(--el-border-color-lighter);
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
  }

  .step-type {
    height: 26px;
    line-height: 26px;
    padding: 0 10px;
    font-size: 12px;
    font-weight: 600;
    color: #fff;
    background: #909399;
  }

  .flow-step.type-start .step-type {
    background: #576a95;
  }

  .flow-step.type-approval .step-type {
    background: #ff943e;
  }

  .flow-step.type-cc .step-type {
    background: #3296fa;
  }

  .flow-step.type-condition .step-type {
    background: #15bc83;
  }

  .step-name {
    padding: 8px 10px 2px;
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .step-summary {
    padding: 0 10px 10px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .flow-arrow {
    width: 20px;
    flex: 0 0 20px;
    align-self: center;
    position: relative;
    height: 2px;
    background: #cacaca;

    &::after {
      content: '';
      position: absolute;
      right: -1px;
      top: 50%;
      width: 6px;
      height: 6px;
      border-top: 2px solid #cacaca;
      border-right: 2px solid #cacaca;
      transform: translateY(-50%) rotate(45deg);
    }
  }

  .flow-empty,
  .snapshot-empty {
    padding: 18px 0 6px;
    text-align: center;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  @media (max-width: 768px) {
    .snapshot-meta {
      grid-template-columns: 1fr 1fr;
    }

    .version-head {
      flex-direction: column;
      align-items: flex-start;
    }

    .version-head-meta {
      width: 100%;
      justify-content: space-between;
    }
  }
</style>
