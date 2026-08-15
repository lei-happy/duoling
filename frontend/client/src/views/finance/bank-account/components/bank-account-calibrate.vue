<template>
  <el-dialog
    title="余额校准"
    :model-value="visible"
    width="520px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <div v-if="account" class="finance-identity">
      <div class="finance-identity__name">{{ account.accountName }}</div>
      <div class="finance-identity__meta">
        当前账面余额 ¥ {{ formatMoney(account.balance) }}
        <template v-if="account.accountNoMasked">
          · {{ account.accountNoMasked }}
        </template>
      </div>
    </div>
    <p class="finance-form-tip">
      按银行实际余额改账面数。校准会留痕，请写清原因，方便以后对账。
    </p>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="finance-edit-form"
      @submit.prevent=""
    >
      <el-form-item prop="balance">
        <floating-label
          v-model="form.balance"
          label="请输入银行实际余额"
          type="input-number"
          :input-number-precision="2"
          :input-number-step="100"
          input-number-controls-position="right"
        />
      </el-form-item>
      <el-form-item prop="reason">
        <floating-label
          label="请说明校准原因，至少 5 个字"
          type="input"
          input-type="textarea"
          v-model="form.reason"
          :clearable="false"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        确认校准
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { nextTick, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { calibrateBankAccount } from '@/api/finance/bank-account';
  import type { BankAccountItem } from '@/api/finance/bank-account/model';
  import { formatMoney } from '../../status-config';

  const props = defineProps<{
    visible: boolean;
    account: BankAccountItem | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive({ balance: 0, reason: '' });

  const rules = reactive<FormRules>({
    balance: [{ required: true, message: '请填写银行实际余额', trigger: 'change' }],
    reason: [
      { required: true, message: '请填写校准原因', trigger: 'blur' },
      { min: 5, message: '原因至少写 5 个字，方便日后追溯', trigger: 'blur' }
    ]
  });

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        balance: Number(props.account?.balance ?? 0),
        reason: ''
      });
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid || !props.account?.id) return;
      loading.value = true;
      try {
        await calibrateBankAccount(props.account.id, {
          balance: Number(form.balance),
          reason: form.reason
        });
        EleMessage.success({ message: '余额已校准', plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: unknown) {
        EleMessage.error({
          message: (e as { message?: string }).message || '校准失败，请重试',
          plain: true
        });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped lang="scss">
  @use '../../_shared/ui.scss';
</style>
