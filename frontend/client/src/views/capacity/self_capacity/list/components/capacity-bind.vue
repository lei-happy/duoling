<template>
  <el-dialog
    title="上车（绑定司机与车辆）"
    :model-value="visible"
    @update:model-value="updateVisible"
    width="500px"
    draggable
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :span="24">
          <el-form-item prop="driverId">
            <floating-label
              v-model="form.driverId"
              label="请选择司机"
              type="select"
              :filterable="true"
              :remote="true"
              :remote-method="searchDrivers"
              clearable
            >
              <el-option
                v-for="item in driverOptions"
                :key="item.id"
                :label="`${item.name}（${item.phone}）`"
                :value="item.id"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item prop="vehicleId">
            <floating-label
              v-model="form.vehicleId"
              label="请选择车辆"
              type="select"
              :filterable="true"
              :remote="true"
              :remote-method="searchVehicles"
              clearable
            >
              <el-option
                v-for="item in vehicleOptions"
                :key="item.id"
                :label="item.plateNumber"
                :value="item.id"
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
              v-model.trim="form.remark"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        确认上车
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import {
    bindCapacity,
    listAvailableDrivers,
    listAvailableVehicles
  } from '@/api/capacity/self_capacity/list';
  import type { DriverOption, VehicleOption } from '@/api/capacity/self_capacity/list/model';

  const props = defineProps<{
    visible: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const driverOptions = ref<DriverOption[]>([]);
  const vehicleOptions = ref<VehicleOption[]>([]);

  const form = reactive({
    driverId: void 0 as number | undefined,
    vehicleId: void 0 as number | undefined,
    remark: ''
  });

  const rules = reactive<FormRules>({
    driverId: [
      { required: true, message: '请选择司机', trigger: 'change' }
    ],
    vehicleId: [
      { required: true, message: '请选择车辆', trigger: 'change' }
    ]
  });

  const searchDrivers = async (keyword?: string) => {
    try {
      driverOptions.value = await listAvailableDrivers(keyword || undefined);
    } catch {
      driverOptions.value = [];
    }
  };

  const searchVehicles = async (keyword?: string) => {
    try {
      vehicleOptions.value = await listAvailableVehicles(keyword || undefined);
    } catch {
      vehicleOptions.value = [];
    }
  };

  watch(
    () => props.visible,
    (val) => {
      if (val) {
        form.driverId = void 0;
        form.vehicleId = void 0;
        form.remark = '';
        formRef.value?.resetFields();
        searchDrivers();
        searchVehicles();
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
        await bindCapacity({
          driverId: form.driverId!,
          vehicleId: form.vehicleId!,
          remark: form.remark || undefined
        });
        EleMessage.success({ message: '上车成功', plain: true });
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
