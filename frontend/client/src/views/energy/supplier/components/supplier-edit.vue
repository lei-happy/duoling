<template>
  <el-dialog
    :title="isEdit ? '编辑供应商' : '新增供应商'"
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
          <el-form-item prop="supplierName">
            <floating-label
              label="请输入供应商名称"
              type="input"
              v-model.trim="form.supplierName"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="supplierType">
            <floating-label
              v-model="form.supplierType"
              label="请选择供应商类型"
              type="select"
              :clearable="false"
            >
              <el-option
                v-for="o in SUPPLIER_TYPES"
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
              label="请输入编码，留空则自动生成"
              type="input"
              v-model.trim="form.supplierCode"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入联系人"
              type="input"
              v-model.trim="form.contactName"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入联系电话"
              type="input"
              v-model.trim="form.contactPhone"
              clearable
            />
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
  import { addSupplier, updateSupplier } from '@/api/energy';
  import { SUPPLIER_TYPES } from '../../_shared/options';

  const props = defineProps<{
    visible: boolean;
    data: Record<string, any> | null;
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
    supplierName: [
      { required: true, message: '请输入供应商名称', trigger: 'blur' }
    ],
    supplierType: [
      { required: true, message: '请选择供应商类型', trigger: 'change' }
    ]
  });

  const resetForm = () => {
    Object.assign(form, {
      id: undefined,
      supplierName: '',
      supplierType: 9,
      supplierCode: '',
      contactName: '',
      contactPhone: '',
      remark: ''
    });
  };

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      if (props.data?.id) {
        Object.assign(form, {
          id: props.data.id,
          supplierName: props.data.supplierName || '',
          supplierType: props.data.supplierType ?? 9,
          supplierCode: props.data.supplierCode || '',
          contactName: props.data.contactName || '',
          contactPhone: props.data.contactPhone || '',
          remark: props.data.remark || ''
        });
      } else {
        resetForm();
      }
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        const payload = {
          supplierName: form.supplierName,
          supplierType: form.supplierType,
          supplierCode: form.supplierCode || undefined,
          contactName: form.contactName || undefined,
          contactPhone: form.contactPhone || undefined,
          remark: form.remark || undefined
        };
        if (isEdit.value) await updateSupplier(form.id, payload);
        else await addSupplier(payload);
        EleMessage.success({
          message: isEdit.value ? '已保存供应商' : '已新增供应商',
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
