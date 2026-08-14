<template>
  <el-dialog
    :model-value="visible"
    title="调整对账行"
    width="540px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-form :model="form" label-width="96px">
      <el-form-item label="任务号">
        <span>{{ line?.taskNo || '--' }}</span>
      </el-form-item>
      <el-form-item label="快照成本">
        <span class="num">
          ¥ {{ formatMoney(line?.carrierCostSnapshot) }}
          <span class="hint">（建行时冻结的业务事实，调整不会改动任务）</span>
        </span>
      </el-form-item>
      <el-form-item label="已预付扣减">
        <span class="num offset">
          ¥ {{ formatMoney(line?.prepaidOffsetAmount) }}
          <span class="hint">预付已实付，不可改；要补回请用调整金额</span>
        </span>
      </el-form-item>
      <el-form-item label="数量">
        <el-input-number
          v-model="form.quantity"
          :min="0"
          :precision="2"
          :controls="false"
          style="width: 160px"
        />
      </el-form-item>
      <el-form-item label="单价">
        <el-input-number
          v-model="form.unitPrice"
          :min="0"
          :precision="2"
          :controls="false"
          style="width: 160px"
        />
      </el-form-item>
      <el-form-item label="调整金额">
        <el-input-number
          v-model="form.adjustAmount"
          :precision="2"
          :controls="false"
          style="width: 160px"
        />
        <span class="hint">正数补付、负数扣款</span>
      </el-form-item>
      <el-form-item label="调整原因">
        <el-input
          v-model="form.adjustReason"
          type="textarea"
          :rows="2"
          maxlength="200"
          placeholder="有调整金额时必填，承运商核对时会看到"
        />
      </el-form-item>
      <el-form-item label="行备注">
        <el-input v-model="form.remark" maxlength="200" placeholder="选填" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { adjustCarrierReconLine } from '@/api/finance/carrier-recon';
  import type { CarrierReconLine } from '@/api/finance/carrier-recon/model';
  import { formatMoney } from '../../status-config';

  const props = defineProps<{
    visible: boolean;
    reconId: number;
    line?: CarrierReconLine | null;
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

  const onOpen = () => {
    form.value = {
      quantity: props.line?.quantity,
      unitPrice: props.line?.unitPrice,
      adjustAmount: props.line?.adjustAmount,
      adjustReason: props.line?.adjustReason,
      remark: props.line?.remark
    };
  };

  const save = async () => {
    if (!props.line) return;
    if (
      Number(form.value.adjustAmount || 0) !== 0 &&
      !form.value.adjustReason
    ) {
      EleMessage.warning({ message: '请填写调整原因', plain: true });
      return;
    }
    saving.value = true;
    try {
      await adjustCarrierReconLine(props.reconId, props.line.id, form.value);
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
  .num {
    font-variant-numeric: tabular-nums;
  }

  .offset {
    color: var(--el-color-info);
  }

  .hint {
    margin-left: 8px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }
</style>
