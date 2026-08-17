<!--
  待分配 → 待派车：确认承运方式（承运商 / 社会运力 / 自有车可先不定运力）

  - 单条：三种承运方式均可选（社会运力从运力池选择）
  - 批量：仅支持自有车 / 承运商，统一写入后进入待派车
-->
<template>
  <el-dialog
    :model-value="visible"
    :title="isBatch ? undefined : dialogTitle"
    :width="isBatch ? '860px' : '720px'"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <template v-if="isBatch" #header>
      <div class="assign-carrier-dialog-header">
        <span class="assign-carrier-dialog-header__title">{{
          dialogTitle
        }}</span>
        <el-tooltip placement="bottom-start" :show-after="200" :width="360">
          <template #content>
            <div class="assign-carrier-dialog-header__tip">
              批量分配仅支持「自有车」或「承运商」。社会运力对应具体司机，请逐单分配。自有车可在待派车池再绑定运力。
            </div>
          </template>
          <el-icon
            class="assign-carrier-dialog-header__info"
            :size="16"
            tabindex="-1"
          >
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </template>
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

    <div v-if="isBatch" class="assign-carrier-batch-summary">
      <div class="assign-carrier-batch-summary__item">
        <span class="assign-carrier-batch-summary__label">任务单</span>
        <span class="assign-carrier-batch-summary__value">{{
          taskList.length
        }}</span>
        <span class="assign-carrier-batch-summary__unit">张</span>
      </div>
      <div class="assign-carrier-batch-summary__divider"></div>
      <div class="assign-carrier-batch-summary__item">
        <span class="assign-carrier-batch-summary__label">商品车台数</span>
        <span class="assign-carrier-batch-summary__value">{{
          batchTotalQuantity
        }}</span>
        <span class="assign-carrier-batch-summary__unit">台</span>
      </div>
    </div>

    <el-table
      v-if="isBatch"
      :data="taskList"
      size="small"
      border
      max-height="220"
      class="assign-carrier-batch-table"
    >
      <el-table-column prop="taskNo" label="任务单号" min-width="150" />
      <el-table-column label="运输线路" min-width="260">
        <template #default="{ row }">
          <route-cell
            :nodes="row.routeNodes"
            :origin="row.origin"
            :destination="row.destination"
          />
        </template>
      </el-table-column>
      <el-table-column
        prop="totalQuantity"
        label="台数"
        width="72"
        align="center"
      />
    </el-table>

    <div class="assign-carrier-section-title">选择承运方</div>

    <el-form :model="form" label-width="100px" v-loading="submitting">
      <task-carrier-picker
        ref="pickerRef"
        v-model="form.carrier"
        :simple-mode="true"
        :allowed-carrier-types="
          isBatch ? BATCH_ALLOWED_CARRIER_TYPES : undefined
        "
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
  import { InfoFilled, Right } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import TaskCarrierPicker from '../../task/components/task-carrier-picker.vue';
  import RouteCell from './route-cell.vue';
  import {
    batchCompleteCarrierAssignment,
    completeCarrierAssignment,
    listTaskWaybillItems
  } from '@/api/operation/task';
  import type { Task, TaskCarrierInfo } from '@/api/operation/task/model';
  import { CARRIER_TYPE, TASK_STATUS } from '../../task/status-config';
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

  const batchTotalQuantity = computed(() =>
    taskList.value.reduce((sum, t) => sum + (t.totalQuantity || 0), 0)
  );

  const dialogTitle = computed(() =>
    isBatch.value ? `批量分配承运（${taskList.value.length} 单）` : '分配承运'
  );

  const submitLabel = computed(() =>
    isBatch.value ? `确认批量分配（${taskList.value.length}）` : '确认分配'
  );

  const defaultCarrier = (): TaskCarrierInfo => ({
    carrierType: CARRIER_TYPE.SELF,
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
    if (isBatch.value && c.carrierType === CARRIER_TYPE.SOCIAL) {
      return '社会运力不支持批量分配，请逐单操作';
    }
    if (
      c.carrierType === CARRIER_TYPE.CARRIER &&
      !c.carrierId &&
      !c.carrierName?.trim()
    ) {
      return '请选择承运商';
    }
    if (c.carrierType === CARRIER_TYPE.SOCIAL) {
      if (!c.socialDriverId) {
        return '请选择社会运力';
      }
      if (
        !c.mainDriverName?.trim() ||
        !c.mainDriverPhone?.trim() ||
        !c.plateNumber?.trim()
      ) {
        return '所选社会运力信息不完整，请重新选择';
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
      if (
        (task.status ?? TASK_STATUS.PENDING_DISPATCH) !==
        TASK_STATUS.PENDING_ASSIGN
      ) {
        EleMessage.warning({
          message: '仅待分配状态可执行本操作',
          plain: true
        });
        return;
      }
      await completeCarrierAssignment(task.id, form.carrier);
      const nextStage =
        form.carrier.carrierType === CARRIER_TYPE.SOCIAL ? '待装车' : '待派车';
      EleMessage.success({
        message: `已确认承运分配，任务已进入${nextStage}`,
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

  .assign-carrier-dialog-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding-right: 32px;
  }

  .assign-carrier-dialog-header__title {
    font-size: 16px;
    font-weight: 600;
    line-height: 1.4;
    color: var(--el-text-color-primary);
  }

  .assign-carrier-dialog-header__info {
    flex-shrink: 0;
    color: var(--el-color-warning);
    cursor: help;
  }

  .assign-carrier-dialog-header__tip {
    max-width: 340px;
    line-height: 1.55;
  }

  .assign-carrier-batch-summary {
    display: flex;
    align-items: baseline;
    gap: 20px;
    margin-bottom: 12px;
    padding: 14px 18px;
    border-radius: 8px;
    background: linear-gradient(
      135deg,
      var(--el-color-primary-light-9) 0%,
      var(--el-fill-color-blank) 100%
    );
    border: 1px solid var(--el-color-primary-light-7);
  }

  .assign-carrier-batch-summary__item {
    display: flex;
    align-items: baseline;
    gap: 6px;
  }

  .assign-carrier-batch-summary__label {
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  .assign-carrier-batch-summary__value {
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
    color: var(--el-color-primary);
  }

  .assign-carrier-batch-summary__unit {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-color-primary);
  }

  .assign-carrier-batch-summary__divider {
    width: 1px;
    height: 28px;
    align-self: center;
    background: var(--el-border-color);
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
