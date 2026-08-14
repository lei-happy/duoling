<template>
  <el-dialog
    :model-value="visible"
    title="调整任务提成"
    width="520px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-form :model="form" label-width="96px">
      <el-form-item label="任务号">
        <span>{{ link?.taskNo || '--' }}</span>
        <span v-if="link?.plateNumber" class="muted">
          {{ link.plateNumber }}
        </span>
      </el-form-item>
      <el-form-item label="交车台数">
        <span>{{ link?.signedQuantitySnapshot ?? '--' }}</span>
        <span class="muted">交车时的台数，改动量请填在下面</span>
      </el-form-item>
      <el-form-item label="计件数量">
        <el-input-number
          v-model="form.quantity"
          :min="0"
          :precision="2"
          :controls="false"
          style="width: 160px"
        />
      </el-form-item>
      <el-form-item label="提成单价">
        <el-input-number
          v-model="form.unitPrice"
          :min="0"
          :precision="2"
          :controls="false"
          style="width: 160px"
        />
      </el-form-item>
      <el-form-item label="额外调整">
        <el-input-number
          v-model="form.adjustAmount"
          :precision="2"
          :controls="false"
          placeholder="补贴填正、扣减填负"
          style="width: 160px"
        />
      </el-form-item>
      <el-form-item v-if="needReason" label="调整原因" required>
        <el-input
          v-model="form.adjustReason"
          type="textarea"
          :rows="2"
          maxlength="255"
          placeholder="说明为什么调整，会记进操作记录"
        />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" maxlength="255" placeholder="选填" />
      </el-form-item>
    </el-form>

    <div class="preview"> 本行提成预计 ¥ {{ formatMoney(previewAmount) }} </div>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
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
  .muted {
    margin-left: 8px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .preview {
    padding: 8px 12px;
    background: var(--el-fill-color-light);
    border-radius: 4px;
    font-variant-numeric: tabular-nums;
  }
</style>
