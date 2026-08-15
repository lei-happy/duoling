<template>
  <el-dialog
    title="登记充值"
    :model-value="visible"
    width="560px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <p class="form-tip">先记下要打给供应商的金额。确认打款后再入账，账户余额才会增加。</p>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="energy-edit-form"
      @submit.prevent=""
    >
      <el-form-item prop="accountId">
        <floating-label
          v-model="form.accountId"
          label="请选择能源账户"
          type="select"
          filterable
          :clearable="false"
        >
          <el-option
            v-for="a in accounts"
            :key="a.id"
            :label="`${a.accountName}（余额 ${a.ledgerBalance ?? 0}）`"
            :value="a.id"
          />
        </floating-label>
      </el-form-item>
      <el-form-item prop="plannedAmount">
        <floating-label
          v-model="form.plannedAmount"
          label="请输入充值金额"
          type="input-number"
          :input-number-min="0.01"
          :input-number-precision="2"
          :input-number-step="100"
          input-number-controls-position="right"
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          v-model="form.rechargeTime"
          label="请选择充值时间"
          type="date"
          date-type="datetime"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          label="请输入付款账户名称"
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
      <el-form-item>
        <floating-label
          label="请输入备注"
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
        保存草稿
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { nextTick, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { addRecharge } from '@/api/energy';

  const props = defineProps<{
    visible: boolean;
    accounts: Array<Record<string, any>>;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Record<string, any>>({});

  const rules = reactive<FormRules>({
    accountId: [
      { required: true, message: '请选择能源账户', trigger: 'change' }
    ],
    plannedAmount: [
      { required: true, message: '请输入充值金额', trigger: 'change' }
    ]
  });

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        accountId: undefined,
        plannedAmount: undefined,
        rechargeTime: '',
        bankAccountLabel: '',
        paymentReference: '',
        remark: ''
      });
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        await addRecharge(form);
        EleMessage.success({
          message: '已登记充值单，确认打款后再入账',
          plain: true
        });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        if (e?.message) EleMessage.error({ message: e.message, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
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
