<template>
  <el-dialog
    title="手工录入消费"
    :model-value="visible"
    width="760px"
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
          <el-form-item prop="consumptionTime">
            <floating-label
              v-model="form.consumptionTime"
              label="请选择消费时间"
              type="date"
              date-type="datetime"
              value-format="YYYY-MM-DD HH:mm:ss"
              :clearable="false"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="amount">
            <floating-label
              v-model="form.amount"
              label="请输入金额"
              type="input-number"
              :input-number-min="0.01"
              :input-number-precision="2"
              input-number-controls-position="right"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.quantity"
              label="请输入数量"
              type="input-number"
              :input-number-min="0"
              :input-number-precision="3"
              input-number-controls-position="right"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.unitPrice"
              label="请输入单价"
              type="input-number"
              :input-number-min="0"
              :input-number-precision="4"
              input-number-controls-position="right"
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
              v-model="form.energyProductId"
              label="请选择能源商品"
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
        <el-col :span="24">
          <el-divider content-position="left">归属</el-divider>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.accountId"
              label="请选择能源账户"
              type="select"
              filterable
              clearable
            >
              <el-option
                v-for="a in accounts"
                :key="a.id"
                :label="a.accountName"
                :value="a.id"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入卡号"
              type="input"
              v-model.trim="form.cardNo"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.vehicleId"
              label="请选择车辆"
              type="select"
              filterable
              clearable
              @change="onVehicleChange"
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
          <el-form-item>
            <floating-label
              v-model="form.driverId"
              label="请选择司机"
              type="select"
              filterable
              clearable
            >
              <el-option
                v-for="d in drivers"
                :key="d.id"
                :label="d.name"
                :value="d.id"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入站点名称"
              type="input"
              v-model.trim="form.stationName"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.mileage"
              label="请输入本次里程"
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
              v-model="form.sourceChannel"
              label="请选择来源"
              type="select"
              :clearable="false"
            >
              <el-option
                v-for="o in SOURCE_CHANNELS.filter((x) => [3, 4, 5].includes(x.value))"
                :key="o.value"
                :label="o.label"
                :value="o.value"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <div class="switch-field">
              <span>扣账户余额</span>
              <el-switch
                v-model="form.isLedgerAffecting"
                :active-value="1"
                :inactive-value="0"
                :disabled="form.sourceChannel === 4"
              />
            </div>
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
  import { nextTick, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { addConsumption } from '@/api/energy';
  import { ENERGY_TYPES, SOURCE_CHANNELS } from '../../_shared/options';

  const props = defineProps<{
    visible: boolean;
    accounts: Array<Record<string, any>>;
    products: Array<Record<string, any>>;
    vehicles: Array<Record<string, any>>;
    drivers: Array<Record<string, any>>;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Record<string, any>>({});

  const rules = reactive<FormRules>({
    consumptionTime: [
      { required: true, message: '请选择消费时间', trigger: 'change' }
    ],
    amount: [{ required: true, message: '请输入金额', trigger: 'change' }],
    energyType: [
      { required: true, message: '请选择能源类型', trigger: 'change' }
    ]
  });

  watch(
    () => form.sourceChannel,
    (v) => {
      if (v === 4) form.isLedgerAffecting = 0;
    }
  );

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        consumptionTime: '',
        amount: undefined,
        quantity: undefined,
        unitPrice: undefined,
        energyType: 'OIL',
        energyProductId: undefined,
        accountId: undefined,
        cardNo: '',
        vehicleId: undefined,
        plateNumber: '',
        driverId: undefined,
        stationName: '',
        mileage: undefined,
        sourceChannel: 3,
        isLedgerAffecting: 1,
        remark: ''
      });
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const onVehicleChange = (id?: number) => {
    const v = props.vehicles.find((x) => x.id === id);
    if (v) form.plateNumber = v.plateNumber;
  };

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      const product = props.products.find((p) => p.id === form.energyProductId);
      loading.value = true;
      try {
        await addConsumption({
          ...form,
          productName: product?.productName,
          unit: product?.standardUnit
        });
        EleMessage.success({ message: '已录入消费', plain: true });
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

  .energy-edit-form :deep(.el-divider) {
    margin: 0 0 18px;
  }

  .switch-field {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 32px;
    padding: 0 12px;
    border: 1px solid var(--el-border-color);
    border-radius: 4px;
    color: var(--el-text-color-regular);
  }
</style>
