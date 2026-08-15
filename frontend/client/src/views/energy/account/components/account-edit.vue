<template>
  <el-dialog
    :title="isEdit ? '编辑账户' : '新增账户'"
    :model-value="visible"
    width="720px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="energy-edit-form"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item prop="accountName">
            <floating-label
              label="请输入账户名称"
              type="input"
              v-model.trim="form.accountName"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="supplierId">
            <floating-label
              v-model="form.supplierId"
              label="请选择供应商"
              type="select"
              filterable
              :clearable="false"
              :disabled="isEdit"
            >
              <el-option
                v-for="s in suppliers"
                :key="s.id"
                :label="s.supplierName"
                :value="s.id"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="energyType">
            <floating-label
              v-model="form.energyType"
              label="请选择能源类型"
              type="select"
              :clearable="false"
            >
              <el-option
                v-for="o in ENERGY_TYPES"
                :key="o.value"
                :label="o.label"
                :value="o.value"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="accountType">
            <floating-label
              v-model="form.accountType"
              label="请选择账户类型"
              type="select"
              :clearable="false"
            >
              <el-option
                v-for="o in ACCOUNT_TYPES"
                :key="o.value"
                :label="o.label"
                :value="o.value"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入供应商侧账号，可空"
              type="input"
              v-model.trim="form.externalAccountNo"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col v-if="isEdit" :span="12">
          <el-form-item>
            <floating-label
              v-model="form.status"
              label="请选择账户状态"
              type="select"
              :clearable="false"
            >
              <el-option
                v-for="o in ACCOUNT_STATUSES"
                :key="o.value"
                :label="o.label"
                :value="o.value"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <floating-label
              label="请输入备注"
              type="input"
              input-type="textarea"
              v-model="form.remark"
              :clearable="false"
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
  import { computed, nextTick, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { addAccount, updateAccount } from '@/api/energy';
  import {
    ACCOUNT_STATUSES,
    ACCOUNT_TYPES,
    ENERGY_TYPES
  } from '../../_shared/options';

  const props = defineProps<{
    visible: boolean;
    data: Record<string, any> | null;
    suppliers: Array<{ id: number; supplierName: string }>;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Record<string, any>>({});

  const rules = reactive<FormRules>({
    accountName: [
      { required: true, message: '请输入账户名称', trigger: 'blur' }
    ],
    supplierId: [
      { required: true, message: '请选择供应商', trigger: 'change' }
    ],
    energyType: [
      { required: true, message: '请选择能源类型', trigger: 'change' }
    ],
    accountType: [
      { required: true, message: '请选择账户类型', trigger: 'change' }
    ]
  });

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        id: props.data?.id,
        accountName: props.data?.accountName || '',
        supplierId: props.data?.supplierId,
        energyType: props.data?.energyType || 'OIL',
        accountType: props.data?.accountType || 'PREPAID',
        externalAccountNo: props.data?.externalAccountNo || '',
        status: props.data?.status ?? 1,
        remark: props.data?.remark || ''
      });
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        if (isEdit.value) await updateAccount(form.id, form);
        else await addAccount(form);
        EleMessage.success({
          message: isEdit.value ? '已保存账户' : '已新增账户',
          plain: true
        });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        if (e?.message) EleMessage.error({ message: e.message, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .energy-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
</style>
