<!--
  派车弹窗（任务单 status 0 → 1，或已派车后换车）

  作业语义：调度员为任务单选择承运方（自有车/承运商/社会运力），完成派车。
  复用 task-carrier-picker.vue 作为承运方选择面板。
-->
<template>
  <el-dialog
    :model-value="visible"
    :title="title"
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

    <el-form
      ref="formRef"
      :model="form"
      label-width="100px"
      v-loading="submitting"
    >
      <task-carrier-picker ref="pickerRef" v-model="form.carrier" />

      <el-divider content-position="left">承运成本（可选）</el-divider>
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="成本类型">
            <el-select v-model="form.carrierCostType" clearable>
              <el-option
                v-for="o in CARRIER_COST_TYPE_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="成本总额">
            <el-input-number
              v-model="form.carrierCostAmount"
              :min="0"
              :precision="2"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="成本备注">
            <el-input v-model="form.costRemark" placeholder="可选" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">
        {{ isReassign ? '确认换车' : '确认派车' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, nextTick } from 'vue';
  import type { FormInstance } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import TaskCarrierPicker from '../../task/components/task-carrier-picker.vue';
  import { assignCarrier } from '@/api/operation/task';
  import type { Task, TaskCarrierInfo } from '@/api/operation/task/model';
  import { CARRIER_COST_TYPE_OPTIONS } from '../../task/status-config';

  const props = defineProps<{
    visible: boolean;
    task: Task | null;
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
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
    carrier: defaultCarrier(),
    carrierCostType: undefined as number | undefined,
    carrierCostAmount: undefined as number | undefined,
    costRemark: ''
  });

  const isReassign = computed(
    () => (props.task?.status ?? 0) === 1 && !!props.task?.carrierType
  );
  const title = computed(() => (isReassign.value ? '重新派车' : '派车'));

  const onOpen = () => {
    // 从任务单回填当前承运方信息作为预填
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
      form.carrierCostType = props.task.carrierCostType ?? undefined;
      form.carrierCostAmount = props.task.carrierCostAmount ?? undefined;
      form.costRemark = props.task.costRemark || '';
    } else {
      form.carrier = defaultCarrier();
      form.carrierCostType = undefined;
      form.carrierCostAmount = undefined;
      form.costRemark = '';
    }
    nextTick(() => pickerRef.value?.init?.());
  };

  const validateCarrier = (c: TaskCarrierInfo): string | null => {
    if (c.carrierType === 1 && !c.capacityId && !c.mainDriverName?.trim()) {
      return '请选择运力或填写主驾姓名';
    }
    if (c.carrierType === 2 && !c.carrierId) {
      return '请选择承运商';
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
    const err = validateCarrier(form.carrier);
    if (err) {
      EleMessage.error({ message: err, plain: true });
      return;
    }
    submitting.value = true;
    try {
      await assignCarrier(props.task.id, {
        carrier: form.carrier,
        carrierCostType: form.carrierCostType ?? null,
        carrierCostAmount: form.carrierCostAmount ?? null,
        costRemark: form.costRemark
      });
      EleMessage.success({
        message: isReassign.value ? '换车成功' : '派车成功',
        plain: true
      });
      emit('done');
      emit('update:visible', false);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '派车失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
    }
  };
</script>
