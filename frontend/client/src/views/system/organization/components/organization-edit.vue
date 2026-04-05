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
      label-width="0"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :sm="12" :xs="24">
          <el-form-item prop="parentId">
            <organization-select
              v-model="form.parentId"
              placeholder="请选择上级机构"
            />
          </el-form-item>
          <el-form-item prop="organizationName">
            <floating-label
              label="请输入机构名称"
              type="input"
              v-model.trim="form.organizationName"
              :maxlength="20"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <floating-label
              label="请输入机构代码"
              type="input"
              v-model.trim="form.organizationCode"
              :maxlength="20"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :sm="12" :xs="24">
          <el-form-item prop="organizationType">
            <floating-label
              v-model="form.organizationType"
              label="请选择机构类型"
              type="select"
              clearable
            >
              <el-option
                v-for="item in organizationTypeDict"
                :key="item.dictDataCode"
                :label="item.dictDataName"
                :value="item.dictDataCode"
              />
            </floating-label>
          </el-form-item>
          <el-form-item prop="sortNumber">
            <floating-label
              label="请输入排序号"
              type="input"
              input-type="number"
              v-model="sortNumberStr"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <floating-label
              label="请输入备注"
              type="input"
              input-type="textarea"
              v-model.trim="form.comments"
              :maxlength="200"
              :show-word-limit="true"
              clearable
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
  import { ref, reactive, computed } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { useDictData } from '@/utils/use-dict-data';
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

  const [organizationTypeDict] = useDictData(['organization_type']);

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

  /** 排序号（与数字校验规则配合的字符串桥接） */
  const sortNumberStr = computed({
    get() {
      const v = form.sortNumber;
      return v === undefined || v === null ? '' : String(v);
    },
    set(s: string) {
      if (s === '' || s == null) {
        form.sortNumber = void 0;
        return;
      }
      const n = Number(s);
      if (Number.isNaN(n)) {
        form.sortNumber = void 0;
        return;
      }
      form.sortNumber = Math.min(99999, Math.max(0, n));
    }
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
