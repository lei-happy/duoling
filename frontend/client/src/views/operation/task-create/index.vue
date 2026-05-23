<template>
  <ele-page class="task-create-page">
    <ele-card class="task-create-page__header">
      <div class="task-create-page__title-row">
        <span class="task-create-page__title">配载建单</span>
        <span class="task-create-page__tip">
          从待配运单中挑选商品车组成任务单；建议优先同线路、同车型凑成一板。创建后为「待分配」草稿，请在调度工作台继续分配承运。
        </span>
      </div>
    </ele-card>

    <ele-card
      class="task-create-page__main"
      :body-style="{ padding: '12px 12px 8px' }"
    >
      <task-cargo-picker
        ref="pickerRef"
        v-model="waybillItems"
        :segments="segments"
        layout="page"
      />
      <div class="task-create-page__remark">
        <div class="task-create-page__remark-label">备注（选填）</div>
        <el-input
          v-model="remark"
          type="textarea"
          :rows="3"
          maxlength="500"
          show-word-limit
          placeholder="调度说明、客户特殊要求等（选填）"
        />
      </div>
    </ele-card>

    <div class="task-create-page__footer">
      <el-button @click="onCancel">取消</el-button>
      <el-button
        v-permission="'operation:task:add'"
        type="primary"
        :loading="submitting"
        @click="submitCreate"
      >
        创建任务单
      </el-button>
    </div>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { EleMessage } from 'ele-admin-plus';
  import TaskCargoPicker from '../task/components/task-cargo-picker.vue';
  import { addTask } from '@/api/operation/task';
  import type { TaskSegment, TaskWaybillItem } from '@/api/operation/task/model';
  import {
    buildWaybillItemsPayload,
    validateCargoTab
  } from '../task/task-create-utils';

  defineOptions({ name: 'OperationTaskCreate' });

  const router = useRouter();
  const pickerRef = ref<{ reload: () => Promise<void> } | null>(null);

  const waybillItems = ref<TaskWaybillItem[]>([]);
  const segments = ref<TaskSegment[]>([]);
  const remark = ref('');
  const submitting = ref(false);

  const onCancel = () => {
    if (window.history.length > 1) {
      router.back();
      return;
    }
    router.push('/operation/task-workbench');
  };

  const submitCreate = async () => {
    if (submitting.value) return;
    if (!validateCargoTab(waybillItems.value)) return;

    submitting.value = true;
    try {
      await addTask({
        source: 1,
        remark: remark.value,
        waybillItems: buildWaybillItemsPayload(waybillItems.value),
        segments: [],
        carrier: undefined
      });
      EleMessage.success({
        message: '已创建配载单，可以继续配载下一单',
        plain: true
      });
      waybillItems.value = [];
      await pickerRef.value?.reload();
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '保存失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
    }
  };
</script>

<style scoped lang="scss">
  .task-create-page {
    display: flex;
    flex-direction: column;
    min-height: calc(100vh - 120px);
    padding-bottom: 72px;
  }

  .task-create-page__header {
    margin-bottom: 12px;
  }

  .task-create-page__title-row {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .task-create-page__title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .task-create-page__tip {
    font-size: 13px;
    line-height: 1.5;
    color: var(--el-text-color-secondary);
  }

  .task-create-page__main {
    flex: 1;
    min-height: 0;

    :deep(.ele-card-body) {
      display: flex;
      flex-direction: column;
    }
  }

  .task-create-page__remark {
    flex-shrink: 0;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--el-border-color-lighter);
  }

  .task-create-page__remark-label {
    margin-bottom: 8px;
    font-size: 13px;
    font-weight: 500;
    color: var(--el-text-color-regular);
  }

  .task-create-page__footer {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 10;
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    padding: 12px 24px;
    background: var(--el-bg-color);
    border-top: 1px solid var(--el-border-color-lighter);
    box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.04);
  }
</style>
