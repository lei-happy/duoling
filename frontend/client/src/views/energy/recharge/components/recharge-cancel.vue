<template>
  <el-dialog
    title="撤销充值单"
    :model-value="visible"
    width="480px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="energy-edit-form"
      @submit.prevent=""
    >
      <el-form-item prop="reason">
        <floating-label
          label="请填写撤销原因，至少 5 个字"
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
        确认撤销
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { nextTick, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { cancelRecharge } from '@/api/energy';

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
  const form = reactive({ id: 0, reason: '' });

  const rules = reactive<FormRules>({
    reason: [
      { required: true, message: '请填写撤销原因', trigger: 'blur' },
      { min: 5, message: '撤销原因至少 5 个字', trigger: 'blur' }
    ]
  });

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, { id: props.data?.id, reason: '' });
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        await cancelRecharge(form.id, { reason: form.reason });
        EleMessage.success({ message: '已撤销充值单', plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        EleMessage.error({
          message: e.message || '撤销失败，请稍后重试',
          plain: true
        });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .energy-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
</style>
