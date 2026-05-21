<!--
  待分配 → 待派车：确认承运方式（承运商 / 社会运力 / 自有车可先不定运力）

  与「派车」区分：本步只决定由谁承运，进入待派车后再做派车（绑定运力等）。
-->
<template>
  <el-dialog
    :model-value="visible"
    title="分配承运"
    width="780px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-alert
      v-if="task"
      type="info"
      :closable="false"
      style="margin-bottom: 12px"
      :title="`任务单 ${task.taskNo} · ${task.origin || '--'} → ${task.destination || '--'} · ${task.totalQuantity || 0} 台`"
    />
    <el-alert
      type="warning"
      :closable="false"
      style="margin-bottom: 12px"
      title="本步确认承运方式后，任务进入「待派车」。自有车若暂未选运力，可在待派车池完成派车时再绑定。"
    />

    <el-form :model="form" label-width="100px" v-loading="submitting">
      <task-carrier-picker
        ref="pickerRef"
        v-model="form.carrier"
        :simple-mode="true"
      />
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">
        确认分配
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { reactive, ref, nextTick } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import TaskCarrierPicker from '../../task/components/task-carrier-picker.vue';
  import { completeCarrierAssignment } from '@/api/operation/task';
  import type { Task, TaskCarrierInfo } from '@/api/operation/task/model';

  const props = defineProps<{
    visible: boolean;
    task: Task | null;
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const pickerRef = ref<{ init: () => void } | null>(null);
  const submitting = ref(false);

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
    if (props.task) {
      form.carrier = {
        carrierType: props.task.carrierType || 1,
        capacityId: props.task.capacityId ?? undefined,
        carrierId: props.task.carrierId ?? undefined,
        socialDriverId: props.task.socialDriverId ?? undefined,
        mainDriverName: props.task.mainDriverName || '',
        mainDriverPhone: props.task.mainDriverPhone || '',
        mainDriverIdCard: props.task.mainDriverIdCard || '',
        plateNumber: props.task.plateNumber || '',
        trailerPlateNumber: props.task.trailerPlateNumber || '',
        carrierName: props.task.carrierName || '',
        carrierShortName: props.task.carrierShortName || ''
      };
    } else {
      form.carrier = defaultCarrier();
    }
    nextTick(() => pickerRef.value?.init?.());
  };

  const validateAssignment = (c: TaskCarrierInfo): string | null => {
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

  const submit = async () => {
    if (!props.task?.id) {
      emit('update:visible', false);
      return;
    }
    if ((props.task.status ?? 0) !== -1) {
      EleMessage.warning({
        message: '仅待分配状态可执行本操作',
        plain: true
      });
      return;
    }
    const err = validateAssignment(form.carrier);
    if (err) {
      EleMessage.error({ message: err, plain: true });
      return;
    }
    submitting.value = true;
    try {
      await completeCarrierAssignment(props.task.id, form.carrier);
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
