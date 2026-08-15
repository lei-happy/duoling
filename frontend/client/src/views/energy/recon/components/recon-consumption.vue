<template>
  <el-dialog
    title="消费流水对账"
    :model-value="visible"
    width="560px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <p class="form-tip">把供应商账单按「流水号 金额」逐行贴进来，系统会和本期间消费比对。</p>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="energy-edit-form"
      @submit.prevent=""
    >
      <el-form-item>
        <floating-label
          v-model="form.accountId"
          label="请选择能源账户"
          type="select"
          filterable
          clearable
        >
          <el-option
            v-for="a in accounts"
            :key="a.id"
            :label="a.accountName"
            :value="a.id"
          />
        </floating-label>
      </el-form-item>
      <el-form-item prop="period">
        <floating-label
          v-model="form.period"
          label="请选择对账期间"
          type="date"
          date-type="datetimerange"
          value-format="YYYY-MM-DD HH:mm:ss"
          start-placeholder="开始"
          end-placeholder="结束"
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          label="请粘贴外部账单，每行：流水号 金额"
          type="input"
          input-type="textarea"
          v-model="form.externalText"
          :clearable="false"
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
  import { createConsumptionRecon } from '@/api/energy';

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
  const form = reactive<Record<string, any>>({ period: [], externalText: '' });

  const rules = reactive<FormRules>({
    period: [{ required: true, message: '请选择对账期间', trigger: 'change' }]
  });

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        accountId: undefined,
        period: [],
        externalText: ''
      });
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      const [start, end] = form.period || [];
      const externalRows = String(form.externalText || '')
        .split('\n')
        .map((line: string) => line.trim())
        .filter(Boolean)
        .map((line: string) => {
          const [id, amount] = line.split(/\s+/);
          return { externalTransactionId: id, amount: Number(amount) };
        });
      loading.value = true;
      try {
        await createConsumptionRecon({
          accountId: form.accountId,
          start,
          end,
          externalRows
        });
        EleMessage.success({ message: '已生成流水对账单', plain: true });
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
