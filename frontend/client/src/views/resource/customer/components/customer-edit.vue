<template>
  <el-dialog
    :title="isEdit ? '编辑客户' : '新增客户'"
    :model-value="visible"
    @update:model-value="updateVisible"
    width="700px"
    draggable
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
          <el-form-item label="客户名称" prop="customerName">
            <el-input
              v-model="form.customerName"
              placeholder="请输入客户名称"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="简称">
            <el-input v-model="form.shortName" placeholder="请输入简称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="客户类型" prop="customerType">
            <el-select
              v-model="form.customerType"
              placeholder="请选择客户类型"
              style="width: 100%"
            >
              <el-option label="托运方" :value="0" />
              <el-option label="收货方" :value="1" />
              <el-option label="两者兼具" :value="2" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系人" prop="contactPerson">
            <el-input
              v-model="form.contactPerson"
              placeholder="请输入联系人"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系电话" prop="contactPhone">
            <el-input
              v-model="form.contactPhone"
              placeholder="请输入联系电话"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="地址">
            <el-input v-model="form.address" placeholder="请输入地址" />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="备注">
            <el-input
              v-model="form.remark"
              type="textarea"
              :rows="3"
              placeholder="请输入备注"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch, computed } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { addCustomer, updateCustomer } from '@/api/resource/customer';
  import type { Customer } from '@/api/resource/customer/model';

  const props = defineProps<{
    visible: boolean;
    data: Customer | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Customer>({});

  const rules = reactive<FormRules>({
    customerName: [
      { required: true, message: '请输入客户名称', trigger: 'blur' }
    ],
    customerType: [
      { required: true, message: '请选择客户类型', trigger: 'change' }
    ],
    contactPerson: [
      { required: true, message: '请输入联系人', trigger: 'blur' }
    ],
    contactPhone: [
      { required: true, message: '请输入联系电话', trigger: 'blur' }
    ]
  });

  watch(
    () => props.visible,
    (val) => {
      if (val) {
        if (props.data) {
          Object.assign(form, props.data);
        } else {
          Object.keys(form).forEach((k) => {
            (form as any)[k] = undefined;
          });
        }
      }
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        if (isEdit.value) {
          await updateCustomer(form);
        } else {
          await addCustomer(form);
        }
        EleMessage.success({ message: '操作成功', plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        EleMessage.error({ message: e.message, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>
