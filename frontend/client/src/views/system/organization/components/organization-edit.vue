<!-- 机构编辑弹窗 -->
<template>
  <ele-modal
    form
    :width="620"
    :title="isUpdate ? '修改机构' : '添加机构'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :sm="12" :xs="24">
          <el-form-item label="上级机构" prop="parentId">
            <organization-select
              v-model="form.parentId"
              placeholder="请选择上级机构"
            />
          </el-form-item>
          <el-form-item label="机构名称" prop="organizationName">
            <el-input
              clearable
              :maxlength="20"
              v-model="form.organizationName"
              placeholder="请输入机构名称"
            />
          </el-form-item>
          <el-form-item label="机构代码">
            <el-input
              clearable
              :maxlength="20"
              v-model="form.organizationCode"
              placeholder="请输入机构代码"
            />
          </el-form-item>
        </el-col>
        <el-col :sm="12" :xs="24">
          <el-form-item label="机构类型" prop="organizationType">
            <dict-data
              code="organization_type"
              v-model="form.organizationType"
              placeholder="请选择机构类型"
            />
          </el-form-item>
          <el-form-item label="排序号" prop="sortNumber">
            <el-input-number
              :min="0"
              :max="99999"
              v-model="form.sortNumber"
              placeholder="请输入排序号"
              controls-position="right"
              class="ele-fluid"
            />
          </el-form-item>
          <el-form-item label="备注">
            <el-input
              :rows="3"
              type="textarea"
              :maxlength="200"
              v-model="form.comments"
              placeholder="请输入备注"
            />
          </el-form-item>
        </el-col>
      </el-row>
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
  import OrganizationSelect from './organization-select.vue';
  import {
    addOrganization,
    updateOrganization
  } from '@/api/system/organization';
  import type { Organization } from '@/api/system/organization/model';

  const props = defineProps<{
    /** 修改回显的数据 */
    data?: Organization | null;
    /** 添加时机构id */
    organizationId?: number;
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
  const [form, _resetFields, assignFields] = useFormData<Organization>({
    organizationId: void 0,
    parentId: props.organizationId,
    organizationName: '',
    organizationCode: '',
    organizationType: void 0,
    sortNumber: void 0,
    comments: ''
  });

  /** 表单验证规则 */
  const rules = reactive<FormRules>({
    organizationName: [
      {
        required: true,
        message: '请输入机构名称',
        type: 'string',
        trigger: 'blur'
      }
    ],
    organizationType: [
      {
        required: true,
        message: '请选择机构类型',
        type: 'string',
        trigger: 'change'
      }
    ],
    sortNumber: [
      {
        required: true,
        message: '请输入排序号',
        type: 'number',
        trigger: 'blur'
      }
    ]
  });

  /** 关闭弹窗 */
  const handleCancel = () => {
    closeModal();
  };

  /** 保存编辑 */
  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      loading.value = true;
      const saveOrUpdate = isUpdate.value
        ? updateOrganization
        : addOrganization;
      saveOrUpdate({ ...form, parentId: form.parentId || 0 })
        .then((msg) => {
          loading.value = false;
          EleMessage.success({ message: msg, plain: true });
          handleCancel();
          emit('done');
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
      parentId: props.data.parentId || void 0
    });
    isUpdate.value = true;
  }
</script>
