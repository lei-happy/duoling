<template>
  <div class="flow-design">
    <div class="flow-design-header">
      <div class="flow-design-header-left">
        <el-button text :icon="ArrowLeft" @click="goBack">返回</el-button>
        <el-divider direction="vertical" />
        <span class="flow-design-title">{{
          flow?.flowName || '审批流程配置'
        }}</span>
        <el-tag v-if="flow" size="small" :type="statusTag(flow.status)">
          {{ statusLabel(flow.status) }}
        </el-tag>
      </div>
      <div class="flow-design-header-right">
        <div class="flow-design-zoom">
          <el-button
            text
            :icon="ZoomOut"
            :disabled="zoom <= 50"
            @click="zoom -= 10"
          />
          <span>{{ zoom }}%</span>
          <el-button
            text
            :icon="ZoomIn"
            :disabled="zoom >= 150"
            @click="zoom += 10"
          />
        </div>
        <el-button :loading="saving" @click="save(false)">保存草稿</el-button>
        <el-button type="primary" :loading="saving" @click="save(true)">
          保存并发布
        </el-button>
      </div>
    </div>

    <div v-loading="loading" class="flow-design-body">
      <div class="wf-canvas" :style="{ transform: `scale(${zoom / 100})` }">
        <workflow-node v-if="root" v-model:node="root" />
        <div class="wf-end">
          <div class="wf-end-circle"></div>
          <div class="wf-end-text">流程结束</div>
        </div>
      </div>
    </div>

    <node-config-drawer
      v-model:visible="configVisible"
      v-model:node="activeNode"
    />
    <condition-drawer
      v-model:visible="conditionVisible"
      v-model:branch="activeBranch"
      :is-default="branchIsDefault"
    />
  </div>
</template>

<script lang="ts" setup>
  import { ref, provide, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { ElMessage, ElMessageBox } from 'element-plus';
  import { ArrowLeft, ZoomIn, ZoomOut } from '@element-plus/icons-vue';
  import { getFlow, updateFlow, publishFlow } from '@/api/approval';
  import {
    configToTree,
    treeToConfig,
    validateTree
  } from '@/api/approval/transform';
  import type {
    CanvasNode,
    ConditionBranch,
    FlowOut
  } from '@/api/approval/model';
  import WorkflowNode from '../components/workflow/workflow-node.vue';
  import NodeConfigDrawer from '../components/workflow/node-config-drawer.vue';
  import ConditionDrawer from '../components/workflow/condition-drawer.vue';
  import { WORKFLOW_CTX } from '../components/workflow/context';

  defineOptions({ name: 'EnterpriseApprovalFlowDesign' });

  const route = useRoute();
  const router = useRouter();

  const loading = ref(false);
  const saving = ref(false);
  const zoom = ref(100);
  const flow = ref<FlowOut | null>(null);
  const root = ref<CanvasNode | null>(null);

  const configVisible = ref(false);
  const activeNode = ref<CanvasNode | null>(null);
  const conditionVisible = ref(false);
  const activeBranch = ref<ConditionBranch | null>(null);
  const branchIsDefault = ref(false);

  provide(WORKFLOW_CTX, {
    readonly: false,
    openNodeConfig: (node: CanvasNode) => {
      activeNode.value = node;
      configVisible.value = true;
    },
    openCondition: (branch: ConditionBranch, isDefault: boolean) => {
      activeBranch.value = branch;
      branchIsDefault.value = isDefault;
      conditionVisible.value = true;
    }
  });

  const statusLabel = (s?: number) =>
    s === 1 ? '已发布' : s === 2 ? '已停用' : '草稿';
  const statusTag = (s?: number): 'info' | 'success' | 'danger' =>
    s === 1 ? 'success' : s === 2 ? 'danger' : 'info';

  const flowId = Number(route.params.id);

  const load = async () => {
    loading.value = true;
    try {
      const data = await getFlow(flowId);
      flow.value = data;
      root.value = configToTree(data.processConfig, data.nodes);
    } catch (e: any) {
      ElMessage.error(e?.message ?? '加载流程失败');
    } finally {
      loading.value = false;
    }
  };

  const goBack = () => {
    router.push('/enterprise/approval-config');
  };

  const save = async (publish: boolean) => {
    if (!root.value) return;
    if (publish) {
      const errors = validateTree(root.value);
      if (errors.length) {
        ElMessageBox.alert(errors.join('<br/>'), '流程配置不完整', {
          dangerouslyUseHTMLString: true,
          type: 'warning'
        });
        return;
      }
    }
    saving.value = true;
    try {
      await updateFlow(flowId, { processConfig: treeToConfig(root.value) });
      if (publish) {
        await publishFlow(flowId);
        ElMessage.success('已保存并发布');
      } else {
        ElMessage.success('草稿已保存');
      }
      await load();
    } catch (e: any) {
      ElMessage.error(e?.message ?? '保存失败');
    } finally {
      saving.value = false;
    }
  };

  onMounted(load);
</script>

<style lang="scss">
  @use '../components/workflow/workflow.scss';
</style>

<style lang="scss" scoped>
  .flow-design {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 110px);
    background: #f5f5f7;
    border-radius: 6px;
    overflow: hidden;
  }

  .flow-design-header {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 52px;
    padding: 0 16px;
    background: #fff;
    border-bottom: 1px solid var(--el-border-color-light);
  }

  .flow-design-header-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .flow-design-title {
    font-size: 15px;
    font-weight: 600;
  }

  .flow-design-header-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .flow-design-zoom {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  .flow-design-body {
    flex: 1;
    overflow: auto;
  }

  .flow-design-body .wf-canvas {
    transform-origin: top center;
  }
</style>
