<template>
  <el-dialog
    title="调整风控阈值"
    :model-value="visible"
    width="480px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <div v-if="data" class="rule-identity">
      <div class="rule-identity__name">{{ data.ruleName }}</div>
    </div>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="energy-edit-form"
      @submit.prevent=""
    >
      <el-form-item prop="thresholdValue">
        <floating-label
          v-model="form.thresholdValue"
          label="请输入阈值"
          type="input-number"
          :input-number-precision="3"
          input-number-controls-position="right"
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          v-model="form.riskLevel"
          label="请选择风险等级"
          type="select"
          :clearable="false"
        >
          <el-option
            v-for="o in RISK_LEVELS"
            :key="o.value"
            :label="o.label"
            :value="o.value"
          />
        </floating-label>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { nextTick, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { updateRule } from '@/api/energy';
  import { RISK_LEVELS } from '../../_shared/options';

  const props = defineProps<{
    visible: boolean;
    data: Record<string, any> | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Record<string, any>>({});

  const rules = reactive<FormRules>({
    thresholdValue: [
      { required: true, message: '请输入阈值', trigger: 'change' }
    ]
  });

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        id: props.data?.id,
        thresholdValue: props.data?.thresholdValue,
        riskLevel: props.data?.riskLevel || 'MEDIUM'
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
        await updateRule(form.id, {
          thresholdValue: form.thresholdValue,
          riskLevel: form.riskLevel
        });
        EleMessage.success({ message: '已更新阈值', plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        EleMessage.error({
          message: e.message || '保存失败，请稍后重试',
          plain: true
        });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .rule-identity {
    margin-bottom: 16px;
    padding: 12px 14px;
    border-radius: 8px;
    background: var(--el-fill-color-light);
  }

  .rule-identity__name {
    font-weight: 600;
  }

  .energy-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
</style>
