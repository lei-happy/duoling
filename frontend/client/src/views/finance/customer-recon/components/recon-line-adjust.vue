<template>
  <el-dialog
    :model-value="visible"
    title="调整对账行"
    width="520px"
    destroy-on-close
    draggable
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <div class="finance-identity">
      <div class="finance-identity__name">{{ line?.waybillNo || '--' }}</div>
      <div class="finance-identity__meta">
        快照运费 ¥ {{ formatMoney(line?.freightAmountSnapshot) }}
        · 建行时冻结，调整不会改动运单
      </div>
    </div>
    <el-form :model="form" label-width="0" class="finance-edit-form">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.quantity"
              label="请输入数量"
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
              label="请输入单价"
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
              label="请输入调整金额，正数加收、负数扣减"
              type="input-number"
              :input-number-precision="2"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <floating-label
              label="请输入调整原因，有调整金额时必填"
              type="input"
              input-type="textarea"
              v-model="form.adjustReason"
              :maxlength="200"
              :clearable="false"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <floating-label
              label="请输入行备注，选填"
              type="input"
              v-model="form.remark"
              :maxlength="200"
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
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { adjustReconLine } from '@/api/finance/customer-recon';
  import type { ReconLine } from '@/api/finance/customer-recon/model';
  import { formatMoney } from '../../status-config';

  const props = defineProps<{
    visible: boolean;
    reconId: number;
    line?: ReconLine | null;
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
      await adjustReconLine(props.reconId, props.line.id, form.value);
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
