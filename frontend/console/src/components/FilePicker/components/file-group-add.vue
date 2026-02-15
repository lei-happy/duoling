<template>
  <EleModal
    :form="true"
    :width="460"
    :title="lang.groupAddTitle"
    :zIndex="baseIndex"
    :appendToBody="false"
    :loading="loading"
    v-bind="modalProps || {}"
    v-model="visible"
    @open="handleOpen"
    @closed="handleClosed"
  >
    <ElForm ref="formRef" :model="form" labelWidth="82px" @submit.prevent="">
      <ElFormItem :label="lang.groupParent" prop="parentId">
        <ElTreeSelect
          v-model="form.parentId"
          :data="groupData.filter((d) => d.id !== 0 && d.id !== -1)"
          nodeKey="id"
          :props="{ label: 'name' }"
          :clearable="true"
          :checkStrictly="true"
          :defaultExpandAll="true"
          :placeholder="lang.groupParentPlaceholder"
          :popperOptions="{ strategy: 'fixed' }"
          :teleported="false"
          class="ele-fluid"
        >
          <template #default="{ data }">
            <img
              src="/ele-file-list/ic_file_folder.png"
              class="ele-file-picker-tree-icon"
            />
            <span>{{ data.name }}</span>
          </template>
          <template v-if="form.parentId" #prefix>
            <img
              src="/ele-file-list/ic_file_folder.png"
              class="ele-file-picker-tree-icon"
            />
          </template>
        </ElTreeSelect>
      </ElFormItem>
      <ElFormItem
        :label="lang.groupName"
        prop="name"
        :rules="[
          {
            required: true,
            message: lang.groupNamePlaceholder,
            type: 'string',
            trigger: 'blur'
          }
        ]"
      >
        <ElInput
          :maxlength="200"
          :clearable="true"
          v-model="form.name"
          :placeholder="lang.groupNamePlaceholder"
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
  import { addGroupApi } from '../config';

  const props = defineProps<{
    /** 上级分组 */
    parentId?: number;
    /** 分组数据 */
    groupData: UserFile[];
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
  const [form, resetFields] = useFormData<UserFile>({
    name: '',
    parentId: void 0
  });

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
      loading.value = true;
      addGroupApi({ ...form, isDirectory: 1 })
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
    if (props.parentId != null) {
      form.parentId = props.parentId;
    }
  };
</script>
