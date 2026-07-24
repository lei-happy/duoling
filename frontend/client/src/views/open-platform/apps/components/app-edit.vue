<template>
  <ele-modal
    form
    :width="520"
    :title="isUpdate ? '编辑接入应用' : '新建接入应用'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      @submit.prevent=""
    >
      <el-form-item prop="name">
        <floating-label
          label="应用名称，如「我的 ERP 系统」「财务助手」"
          type="input"
          v-model.trim="form.name"
          :maxlength="50"
          clearable
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          label="用途备注（选填）"
          type="input"
          input-type="textarea"
          v-model.trim="form.description"
          :maxlength="200"
          :show-word-limit="true"
          clearable
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => closeModal() },
          { preset: 'save', onClick: () => save() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { createApp, updateApp } from '@/api/open-platform';
  import type { OpenApp } from '@/api/open-platform/model';

  const props = defineProps<{ data?: OpenApp | null }>();
  const emit = defineEmits<{ (e: 'done'): void }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(false);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);

  const [form, , assignFields] = useFormData<OpenApp>({
    id: void 0,
    name: '',
    description: '',
    status: 'enabled'
  });

  const rules = reactive<FormRules>({
    name: [{ required: true, message: '请填写应用名称', trigger: 'blur' }]
  });

  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;
      const payload = {
        name: form.name as string,
        description: form.description,
        status: form.status
      };
      const done = () => {
        loading.value = false;
        EleMessage.success({ message: '保存成功', plain: true });
        closeModal();
        emit('done');
      };
      const fail = (e: any) => {
        loading.value = false;
        EleMessage.error({
          message: e.message || '保存失败，请稍后重试',
          plain: true
        });
      };
      if (isUpdate.value && form.id) {
        updateApp(form.id, payload).then(done).catch(fail);
      } else {
        createApp(payload).then(done).catch(fail);
      }
    });
  };

  if (props.data) {
    assignFields({ ...props.data });
    isUpdate.value = true;
  }
</script>
