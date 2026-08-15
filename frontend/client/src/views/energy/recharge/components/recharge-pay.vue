<template>
  <el-dialog
    title="登记入账"
    :model-value="visible"
    width="520px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <div v-if="data" class="pay-identity">
      <div class="pay-identity__name">{{ data.docNo }}</div>
      <div class="pay-identity__meta">
        {{ data.accountName }} · 计划 {{ formatMoney(data.plannedAmount) }}
      </div>
    </div>
    <p class="form-tip">确认已经向供应商打款后，再入账。入账后会增加能源账户余额。</p>
    <el-form
      :model="form"
      label-width="0"
      class="energy-edit-form"
      @submit.prevent=""
    >
      <el-form-item>
        <floating-label
          v-model="form.actualAmount"
          label="请输入实付金额"
          type="input-number"
          :input-number-min="0.01"
          :input-number-precision="2"
          input-number-controls-position="right"
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          label="请输入付款账户"
          type="input"
          v-model.trim="form.bankAccountLabel"
          clearable
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          label="请输入回单号"
          type="input"
          v-model.trim="form.paymentReference"
          clearable
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        确认入账
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { reactive, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { payRecharge } from '@/api/energy';
  import { formatMoney } from '../../_shared/options';

  const props = defineProps<{
    visible: boolean;
    data: Record<string, any> | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const loading = ref(false);
  const form = reactive<Record<string, any>>({});

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        id: props.data?.id,
        actualAmount: props.data?.plannedAmount,
        bankAccountLabel: props.data?.bankAccountLabel || '',
        paymentReference: props.data?.paymentReference || ''
      });
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = async () => {
    if (!form.id) return;
    loading.value = true;
    try {
      await payRecharge(form.id, form);
      EleMessage.success({ message: '已入账到能源账户', plain: true });
      updateVisible(false);
      emit('done');
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '入账失败，请稍后重试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };
</script>

<style scoped>
  .pay-identity {
    margin-bottom: 12px;
    padding: 12px 14px;
    border-radius: 8px;
    background: var(--el-fill-color-light);
  }

  .pay-identity__name {
    font-weight: 600;
  }

  .pay-identity__meta {
    margin-top: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .form-tip {
    margin: 0 0 16px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
    line-height: 1.7;
  }

  .energy-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
</style>
