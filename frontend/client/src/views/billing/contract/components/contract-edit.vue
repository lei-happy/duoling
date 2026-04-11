<template>
  <el-dialog
    :title="isEdit ? '编辑合同' : '新增合同'"
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
          <el-form-item label="合同编号" prop="contractNo">
            <el-input
              v-model="form.contractNo"
              placeholder="请输入合同编号"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="合同名称" prop="contractName">
            <el-input
              v-model="form.contractName"
              placeholder="请输入合同名称"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="客户" prop="customerId">
            <el-select
              v-model="form.customerId"
              placeholder="请选择客户"
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="item in customerOptions"
                :key="item.id"
                :label="item.customerName"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12" />
        <el-col :span="12">
          <el-form-item label="生效日期" prop="effectiveDate">
            <el-date-picker
              v-model="form.effectiveDate"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="请选择生效日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="失效日期" prop="expiryDate">
            <el-date-picker
              v-model="form.expiryDate"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="请选择失效日期"
              style="width: 100%"
            />
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
  import { addContract, updateContract } from '@/api/billing/contract';
  import { selectCustomers } from '@/api/partner/customer';
  import type { FreightContract } from '@/api/billing/contract/model';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';

  const props = defineProps<{
    visible: boolean;
    data: FreightContract | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<FreightContract>({});
  const customerOptions = ref<CustomerSelectItem[]>([]);

  const rules = reactive<FormRules>({
    contractNo: [
      { required: true, message: '请输入合同编号', trigger: 'blur' }
    ],
    contractName: [
      { required: true, message: '请输入合同名称', trigger: 'blur' }
    ],
    customerId: [
      { required: true, message: '请选择客户', trigger: 'change' }
    ]
  });

  const loadCustomers = async () => {
    try {
      customerOptions.value = (await selectCustomers()) ?? [];
    } catch (_) {
      customerOptions.value = [];
    }
  };

  watch(
    () => props.visible,
    (val) => {
      if (val) {
        loadCustomers();
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
        const selected = customerOptions.value.find(
          (c) => c.id === form.customerId
        );
        if (selected) {
          form.customerName = selected.customerName;
        }
        if (isEdit.value) {
          await updateContract(form);
        } else {
          await addContract(form);
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
