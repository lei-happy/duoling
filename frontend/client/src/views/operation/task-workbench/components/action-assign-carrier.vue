<!--
  待分配 → 待派车：确认承运方式（承运商 / 社会运力 / 自有车可先不定运力）

  - 单条：三种承运方式均可选（社会运力从运力池选择，待开发）
  - 批量：仅支持自有车 / 承运商，统一写入后进入待派车
-->
<template>
  <el-dialog
    :model-value="visible"
    :title="dialogTitle"
    :width="isBatch ? '860px' : '720px'"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <div
      v-if="!isBatch && primaryTask"
      class="assign-carrier-task"
      v-loading="loadingItems"
    >
      <div class="assign-carrier-task__no">{{ primaryTask.taskNo }}</div>
      <div class="assign-carrier-task__route">
        <div class="assign-carrier-task__loc">
          <div class="assign-carrier-task__label">出发地</div>
          <div class="assign-carrier-task__value">
            {{ primaryTask.origin || '--' }}
          </div>
        </div>
        <el-icon class="assign-carrier-task__arrow"><Right /></el-icon>
        <div class="assign-carrier-task__loc">
          <div class="assign-carrier-task__label">目的地</div>
          <div class="assign-carrier-task__value">
            {{ primaryTask.destination || '--' }}
          </div>
        </div>
      </div>
      <div class="assign-carrier-task__meta">
        <div class="assign-carrier-task__meta-item">
          <span class="assign-carrier-task__label">承运台数</span>
          <span class="assign-carrier-task__highlight">
            {{ primaryTask.totalQuantity || 0 }} 台
          </span>
        </div>
        <div class="assign-carrier-task__meta-item">
          <span class="assign-carrier-task__label">承运品牌车型</span>
          <span class="assign-carrier-task__highlight">
            {{ brandModelSummary }}
          </span>
        </div>
      </div>
    </div>

    <el-alert
      v-else-if="isBatch"
      type="info"
      :closable="false"
      class="assign-carrier-tip"
      :title="`已选 ${taskList.length} 张任务单，将统一确认承运方式并进入「待派车」`"
    />

    <el-alert
      v-if="isBatch"
      type="warning"
      :closable="false"
      class="assign-carrier-tip"
      title="批量分配仅支持「自有车」或「承运商」。社会运力对应具体司机，请逐单分配。自有车可在待派车池再绑定运力。"
    />

    <el-table
      v-if="isBatch"
      :data="taskList"
      size="small"
      border
      max-height="220"
      class="assign-carrier-batch-table"
    >
      <el-table-column prop="taskNo" label="任务单号" min-width="150" />
      <el-table-column label="运输线路" min-width="200">
        <template #default="{ row }">
          {{ row.origin || '--' }} → {{ row.destination || '--' }}
        </template>
      </el-table-column>
      <el-table-column prop="totalQuantity" label="台数" width="72" align="center" />
    </el-table>

    <div class="assign-carrier-section-title">选择承运方</div>

    <el-form :model="form" label-width="100px" v-loading="submitting">
      <task-carrier-picker
        ref="pickerRef"
        v-model="form.carrier"
        :simple-mode="true"
        :allowed-carrier-types="isBatch ? BATCH_ALLOWED_CARRIER_TYPES : undefined"
      />
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">
        {{ submitLabel }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, nextTick } from 'vue';
  import { Right } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import TaskCarrierPicker from '../../task/components/task-carrier-picker.vue';
  import {
    batchCompleteCarrierAssignment,
    completeCarrierAssignment,
    listTaskWaybillItems
  } from '@/api/operation/task';
  import type { Task, TaskCarrierInfo } from '@/api/operation/task/model';
  import { summarizeTaskBrandModels } from '../task-cargo-detail-adapter';

  const BATCH_ALLOWED_CARRIER_TYPES = [1, 2];

  const props = defineProps<{
    visible: boolean;
    /** 兼容任务详情/台账等单条入口 */
    task?: Task | null;
    /** 工作台批量/单条均通过 tasks 传入 */
    tasks?: Task[];
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const pickerRef = ref<{ init: () => void } | null>(null);
  const submitting = ref(false);
  const loadingItems = ref(false);
  const brandModelSummary = ref('--');

  const taskList = computed(() => {
    if (props.tasks?.length) return props.tasks;
    if (props.task) return [props.task];
    return [];
  });

  const isBatch = computed(() => taskList.value.length > 1);
  const primaryTask = computed(() => taskList.value[0] ?? null);

  const dialogTitle = computed(() =>
    isBatch.value ? `批量分配承运（${taskList.value.length} 单）` : '分配承运'
  );

  const submitLabel = computed(() =>
    isBatch.value ? `确认批量分配（${taskList.value.length}）` : '确认分配'
  );

  const defaultCarrier = (): TaskCarrierInfo => ({
    carrierType: 1,
    capacityId: undefined,
    carrierId: undefined,
    mainDriverName: '',
    mainDriverPhone: '',
    plateNumber: '',
    trailerPlateNumber: '',
    carrierName: '',
    carrierShortName: ''
  });

  const form = reactive({
    carrier: defaultCarrier()
  });

  const loadBrandModelSummary = async (task: Task) => {
    brandModelSummary.value = '--';
    if (!task.id) return;
    loadingItems.value = true;
    try {
      const items = await listTaskWaybillItems(task.id);
      brandModelSummary.value = summarizeTaskBrandModels(items);
    } catch {
      brandModelSummary.value = '--';
    } finally {
      loadingItems.value = false;
    }
  };

  const onOpen = () => {
    const task = primaryTask.value;
    if (task && !isBatch.value) {
      form.carrier = {
        carrierType: task.carrierType || 1,
        capacityId: task.capacityId ?? undefined,
        carrierId: task.carrierId ?? undefined,
        socialDriverId: task.socialDriverId ?? undefined,
        mainDriverName: task.mainDriverName || '',
        mainDriverPhone: task.mainDriverPhone || '',
        mainDriverIdCard: task.mainDriverIdCard || '',
        plateNumber: task.plateNumber || '',
        trailerPlateNumber: task.trailerPlateNumber || '',
        carrierName: task.carrierName || '',
        carrierShortName: task.carrierShortName || ''
      };
      loadBrandModelSummary(task);
    } else {
      form.carrier = defaultCarrier();
      brandModelSummary.value = '--';
    }
    nextTick(() => pickerRef.value?.init?.());
  };

  const validateAssignment = (c: TaskCarrierInfo): string | null => {
    if (isBatch.value && c.carrierType === 3) {
      return '社会运力不支持批量分配，请逐单操作';
    }
    if (c.carrierType === 2 && !c.carrierId && !c.carrierName?.trim()) {
      return '请选择承运商';
    }
    if (c.carrierType === 3) {
      if (!c.socialDriverId) {
        return '社会运力池功能开发中，暂不支持分配';
      }
    }
    return null;
  };

  const reportBatchResult = (res: {
    success: number;
    failed: number;
    failures?: Array<{ id: number; error: string }>;
  }) => {
    if (res.failed > 0) {
      EleMessage.warning({
        message: `成功 ${res.success} 张，失败 ${res.failed} 张`,
        plain: true
      });
      return res.success > 0;
    }
    EleMessage.success({
      message: `已成功分配 ${res.success} 张任务`,
      plain: true
    });
    return true;
  };

  const submit = async () => {
    const list = taskList.value;
    if (list.length === 0) {
      emit('update:visible', false);
      return;
    }
    const err = validateAssignment(form.carrier);
    if (err) {
      EleMessage.error({ message: err, plain: true });
      return;
    }

    submitting.value = true;
    try {
      if (isBatch.value) {
        const ids = list.map((t) => t.id!).filter(Boolean);
        if (ids.length === 0) {
          EleMessage.warning({ message: '未选中有效任务', plain: true });
          return;
        }
        const res = await batchCompleteCarrierAssignment({
          ids,
          carrier: form.carrier
        });
        if (res && reportBatchResult(res)) {
          emit('done');
          emit('update:visible', false);
        }
        return;
      }

      const task = list[0];
      if (!task?.id) {
        emit('update:visible', false);
        return;
      }
      if ((task.status ?? 0) !== -1) {
        EleMessage.warning({
          message: '仅待分配状态可执行本操作',
          plain: true
        });
        return;
      }
      await completeCarrierAssignment(task.id, form.carrier);
      EleMessage.success({
        message: '已确认承运分配，任务已进入待派车',
        plain: true
      });
      emit('done');
      emit('update:visible', false);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '提交失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .assign-carrier-task {
    margin-bottom: 12px;
    padding: 16px 18px;
    border-radius: 8px;
    background: linear-gradient(
      135deg,
      var(--el-color-primary-light-9) 0%,
      var(--el-fill-color-blank) 100%
    );
    border: 1px solid var(--el-color-primary-light-7);
  }

  .assign-carrier-task__no {
    margin-bottom: 12px;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  .assign-carrier-task__route {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
  }

  .assign-carrier-task__loc {
    flex: 1;
    min-width: 0;
  }

  .assign-carrier-task__arrow {
    flex-shrink: 0;
    font-size: 18px;
    color: var(--el-color-primary);
  }

  .assign-carrier-task__label {
    margin-bottom: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.4;
  }

  .assign-carrier-task__value {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    line-height: 1.45;
    word-break: break-all;
  }

  .assign-carrier-task__meta {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    padding-top: 12px;
    border-top: 1px dashed var(--el-border-color-lighter);
  }

  .assign-carrier-task__meta-item {
    min-width: 0;
  }

  .assign-carrier-task__highlight {
    display: block;
    margin-top: 4px;
    font-size: 18px;
    font-weight: 700;
    color: var(--el-color-primary);
    line-height: 1.4;
    word-break: break-all;
  }

  .assign-carrier-tip {
    margin-bottom: 12px;
  }

  .assign-carrier-batch-table {
    width: 100%;
    margin-bottom: 12px;
  }

  .assign-carrier-section-title {
    margin-bottom: 12px;
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
</style>
