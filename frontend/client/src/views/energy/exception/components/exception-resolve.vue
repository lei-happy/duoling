<template>
  <el-dialog
    :title="form.status === 'ignored' ? '忽略异常' : '核实异常'"
    :model-value="visible"
    width="480px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <div v-if="data" class="resolve-identity">
      <div class="resolve-identity__name">
        {{ EXCEPTION_TYPES[data.exceptionType] || data.exceptionType }}
      </div>
      <div class="resolve-identity__meta">{{ data.exceptionMessage }}</div>
    </div>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="energy-edit-form"
      @submit.prevent=""
    >
      <el-form-item prop="remark">
        <floating-label
          label="请写下核实结论，方便以后复查"
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
        确认
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { nextTick, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { resolveException } from '@/api/energy';
  import { EXCEPTION_TYPES } from '../../_shared/options';

  const props = defineProps<{
    visible: boolean;
    data: Record<string, any> | null;
    nextStatus: string;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive({ id: 0, status: 'processed', remark: '' });

  const rules = reactive<FormRules>({
    remark: [{ required: true, message: '请填写处理说明', trigger: 'blur' }]
  });

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        id: props.data?.id,
        status: props.nextStatus,
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
        await resolveException(form.id, {
          status: form.status,
          remark: form.remark
        });
        EleMessage.success({
          message: form.status === 'ignored' ? '已忽略这条异常' : '已标记为处理完成',
          plain: true
        });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        EleMessage.error({
          message: e.message || '处理失败，请稍后重试',
          plain: true
        });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .resolve-identity {
    margin-bottom: 16px;
    padding: 12px 14px;
    border-radius: 8px;
    background: var(--el-fill-color-light);
  }

  .resolve-identity__name {
    font-weight: 600;
  }

  .resolve-identity__meta {
    margin-top: 4px;
    font-size: 12px;
    line-height: 1.6;
    color: var(--el-text-color-secondary);
  }

  .energy-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
</style>
