<template>
  <el-dialog
    title="调账"
    :model-value="visible"
    width="520px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <div v-if="account" class="adjust-identity">
      <div class="adjust-identity__name">{{ account.accountName }}</div>
      <div class="adjust-identity__meta">
        账面余额 {{ formatMoney(account.ledgerBalance) }} · 可用
        {{ formatMoney(account.availableBalance) }}
      </div>
    </div>
    <p class="form-tip">
      正数增加账面余额，负数减少。调账会留下流水，不能直接改余额。
    </p>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="energy-edit-form"
      @submit.prevent=""
    >
      <el-form-item prop="amount">
        <floating-label
          v-model="form.amount"
          label="请输入调账金额"
          type="input-number"
          :input-number-precision="2"
          :input-number-step="100"
          input-number-controls-position="right"
        />
      </el-form-item>
      <el-form-item prop="remark">
        <floating-label
          label="请说明调账原因"
          type="input"
          input-type="textarea"
          v-model="form.remark"
          :clearable="false"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        确认调账
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { nextTick, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { adjustAccount } from '@/api/energy';
  import { formatMoney } from '../../_shared/options';

  const props = defineProps<{
    visible: boolean;
    account: Record<string, any> | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive({ amount: 0, remark: '' });

  const rules = reactive<FormRules>({
    amount: [{ required: true, message: '请输入调账金额', trigger: 'change' }],
    remark: [{ required: true, message: '请填写调账原因', trigger: 'blur' }]
  });

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, { amount: 0, remark: '' });
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      if (!form.amount) {
        EleMessage.error({ message: '调账金额不能为 0', plain: true });
        return;
      }
      if (!props.account?.id) return;
      loading.value = true;
      try {
        await adjustAccount(props.account.id, {
          amount: form.amount,
          remark: form.remark
        });
        EleMessage.success({ message: '已完成调账', plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        EleMessage.error({
          message: e.message || '调账失败，请稍后重试',
          plain: true
        });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .adjust-identity {
    margin-bottom: 12px;
    padding: 12px 14px;
    border-radius: 8px;
    background: var(--el-fill-color-light);
  }

  .adjust-identity__name {
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .adjust-identity__meta {
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
