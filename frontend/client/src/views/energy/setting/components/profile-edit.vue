<template>
  <el-dialog
    title="车辆能源档案"
    :model-value="visible"
    width="560px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <p class="form-tip">油箱、电池和标准百公里会用来判断异常加注，尽量按实车填写。</p>
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
          <el-form-item prop="vehicleId">
            <floating-label
              v-model="form.vehicleId"
              label="请选择车辆"
              type="select"
              filterable
              :clearable="false"
              :disabled="isEdit"
            >
              <el-option
                v-for="v in vehicles"
                :key="v.id"
                :label="v.plateNumber"
                :value="v.id"
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
          <el-form-item>
            <floating-label
              v-model="form.defaultProductId"
              label="请选择默认商品"
              type="select"
              filterable
              clearable
            >
              <el-option
                v-for="p in products"
                :key="p.id"
                :label="p.productName"
                :value="p.id"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.tankCapacity"
              label="请输入油箱/气瓶容量"
              type="input-number"
              :input-number-min="0"
              :input-number-precision="1"
              input-number-controls-position="right"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.batteryCapacity"
              label="请输入电池容量"
              type="input-number"
              :input-number-min="0"
              :input-number-precision="1"
              input-number-controls-position="right"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.standardConsumptionPer100km"
              label="请输入标准百公里"
              type="input-number"
              :input-number-min="0"
              :input-number-precision="2"
              input-number-controls-position="right"
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
  import { upsertProfile } from '@/api/energy';
  import { ENERGY_TYPES } from '../../_shared/options';

  const props = defineProps<{
    visible: boolean;
    data: Record<string, any> | null;
    vehicles: Array<Record<string, any>>;
    products: Array<Record<string, any>>;
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
    vehicleId: [{ required: true, message: '请选择车辆', trigger: 'change' }],
    energyType: [
      { required: true, message: '请选择能源类型', trigger: 'change' }
    ]
  });

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        id: props.data?.id,
        vehicleId: props.data?.vehicleId,
        energyType: props.data?.energyType || 'OIL',
        defaultProductId: props.data?.defaultProductId,
        tankCapacity: props.data?.tankCapacity,
        batteryCapacity: props.data?.batteryCapacity,
        standardConsumptionPer100km: props.data?.standardConsumptionPer100km
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
        await upsertProfile(form);
        EleMessage.success({ message: '已保存车辆档案', plain: true });
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
  .form-tip {
    margin: 0 0 16px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
    line-height: 1.7;
  }

  .energy-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
</style>
