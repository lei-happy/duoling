<!-- 递归节点渲染：发起人 / 审批人 / 抄送人 / 条件分支（对标钉钉自上而下流程） -->
<template>
  <template v-if="node">
    <!-- 普通节点：发起人 / 审批 / 抄送 -->
    <template v-if="node.type !== 'condition'">
      <div class="wf-node-wrap">
        <div
          class="wf-node"
          :class="[
            node.type === 'start' ? 'is-start' : '',
            node.type === 'approval' ? 'is-approval' : '',
            node.type === 'cc' ? 'is-cc' : '',
            showError ? 'is-error' : ''
          ]"
          @click="onNodeClick"
        >
          <div class="wf-node-head">
            <span class="wf-node-title">{{ node.nodeName || typeLabel }}</span>
            <el-icon
              v-if="node.type !== 'start' && !readonly"
              class="wf-node-del"
              title="删除节点"
              @click.stop="removeSelf"
            >
              <Close />
            </el-icon>
          </div>
          <div class="wf-node-body">
            <span
              v-if="displayText"
              class="wf-node-content"
              :class="{ 'is-placeholder': showPlaceholder }"
            >
              {{ displayText }}
            </span>
            <el-icon v-if="showArrow" class="wf-node-arrow">
              <ArrowRight />
            </el-icon>
          </div>
        </div>
        <add-node
          :readonly="readonly"
          :child-node="node.childNode"
          @update:child-node="onUpdateChild"
        />
      </div>
    </template>

    <!-- 条件分支路由 -->
    <template v-else>
      <div class="wf-branch-wrap">
        <div class="wf-branch-box">
          <button
            v-if="!readonly && supportsConditionBranch"
            type="button"
            class="wf-add-branch"
            @click="addBranch"
          >
            添加条件
          </button>
          <div
            v-for="(branch, index) in node.conditionNodes || []"
            :key="branch.nodeKey"
            class="wf-branch-col"
          >
            <div class="wf-branch-node">
              <div
                class="wf-condition"
                :class="branchError(branch, index) ? 'is-error' : ''"
                @click="openCondition(branch, index)"
              >
                <div class="wf-condition-head">
                  <span class="wf-condition-title">{{ branch.nodeName }}</span>
                  <span class="wf-condition-priority"
                    >优先级{{ index + 1 }}</span
                  >
                  <div v-if="!readonly" class="wf-condition-actions">
                    <button
                      v-if="canMoveBranch(index, -1)"
                      type="button"
                      class="wf-condition-action"
                      title="提高优先级"
                      @click.stop="moveBranch(index, -1)"
                    >
                      <el-icon><ArrowLeft /></el-icon>
                    </button>
                    <button
                      v-if="canMoveBranch(index, 1)"
                      type="button"
                      class="wf-condition-action"
                      title="降低优先级"
                      @click.stop="moveBranch(index, 1)"
                    >
                      <el-icon><ArrowRight /></el-icon>
                    </button>
                    <el-icon
                      v-if="!isDefaultBranch(index)"
                      class="wf-node-del"
                      title="删除条件"
                      @click.stop="removeBranch(index)"
                    >
                      <Close />
                    </el-icon>
                  </div>
                </div>
                <div class="wf-condition-body">
                  {{ conditionText(branch) }}
                </div>
              </div>
              <add-node
                :readonly="readonly"
                :child-node="branch.childNode"
                @update:child-node="(v) => (branch.childNode = v)"
              />
            </div>
            <workflow-node
              v-if="branch.childNode"
              v-model:node="branch.childNode"
            />
            <template v-if="index === 0">
              <div class="wf-cover-line top-left"></div>
              <div class="wf-cover-line bottom-left"></div>
            </template>
            <template v-if="index === (node.conditionNodes || []).length - 1">
              <div class="wf-cover-line top-right"></div>
              <div class="wf-cover-line bottom-right"></div>
            </template>
          </div>
        </div>
        <add-node
          :readonly="readonly"
          :child-node="node.childNode"
          @update:child-node="onUpdateChild"
        />
      </div>
    </template>

    <!-- 继续渲染后继节点（汇合点之后的链） -->
    <workflow-node v-if="node.childNode" v-model:node="node.childNode" />
  </template>
</template>

