<template>
  <el-dialog
    :title="isEdit ? '编辑商品' : '新增商品'"
    :model-value="visible"
    width="560px"
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
          <el-form-item prop="productCode">
            <floating-label
              label="请输入商品编码"
              type="input"
              v-model.trim="form.productCode"
              :disabled="isEdit"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="productName">
            <floating-label
              label="请输入商品名称"
              type="input"
              v-model.trim="form.productName"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="energyType">
            <floating-label
              v-model="form.energyType"
              label="请选择能源类型"
              type="select"
              :clearable="false"
              @change="onEnergyType"
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
          <el-form-item prop="standardUnit">
            <floating-label
              label="请输入标准单位"
              type="input"
              v-model.trim="form.standardUnit"
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
  import { addProduct, updateProduct } from '@/api/energy';
  import { ENERGY_TYPES } from '../../_shared/options';

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
    productCode: [
      { required: true, message: '请输入商品编码', trigger: 'blur' }
    ],
    productName: [
      { required: true, message: '请输入商品名称', trigger: 'blur' }
    ],
    energyType: [
      { required: true, message: '请选择能源类型', trigger: 'change' }
    ]
  });

  const onEnergyType = (v: string) => {
    const unit = ENERGY_TYPES.find((o) => o.value === v)?.unit;
    if (unit) form.standardUnit = unit;
  };

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        id: props.data?.id,
        productCode: props.data?.productCode || '',
        productName: props.data?.productName || '',
        energyType: props.data?.energyType || 'OIL',
        standardUnit: props.data?.standardUnit || 'L',
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
        if (isEdit.value) await updateProduct(form.id, form);
        else await addProduct(form);
        EleMessage.success({
          message: isEdit.value ? '已保存商品' : '已新增商品',
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
