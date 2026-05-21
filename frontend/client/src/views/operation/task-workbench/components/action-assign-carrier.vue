<!--
  待分配 → 待派车：确认承运方式（承运商 / 社会运力 / 自有车可先不定运力）

  - 单条：三种承运方式均可选（社会运力需填写司机信息）
  - 批量：仅支持自有车 / 承运商，统一写入后进入待派车
-->
<template>
  <el-dialog
    :model-value="visible"
    :title="dialogTitle"
    :width="isBatch ? '860px' : '780px'"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-alert
      v-if="!isBatch && primaryTask"
      type="info"
      :closable="false"
      style="margin-bottom: 12px"
      :title="taskSummary(primaryTask)"
    />
    <el-alert
      v-else-if="isBatch"
      type="info"
      :closable="false"
      style="margin-bottom: 12px"
      :title="`已选 ${taskList.length} 张任务单，将统一确认承运方式并进入「待派车」`"
    />
    <el-alert
      type="warning"
      :closable="false"
      style="margin-bottom: 12px"
      :title="warningTitle"
    />

    <el-table
      v-if="isBatch"
      :data="taskList"
      size="small"
      border
      max-height="220"
      style="width: 100%; margin-bottom: 12px"
    >
      <el-table-column prop="taskNo" label="任务单号" min-width="150" />
      <el-table-column label="运输线路" min-width="200">
        <template #default="{ row }">
          {{ row.origin || '--' }} → {{ row.destination || '--' }}
        </template>
      </el-table-column>
      <el-table-column prop="totalQuantity" label="台数" width="72" align="center" />
    </el-table>

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
  import { EleMessage } from 'ele-admin-plus';
  import TaskCarrierPicker from '../../task/components/task-carrier-picker.vue';
  import {
    batchCompleteCarrierAssignment,
    completeCarrierAssignment
  } from '@/api/operation/task';
  import type { Task, TaskCarrierInfo } from '@/api/operation/task/model';

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

  const warningTitle = computed(() =>
    isBatch.value
      ? '批量分配仅支持「自有车」或「承运商」。社会运力对应具体司机，请逐单分配。自有车可在待派车池再绑定运力。'
      : '本步确认承运方式后，任务进入「待派车」。自有车若暂未选运力，可在待派车池完成派车时再绑定。'
  );

  const submitLabel = computed(() =>
    isBatch.value ? `确认批量分配（${taskList.value.length}）` : '确认分配'
  );

  const taskSummary = (task: Task) =>
    `任务单 ${task.taskNo} · ${task.origin || '--'} → ${task.destination || '--'} · ${task.totalQuantity || 0} 台`;

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
    } else {
      form.carrier = defaultCarrier();
    }
    nextTick(() => pickerRef.value?.init?.());
  };

  const validateAssignment = (c: TaskCarrierInfo): string | null => {
    if (isBatch.value && c.carrierType === 3) {
      return '社会运力不支持批量分配，请逐单操作';
    }
    if (c.carrierType === 2 && !c.carrierId && !c.carrierName?.trim()) {
      return '请选择承运商或填写承运商名称';
    }
    if (c.carrierType === 3) {
      if (!c.mainDriverName?.trim()) return '请填写司机姓名';
      if (!c.mainDriverPhone?.trim()) return '请填写司机电话';
      if (!c.plateNumber?.trim()) return '请填写车牌号';
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
