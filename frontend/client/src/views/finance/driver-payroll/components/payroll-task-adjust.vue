<template>
  <el-dialog
    :model-value="visible"
    title="调整任务提成"
    width="520px"
    destroy-on-close
    draggable
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <div class="finance-identity">
      <div class="finance-identity__name">{{ link?.taskNo || '--' }}</div>
      <div class="finance-identity__meta">
        <template v-if="link?.plateNumber">{{ link.plateNumber }} · </template>
        交车台数 {{ link?.signedQuantitySnapshot ?? '--' }}
        · 本行提成预计 ¥ {{ formatMoney(previewAmount) }}
      </div>
    </div>
    <el-form :model="form" label-width="0" class="finance-edit-form">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.quantity"
              label="请输入计件数量"
              type="input-number"
              :input-number-min="0"
              :input-number-precision="2"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.unitPrice"
              label="请输入提成单价"
              type="input-number"
              :input-number-min="0"
              :input-number-precision="2"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <floating-label
              v-model="form.adjustAmount"
              label="请输入额外调整，补贴填正、扣减填负"
              type="input-number"
              :input-number-precision="2"
            />
          </el-form-item>
        </el-col>
        <el-col v-if="needReason" :span="24">
          <el-form-item>
            <floating-label
              label="请说明调整原因，会记进操作记录"
              type="input"
              input-type="textarea"
              v-model="form.adjustReason"
              :maxlength="255"
              :clearable="false"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <floating-label
              label="请输入备注，选填"
              type="input"
              v-model="form.remark"
              :maxlength="255"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { adjustPayrollTask } from '@/api/finance/driver-payroll';
  import type { PayrollTaskLink } from '@/api/finance/driver-payroll/model';
  import { formatMoney } from '../../status-config';

  const props = defineProps<{
    visible: boolean;
    payrollId?: number | null;
    link?: PayrollTaskLink | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const saving = ref(false);
  const form = ref<{
    quantity?: number;
    unitPrice?: number;
    adjustAmount?: number;
    adjustReason?: string;
    remark?: string;
  }>({});

  const needReason = computed(() => {
    if (!props.link) return false;
    return (
      Number(form.value.adjustAmount || 0) !== 0 ||
      Number(form.value.quantity ?? props.link.quantity) !==
        Number(props.link.quantity) ||
      Number(form.value.unitPrice ?? props.link.unitPrice) !==
        Number(props.link.unitPrice)
    );
  });

  const previewAmount = computed(() => {
    const q = Number(form.value.quantity ?? props.link?.quantity ?? 0);
    const p = Number(form.value.unitPrice ?? props.link?.unitPrice ?? 0);
    return q * p + Number(form.value.adjustAmount || 0);
  });

  const onOpen = () => {
    form.value = {
      quantity: props.link?.quantity,
      unitPrice: props.link?.unitPrice,
      adjustAmount: props.link?.adjustAmount || void 0,
      adjustReason: props.link?.adjustReason,
      remark: props.link?.remark
    };
  };

  const save = async () => {
    if (!props.payrollId || !props.link) return;
    if (needReason.value && (form.value.adjustReason || '').trim().length < 5) {
      EleMessage.warning({
        message: '调整了金额，请写清原因（不少于 5 个字）',
        plain: true
      });
      return;
    }
    saving.value = true;
    try {
      await adjustPayrollTask(props.payrollId, props.link.id, {
        quantity: form.value.quantity,
        unitPrice: form.value.unitPrice,
        adjustAmount: form.value.adjustAmount,
        adjustReason: form.value.adjustReason,
        remark: form.value.remark
      });
      EleMessage.success({ message: '已保存调整', plain: true });
      emit('update:visible', false);
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '保存失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  @use '../../_shared/ui.scss';
</style>
