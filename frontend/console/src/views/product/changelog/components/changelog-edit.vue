<!-- 更新记录编辑弹窗 -->
<template>
  <ele-modal
    form
    :width="560"
    :title="isUpdate ? '修改更新记录' : '添加更新记录'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="90px"
      @submit.prevent=""
    >
      <el-form-item label="版本号" prop="version">
        <el-input
          clearable
          :maxlength="50"
          v-model="form.version"
          placeholder="如 v1.2.0"
        />
      </el-form-item>
      <el-form-item label="更新标题" prop="title">
        <el-input
          clearable
          :maxlength="200"
          v-model="form.title"
          placeholder="请输入更新标题"
        />
      </el-form-item>
      <el-form-item label="发布日期" prop="release_date">
        <el-date-picker
          v-model="form.release_date"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="选择发布日期"
          class="ele-fluid"
        />
      </el-form-item>
      <el-form-item label="排序号" prop="sort_order">
        <el-input-number
          :min="0"
          :max="9999"
          v-model="form.sort_order"
          placeholder="越大越靠前"
          controls-position="right"
          class="ele-fluid"
        />
      </el-form-item>
      <el-form-item label="状态" prop="status" v-if="isUpdate">
        <el-radio-group v-model="form.status">
          <el-radio :value="1">已发布</el-radio>
          <el-radio :value="0">停用</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="更新内容" prop="content">
        <el-input
          :rows="8"
          type="textarea"
          v-model="form.content"
          placeholder="支持 Markdown 格式"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
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
  import { useFormData } from '@/utils/use-form-data';
  import {
    addChangelog,
    updateChangelog
  } from '@/api/changelog';
  import type { Changelog } from '@/api/changelog/model';

  const props = defineProps<{
    /** 修改回显的数据 */
    data?: Changelog | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  /** 是否是修改 */
  const isUpdate = ref(false);

  /** 提交状态 */
  const loading = ref(false);

  /** 表单实例 */
  const formRef = ref<FormInstance | null>(null);

  /** 表单数据 */
  const [form, _resetFields, assignFields] = useFormData<Changelog & { release_date?: string }>({
    id: void 0,
    version: '',
    title: '',
    content: '',
    release_date: '',
    sort_order: 0,
    status: 1
  });

  /** 表单验证规则 */
  const rules = reactive<FormRules>({
    version: [
      { required: true, message: '请输入版本号', type: 'string', trigger: 'blur' }
    ],
    title: [
      { required: true, message: '请输入更新标题', type: 'string', trigger: 'blur' }
    ],
    release_date: [
      { required: true, message: '请选择发布日期', type: 'string', trigger: 'change' }
    ]
  });

  /** 关闭弹窗 */
  const handleCancel = () => {
    closeModal();
  };

  /** 保存编辑 */
  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;
      const saveOrUpdate = isUpdate.value
        ? () => updateChangelog(form.id!, form)
        : () => addChangelog({
            version: form.version,
            title: form.title,
            content: form.content,
            release_date: form.release_date,
            sort_order: form.sort_order ?? 0
          });
      saveOrUpdate()
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

  /** 修改赋值 */
  if (props.data) {
    assignFields({
      ...props.data,
      release_date: props.data.release_date || ''
    });
    isUpdate.value = true;
  }
</script>
