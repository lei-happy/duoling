<!-- 经营主体编辑弹窗 -->
<template>
  <ele-modal
    form
    :width="680"
    :title="isUpdate ? '修改经营主体' : '添加经营主体'"
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
          <el-form-item prop="entityName">
            <floating-label
              label="请输入主体名称（法人全称）"
              type="input"
              v-model.trim="form.entityName"
              :maxlength="100"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <floating-label
              label="主体编码（留空自动生成）"
              type="input"
              v-model.trim="form.entityCode"
              :maxlength="50"
              :disabled="isUpdate"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <floating-label
              label="请输入简称"
              type="input"
              v-model.trim="form.shortName"
              :maxlength="50"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <floating-label
              label="统一社会信用代码"
              type="input"
              v-model.trim="form.unifiedCreditCode"
              :maxlength="30"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <floating-label
              label="法定代表人"
              type="input"
              v-model.trim="form.legalPerson"
              :maxlength="50"
              clearable
            />
          </el-form-item>
          <el-form-item prop="sortOrder">
            <floating-label
              label="请输入排序号"
              type="input"
              input-type="number"
              v-model="sortOrderStr"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :sm="12" :xs="24">
          <el-form-item>
            <floating-label
              label="联系人"
              type="input"
              v-model.trim="form.contactPerson"
              :maxlength="50"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <floating-label
              label="联系电话"
              type="input"
              v-model.trim="form.contactPhone"
              :maxlength="20"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <floating-label
              label="对公开户行"
              type="input"
              v-model.trim="form.bankName"
              :maxlength="100"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <floating-label
              label="对公账号"
              type="input"
              v-model.trim="form.bankAccount"
              :maxlength="50"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <floating-label
              label="注册地址"
              type="input"
              v-model.trim="form.registeredAddress"
              :maxlength="255"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <floating-label
              label="请输入备注"
              type="input"
              input-type="textarea"
              v-model.trim="form.remark"
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
  import {
    addBusinessEntity,
    updateBusinessEntity
  } from '@/api/system/business-entity';
  import type { BusinessEntity } from '@/api/system/business-entity/model';

  const props = defineProps<{
    data?: BusinessEntity | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(false);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);

  const [form, _resetFields, assignFields] = useFormData<BusinessEntity>({
    id: void 0,
    entityCode: '',
    entityName: '',
    shortName: '',
    unifiedCreditCode: '',
    legalPerson: '',
    registeredAddress: '',
    contactPerson: '',
    contactPhone: '',
    bankName: '',
    bankAccount: '',
    sortOrder: 0,
    remark: ''
  });

  const sortOrderStr = computed({
    get() {
      const v = form.sortOrder;
      return v === undefined || v === null ? '' : String(v);
    },
    set(s: string) {
      if (s === '' || s == null) {
        form.sortOrder = 0;
        return;
      }
      const n = Number(s);
      form.sortOrder = Number.isNaN(n) ? 0 : Math.min(9999, Math.max(0, n));
    }
  });

  const rules = reactive<FormRules>({
    entityName: [
      {
        required: true,
        message: '请输入主体名称',
        type: 'string',
        trigger: 'blur'
      }
    ]
  });

  const handleCancel = () => {
    closeModal();
  };

  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      loading.value = true;
      const done = () => {
        loading.value = false;
        EleMessage.success({ message: '保存成功', plain: true });
        handleCancel();
        emit('done');
      };
      const fail = (e: any) => {
        loading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      };
      if (isUpdate.value && form.id) {
        updateBusinessEntity(form.id, { ...form })
          .then(done)
          .catch(fail);
      } else {
        addBusinessEntity({ ...form })
          .then(done)
          .catch(fail);
      }
    });
  };

  if (props.data) {
    assignFields({ ...props.data });
    isUpdate.value = true;
  }
</script>
