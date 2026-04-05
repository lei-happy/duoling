<template>
  <ele-modal
    form
    :width="460"
    :title="isUpdate ? '修改地区' : '添加地区'"
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
      <el-form-item>
        <floating-label
          label="上级地区"
          type="input"
          :model-value="currentParentName"
          disabled
        />
      </el-form-item>
      <el-form-item prop="name">
        <floating-label
          label="请输入地区名称"
          type="input"
          v-model.trim="form.name"
          :maxlength="50"
          clearable
        />
      </el-form-item>
      <el-form-item prop="shortName">
        <floating-label
          label="简称"
          type="input"
          v-model.trim="form.shortName"
          :maxlength="50"
          clearable
        />
      </el-form-item>
      <el-form-item prop="sortOrder">
        <floating-label label="排序号" type="input-number">
          <el-input-number
            v-model="form.sortOrder"
            :min="0"
            :max="9999"
            controls-position="right"
            style="width: 100%"
          />
        </floating-label>
      </el-form-item>
      <el-form-item prop="status">
        <el-radio-group v-model="form.status">
          <el-radio :value="1">正常</el-radio>
          <el-radio :value="0">停用</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
          { preset: 'save', onClick: () => handleSave() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, computed } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { addRegion, updateRegion } from '@/api/basic-data/region';
  import type { Region } from '@/api/basic-data/region/model';

  const props = defineProps<{
    data?: Region | null;
    pcode?: number;
    parentName?: string;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(false);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);

  const [form, _resetFields, assignFields] = useFormData({
    code: void 0 as number | undefined,
    name: '',
    shortName: '',
    sortOrder: 0,
    status: 1
  });

  const rules: FormRules = {
    name: [
      {
        required: true,
        message: '请输入地区名称',
        type: 'string',
        trigger: 'blur'
      }
    ]
  };

  const currentParentName = computed(() => {
    if (isUpdate.value && props.data) {
      return props.parentName || String(props.data.pcode ?? '') || '—';
    }
    return props.parentName || '—';
  });

  const handleCancel = () => {
    closeModal();
  };

  const handleSave = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;

      const promise = isUpdate.value
        ? updateRegion(form.code!, {
            name: form.name,
            shortName: form.shortName || undefined,
            sortOrder: form.sortOrder,
            status: form.status
          })
        : addRegion({
            name: form.name,
            shortName: form.shortName || undefined,
            pcode: props.pcode,
            sortOrder: form.sortOrder,
            status: form.status
          });

      promise
        .then((msg) => {
          loading.value = false;
          EleMessage.success({ message: msg, plain: true });
          emit('done');
          handleCancel();
        })
        .catch((e) => {
          loading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };

  if (props.data) {
    assignFields({
      code: props.data.code,
      name: props.data.name ?? '',
      shortName: props.data.shortName ?? '',
      sortOrder: props.data.sortOrder ?? 0,
      status: props.data.status ?? 1
    });
    isUpdate.value = true;
  }
</script>
