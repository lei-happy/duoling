<template>
  <el-dialog
    title="账户余额对账"
    :model-value="visible"
    width="520px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <p class="form-tip">把供应商侧看到的余额填进来，系统会和账面余额比出差异。</p>
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
            :label="`${a.accountName}（账面 ${a.ledgerBalance ?? 0}）`"
            :value="a.id"
          />
        </floating-label>
      </el-form-item>
      <el-form-item prop="supplierBalance">
        <floating-label
          v-model="form.supplierBalance"
          label="请输入供应商侧余额"
          type="input-number"
          :input-number-precision="2"
          input-number-controls-position="right"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        生成对账单
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { nextTick, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { createBalanceRecon } from '@/api/energy';

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
    supplierBalance: [
      { required: true, message: '请输入供应商侧余额', trigger: 'change' }
    ]
  });

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, { accountId: undefined, supplierBalance: undefined });
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        await createBalanceRecon(form);
        EleMessage.success({ message: '已生成余额对账单', plain: true });
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
