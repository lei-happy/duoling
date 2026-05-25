<template>
  <ele-page class="task-create-page">
    <ele-card
      class="task-create-page__main"
      :body-style="{ padding: '12px 12px 8px' }"
    >
      <task-cargo-picker
        ref="pickerRef"
        class="task-create-page__picker"
        v-model="waybillItems"
        :segments="segments"
        layout="page"
      />
    </ele-card>

    <ele-bottom-bar teleported class="task-create-page__bottom-bar">
      <div class="task-create-page__footer-left">
        <el-popover
          v-model:visible="remarkPopoverVisible"
          placement="top-start"
          :width="420"
          trigger="click"
          popper-class="task-create-page__remark-popper"
        >
          <template #reference>
            <el-button link type="primary" class="task-create-page__remark-trigger">
              <el-icon><EditPen /></el-icon>
              {{ remarkFilled ? '编辑备注' : '添加备注（选填）' }}
            </el-button>
          </template>
          <div class="task-create-page__remark-popover">
            <div class="task-create-page__remark-popover-title">调度备注</div>
            <el-input
              v-model="remark"
              type="textarea"
              :rows="4"
              maxlength="500"
              show-word-limit
              placeholder="调度说明、客户特殊要求等（选填）"
            />
          </div>
        </el-popover>
        <span
          v-if="remarkFilled"
          class="task-create-page__remark-preview"
          :title="remark.trim()"
        >
          {{ remarkPreview }}
        </span>
      </div>
      <template #extra>
        <el-button
          v-permission="'operation:task:add'"
          type="primary"
          :loading="submitting"
          :disabled="!canCreate"
          @click="submitCreate"
        >
          创建任务单
        </el-button>
      </template>
    </ele-bottom-bar>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EditPen } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import TaskCargoPicker from '../task/components/task-cargo-picker.vue';
  import { addTask } from '@/api/operation/task';
  import type { TaskSegment, TaskWaybillItem } from '@/api/operation/task/model';
  import {
    buildWaybillItemsPayload,
    validateCargoTab
  } from '../task/task-create-utils';

  defineOptions({ name: 'OperationTaskCreate' });

  const pickerRef = ref<{ reload: () => Promise<void> } | null>(null);

  const waybillItems = ref<TaskWaybillItem[]>([]);
  const segments = ref<TaskSegment[]>([]);
  const remark = ref('');
  const remarkPopoverVisible = ref(false);
  const submitting = ref(false);

  const canCreate = computed(
    () =>
      waybillItems.value.length > 0 &&
      waybillItems.value.every((it) => Number(it.quantity) > 0)
  );
  const remarkFilled = computed(() => !!remark.value.trim());
  const remarkPreview = computed(() => {
    const text = remark.value.trim();
    if (!text) return '';
    return text.length > 48 ? `${text.slice(0, 48)}…` : text;
  });

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
      remark.value = '';
      remarkPopoverVisible.value = false;
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
    flex: 1;
    min-height: 0;
    box-sizing: border-box;
  }

  .task-create-page__main {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    :deep(.ele-card-body) {
      flex: 1;
      min-height: 0;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
  }

  .task-create-page__picker {
    flex: 1 1 0;
    min-height: 0;
  }

  .task-create-page__footer-left {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
  }

  .task-create-page__remark-trigger {
    flex-shrink: 0;

    .el-icon {
      margin-right: 4px;
    }
  }

  .task-create-page__remark-preview {
    min-width: 0;
    max-width: min(480px, 42vw);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  .task-create-page__remark-popover-title {
    margin-bottom: 8px;
    font-size: 13px;
    font-weight: 500;
    color: var(--el-text-color-regular);
  }
</style>

<style lang="scss">
  .task-create-page__remark-popper {
    padding: 12px 16px 16px;
  }
</style>
