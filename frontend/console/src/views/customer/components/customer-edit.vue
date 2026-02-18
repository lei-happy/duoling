<!-- 客户编辑弹窗 -->
<template>
  <ele-modal
    form
    :width="640"
    :title="isUpdate ? '编辑企业' : '注册企业'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="企业名称" prop="tenantName">
            <el-input
              clearable
              :maxlength="100"
              v-model="form.tenantName"
              placeholder="请输入企业名称"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="企业简称" prop="shortName">
            <el-input
              clearable
              :maxlength="50"
              v-model="form.shortName"
              placeholder="请输入企业简称"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系人" prop="contactPerson">
            <el-input
              clearable
              :maxlength="50"
              v-model="form.contactPerson"
              placeholder="请输入联系人"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系电话" prop="contactPhone">
            <el-input
              clearable
              :maxlength="20"
              v-model="form.contactPhone"
              placeholder="请输入联系电话"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系邮箱" prop="contactEmail">
            <el-input
              clearable
              :maxlength="100"
              v-model="form.contactEmail"
              placeholder="请输入联系邮箱"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="营业执照号" prop="licenseNo">
            <el-input
              clearable
              :maxlength="100"
              v-model="form.licenseNo"
              placeholder="请输入营业执照号"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="省份">
            <el-input
              clearable
              :maxlength="50"
              v-model="form.province"
              placeholder="请输入省份"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="城市">
            <el-input
              clearable
              :maxlength="50"
              v-model="form.city"
              placeholder="请输入城市"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="详细地址">
            <el-input
              clearable
              :maxlength="255"
              v-model="form.address"
              placeholder="请输入详细地址"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="备注">
            <el-input
              :rows="3"
              type="textarea"
              v-model="form.remark"
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
          { preset: 'save', onClick: () => handleSave() }
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
  import { addCustomer, updateCustomer } from '@/api/customer';
  import type { Customer } from '@/api/customer/model';

  const props = defineProps<{
    data?: Customer | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(false);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);

  const [form, _resetFields, assignFields] = useFormData<Customer>({
    id: void 0,
    tenantName: '',
    shortName: '',
    contactPerson: '',
    contactPhone: '',
    contactEmail: '',
    province: '',
    city: '',
    address: '',
    licenseNo: '',
    remark: '',
    sourceChannel: ''
  });

  const rules = reactive<FormRules>({
    tenantName: [
      {
        required: true,
        message: '请输入企业名称',
        type: 'string',
        trigger: 'blur'
      }
    ]
  });

  const handleCancel = () => {
    closeModal();
  };

  const handleSave = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      loading.value = true;
      const saveOrUpdate = isUpdate.value ? updateCustomer : addCustomer;
      saveOrUpdate(form)
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
    assignFields(props.data);
    isUpdate.value = !!props.data.id;
  }
</script>