<script lang="ts" setup>
  import { computed, inject } from 'vue';
  import { Close, ArrowRight, ArrowLeft } from '@element-plus/icons-vue';
  import type { CanvasNode, ConditionBranch } from '@/api/approval/model';
  import {
    createBranch,
    approverSummary,
    conditionSummary,
    initiatorSummary
  } from '@/api/approval/transform';
  import { WORKFLOW_CTX } from './context';
  import AddNode from './add-node.vue';

  defineOptions({ name: 'WorkflowNode' });

  /** 当前节点（与父级共享同一响应式引用，可就地编辑） */
  const node = defineModel<CanvasNode | null>('node');

  const ctx = inject(WORKFLOW_CTX);
  const readonly = computed(() => ctx?.readonly ?? false);
  const supportsConditionBranch = computed(
    () => ctx?.supportsConditionBranch ?? false
  );
  const conditionFields = computed(() => ctx?.conditionFields ?? []);

  const typeLabel = computed(() => {
    if (node.value?.type === 'start') return '发起人';
    if (node.value?.type === 'approval') return '审批人';
    if (node.value?.type === 'cc') return '抄送人';
    return node.value?.nodeName ?? '';
  });

  const placeholder = computed(() => {
    if (node.value?.type === 'approval') return '请设置审批人';
    if (node.value?.type === 'cc') return '请设置抄送人';
    return '请设置发起人';
  });

  const contentText = computed(() => {
    if (!node.value || node.value.type === 'start') return '';
    return approverSummary(node.value);
  });

  const displayText = computed(() => {
    if (node.value?.type === 'start') return initiatorSummary(node.value);
    return contentText.value || placeholder.value;
  });

  const showPlaceholder = computed(() => {
    if (node.value?.type === 'start') {
      return displayText.value.startsWith('请设置');
    }
    return !contentText.value;
  });

  const showArrow = computed(() => {
    if (readonly.value) return false;
    return (
      node.value?.type === 'start' ||
      node.value?.type === 'approval' ||
      node.value?.type === 'cc'
    );
  });

  const showError = computed(() => {
    if (!node.value) return false;
    if (node.value.type === 'start') {
      const type = node.value.initiatorType || 'all';
      const cfg = node.value.initiatorConfig || {};
      if (type === 'user') return !cfg.user_ids?.length;
      if (type === 'role') return !cfg.role_ids?.length;
      if (type === 'dept') return !cfg.dept_ids?.length;
      return false;
    }
    return !approverSummary(node.value);
  });

  const onNodeClick = () => {
    if (!node.value || readonly.value) return;
    if (node.value.type === 'start') {
      ctx?.openStartConfig(node.value);
      return;
    }
    ctx?.openNodeConfig(node.value);
  };

  const onUpdateChild = (v: CanvasNode | null) => {
    if (node.value) node.value.childNode = v;
  };

  const removeSelf = () => {
    if (!node.value || node.value.type === 'start') return;
    node.value = node.value.childNode ?? null;
  };

  // ------- 条件分支操作 -------
  const branchCount = computed(() => node.value?.conditionNodes?.length ?? 0);

  const isDefaultBranch = (index: number) => index === branchCount.value - 1;

  const canMoveBranch = (index: number, dir: -1 | 1) => {
    const target = index + dir;
    if (target < 0 || target >= branchCount.value) return false;
    // 默认分支（其它情况）不参与排序
    if (isDefaultBranch(index) || isDefaultBranch(target)) return false;
    return true;
  };

  const conditionText = (b: ConditionBranch) =>
    conditionSummary(b, conditionFields.value);

  const branchError = (b: ConditionBranch, index: number) => {
    const isLast = index === (node.value?.conditionNodes || []).length - 1;
    return !isLast && !b.condition?.rules?.length;
  };

  const openCondition = (b: ConditionBranch, index: number) => {
    if (readonly.value) return;
    const isDefault = index === (node.value?.conditionNodes || []).length - 1;
    ctx?.openCondition(b, isDefault);
  };

  const addBranch = () => {
    const list = node.value?.conditionNodes;
    if (!list) return;
    // 新条件插在「其它情况」默认分支之前
    const len = list.length;
    list.splice(Math.max(len - 1, 0), 0, createBranch(len));
    reorderBranches();
  };

  const removeBranch = (index: number) => {
    const list = node.value?.conditionNodes;
    if (!list) return;
    list.splice(index, 1);
    reorderBranches();
    // 仅剩 1 个分支时，条件路由失去意义：用该分支子链替换整个路由
    if (list.length === 1) {
      const only = list[0];
      const merged = only.childNode ?? null;
      const tail = node.value?.childNode ?? null;
      if (merged) {
        appendChain(merged, tail);
        node.value = merged;
      } else {
        node.value = tail;
      }
    }
  };

  const moveBranch = (index: number, dir: -1 | 1) => {
    const list = node.value?.conditionNodes;
    if (!list) return;
    const target = index + dir;
    if (target < 0 || target >= list.length) return;
    const [item] = list.splice(index, 1);
    list.splice(target, 0, item);
    reorderBranches();
  };

  const reorderBranches = () => {
    (node.value?.conditionNodes || []).forEach((b, i) => {
      b.priority = i + 1;
    });
  };

  /** 把 tail 链接到 chain 末尾（条件路由删除后保留汇合点之后的链） */
  const appendChain = (chain: CanvasNode, tail: CanvasNode | null) => {
    let cur = chain;
    while (cur.childNode) cur = cur.childNode;
    cur.childNode = tail;
  };
</script>
