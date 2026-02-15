<template>
  <EleModal
    :form="true"
    :width="460"
    :title="lang.renameTitle"
    :zIndex="baseIndex"
    :appendToBody="false"
    v-bind="modalProps || {}"
    v-model="visible"
    @open="handleOpen"
    @closed="handleClosed"
  >
    <ElForm ref="formRef" :model="form" labelWidth="82px" @submit.prevent="">
      <ElFormItem
        :label="isEditFile ? lang.fileName : lang.groupName"
        prop="name"
        :rules="[
          {
            required: true,
            message: isEditFile
              ? lang.fileNamePlaceholder
              : lang.groupNamePlaceholder,
            type: 'string',
            trigger: 'blur'
          }
        ]"
      >
        <ElInput
          :maxlength="20"
          :clearable="true"
          v-model="form.name"
          :placeholder="
            isEditFile ? lang.fileNamePlaceholder : lang.groupNamePlaceholder
          "
        />
      </ElFormItem>
    </ElForm>
    <template #footer>
      <BtnItems
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
          { preset: 'save', onClick: () => save() }
        ]"
      />
    </template>
  </EleModal>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import type { FormInstance } from 'element-plus';
  import type { EleModalProps } from 'ele-admin-plus/es/ele-app/plus';
  import { useFormData } from '@/utils/use-form-data';
  import BtnItems from '@/components/BtnItems/index.vue';
  import type { FilePickerLocale, UserFile } from '../types';
  import { renameGroupApi, renameFileApi } from '../config';

  const props = defineProps<{
    /** 是否是操作文件 */
    isEditFile?: boolean;
    /** 文件数据 */
    data?: UserFile | null;
    /** 弹窗参数 */
    modalProps?: Omit<EleModalProps, 'modelValue'>;
    /** 统一设置层级 */
    baseIndex?: number;
    /** 消息提示组件 */
    messageIns?: any;
    /** 组件文案 */
    lang: FilePickerLocale;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  /** 弹窗是否打开 */
  const visible = defineModel({ type: Boolean });

  /** 表单实例 */
  const formRef = ref<FormInstance | null>(null);

  /** 提交状态 */
  const loading = ref(false);

  /** 表单数据 */
  const [form, resetFields] = useFormData<UserFile>({ name: '' });

  /** 关闭弹窗 */
  const handleCancel = () => {
    visible.value = false;
  };

  /** 保存编辑 */
  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      const renameApi = props.isEditFile ? renameFileApi : renameGroupApi;
      loading.value = true;
      renameApi({ ...form, id: props.data?.id })
        .then((msg) => {
          loading.value = false;
          props.messageIns?.success?.(msg);
          handleCancel();
          emit('done');
        })
        .catch((e) => {
          loading.value = false;
          props.messageIns?.error?.(e.message);
        });
    });
  };

  /** 弹窗关闭事件 */
  const handleClosed = () => {
    resetFields();
    formRef.value?.clearValidate?.();
  };

  /** 弹窗打开事件 */
  const handleOpen = () => {
    if (props.data) {
      form.name = props.data.name;
    }
  };
</script>
