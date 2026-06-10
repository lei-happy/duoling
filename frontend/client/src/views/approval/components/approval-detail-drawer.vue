<template>
  <el-drawer
    :model-value="visible"
    :size="560"
    :title="
      detail ? detail.title || detail.instanceNo || '审批详情' : '审批详情'
    "
    :destroy-on-close="true"
    @update:model-value="updateVisible"
  >
    <div v-loading="loading" class="approval-detail">
      <template v-if="detail">
        <!-- 头部 -->
        <div class="approval-detail-head">
          <el-tag :type="statusTag(detail.status)" effect="light">
            {{ statusLabel(detail.status) }}
          </el-tag>
          <span class="approval-detail-no">{{ detail.instanceNo }}</span>
        </div>

        <el-descriptions :column="2" border size="small" class="mt-2">
          <el-descriptions-item label="审批类型">
            {{ bizTypeLabel(detail.bizType) }}
          </el-descriptions-item>
          <el-descriptions-item label="发起人">
            {{ detail.initiatorName || detail.initiatorId }}
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">
            {{ formatDateTime(detail.submittedAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间">
            {{ detail.finishedAt ? formatDateTime(detail.finishedAt) : '—' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 业务摘要 -->
        <el-divider content-position="left">申请内容</el-divider>
        <el-descriptions
          v-if="summaryFields.length"
          :column="1"
          border
          size="small"
        >
          <el-descriptions-item
            v-for="f in summaryFields"
            :key="f.label"
            :label="f.label"
          >
            {{ formatVal(f.value) }}
          </el-descriptions-item>
        </el-descriptions>
        <el-empty v-else description="无摘要信息" :image-size="60" />

        <!-- 审批节点 -->
        <el-divider content-position="left">审批节点</el-divider>
        <div class="approval-nodes">
          <div
            v-for="node in detail.nodes"
            :key="node.id"
            class="approval-node"
          >
            <div class="approval-node-title">
              <span class="approval-node-name">
                {{ node.nodeOrder }}. {{ node.nodeName }}
              </span>
              <el-tag size="small" type="info" effect="plain">
                {{ signTypeLabel(node.signType) }}
              </el-tag>
              <el-tag size="small" :type="nodeTag(node.status)" effect="light">
                {{ nodeStatusLabel(node.status) }}
              </el-tag>
            </div>
            <div class="approval-node-tasks">
              <el-tag
                v-for="t in node.tasks"
                :key="t.id"
                size="small"
                :type="taskTag(t.status)"
                effect="plain"
                class="approval-task-tag"
              >
                {{ t.approverName || t.approverId }}
                <span v-if="t.status !== 0">
                  · {{ taskStatusLabel(t.status) }}
                </span>
              </el-tag>
              <span v-if="!node.tasks.length" class="approval-node-empty">
                —
              </span>
            </div>
          </div>
        </div>

        <!-- 审批流水 -->
        <el-divider content-position="left">审批记录</el-divider>
        <el-timeline>
          <el-timeline-item
            v-for="r in detail.records"
            :key="r.id"
            :type="timelineType(r.action)"
            :timestamp="formatDateTime(r.createdAt)"
          >
            <div class="approval-record">
              <span class="approval-record-op">
                {{ r.operatorName || r.operatorId }}
              </span>
              <span class="approval-record-act">{{
                actionLabel(r.action)
              }}</span>
              <span v-if="r.comment" class="approval-record-comment">
                ：{{ r.comment }}
              </span>
            </div>
          </el-timeline-item>
        </el-timeline>

        <!-- 抄送 -->
        <template v-if="detail.ccList.length">
          <el-divider content-position="left">抄送</el-divider>
          <el-tag
            v-for="c in detail.ccList"
            :key="c.id"
            size="small"
            effect="plain"
            class="approval-task-tag"
          >
            {{ c.userName || c.userId }}
          </el-tag>
        </template>
      </template>
    </div>

    <template #footer>
      <div class="approval-detail-footer">
        <el-button @click="updateVisible(false)">关闭</el-button>
        <template v-if="detail && detail.status === 0">
          <el-button
            v-if="detail.canWithdraw"
            type="warning"
            plain
            @click="onWithdraw"
          >
            撤回
          </el-button>
          <el-button plain @click="openAction('cc')">抄送</el-button>
          <template v-if="detail.myPendingTaskId">
            <el-button plain @click="openAction('transfer')">转审</el-button>
            <el-button plain @click="openAction('addsign')">加签</el-button>
            <el-button type="danger" @click="openAction('reject')"
              >驳回</el-button
            >
            <el-button type="success" @click="openAction('agree')"
              >同意</el-button
            >
          </template>
        </template>
      </div>
    </template>

    <approval-action-modal
      v-model:visible="actionVisible"
      :mode="actionMode"
      :task-id="detail?.myPendingTaskId"
      :instance-id="detail?.instanceId"
      @done="onActionDone"
    />
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref, computed, watch } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { getInstanceDetail, withdrawInstance } from '@/api/approval';
  import type { ApprovalDetailOut } from '@/api/approval/model';
  import { formatDateTime } from '@/utils/date-util';
  import ApprovalActionModal from './approval-action-modal.vue';
  import {
    instanceStatusLabel as statusLabel,
    instanceStatusTag as statusTag,
    actionLabel,
    actionTimelineType as timelineType,
    nodeStatusLabel,
    taskStatusLabel,
    signTypeLabel,
    bizTypeLabel,
    renderSummary
  } from '../constants';

  const props = defineProps<{
    visible: boolean;
    instanceId?: number;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'changed'): void;
  }>();

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const loading = ref(false);
  const detail = ref<ApprovalDetailOut | null>(null);

  const actionVisible = ref(false);
  const actionMode = ref<'agree' | 'reject' | 'transfer' | 'addsign' | 'cc'>(
    'agree'
  );

  const summaryFields = computed(() =>
    renderSummary(detail.value?.bizType, detail.value?.summary)
  );

  const nodeTag = (s?: number) =>
    s === 2 ? 'success' : s === 3 ? 'danger' : s === 1 ? 'primary' : 'info';
  const taskTag = (s?: number) =>
    s === 1 ? 'success' : s === 2 ? 'danger' : s === 0 ? 'primary' : 'info';

  const formatVal = (v: any) => {
    if (v === true) return '是';
    if (v === false) return '否';
    if (v === null || v === undefined || v === '') return '—';
    return String(v);
  };

  const load = async () => {
    if (!props.instanceId) return;
    loading.value = true;
    try {
      detail.value = await getInstanceDetail(props.instanceId);
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '加载失败', plain: true });
      detail.value = null;
    } finally {
      loading.value = false;
    }
  };

  watch(
    () => [props.visible, props.instanceId] as const,
    ([v]) => {
      if (v && props.instanceId) {
        load();
      }
    }
  );

  const openAction = (
    mode: 'agree' | 'reject' | 'transfer' | 'addsign' | 'cc'
  ) => {
    actionMode.value = mode;
    actionVisible.value = true;
  };

  const onActionDone = () => {
    load();
    emit('changed');
  };

  const onWithdraw = () => {
    if (!detail.value) return;
    ElMessageBox.prompt('请输入撤回原因（可选）', '撤回审批', {
      confirmButtonText: '确认撤回',
      cancelButtonText: '取消',
      inputType: 'textarea',
      inputValidator: () => true
    })
      .then(async ({ value }) => {
        await withdrawInstance(detail.value!.instanceId, {
          reason: value || undefined
        });
        EleMessage.success({ message: '已撤回', plain: true });
        load();
        emit('changed');
      })
      .catch(() => {});
  };
</script>

<style lang="scss" scoped>
  .approval-detail {
    min-height: 200px;
  }
  .approval-detail-head {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .approval-detail-no {
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }
  .mt-2 {
    margin-top: 8px;
  }
  .approval-nodes {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .approval-node-title {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .approval-node-name {
    font-weight: 600;
  }
  .approval-node-tasks {
    margin-top: 6px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .approval-task-tag {
    margin-right: 4px;
  }
  .approval-node-empty {
    color: var(--el-text-color-secondary);
  }
  .approval-record-op {
    font-weight: 600;
  }
  .approval-record-act {
    margin-left: 4px;
    color: var(--el-color-primary);
  }
  .approval-detail-footer {
    display: flex;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 8px;
  }
</style>
