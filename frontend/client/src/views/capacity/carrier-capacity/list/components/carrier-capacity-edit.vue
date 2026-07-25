<template>
  <el-dialog
    :model-value="visible"
    :title="form.id ? '编辑承运商运力' : '新增承运商运力'"
    width="720px"
    :close-on-click-modal="false"
    @update:model-value="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
      <el-divider content-position="left">归属承运商</el-divider>
      <el-form-item label="承运商" prop="carrierId">
        <el-select
          v-model="form.carrierId"
          filterable
          remote
          reserve-keyword
          placeholder="搜索并选择承运商"
          :remote-method="searchCarriers"
          :loading="carrierLoading"
          style="width: 100%"
        >
          <el-option
            v-for="c in carrierOptions"
            :key="c.id"
            :label="c.carrierName"
            :value="c.id"
          />
        </el-select>
      </el-form-item>

      <el-divider content-position="left">驾驶员信息</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="姓名" prop="driver.name">
            <el-input v-model="form.driver.name" placeholder="请输入" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="手机号" prop="driver.phone">
            <el-input v-model="form.driver.phone" placeholder="请输入" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="身份证号">
            <el-input v-model="form.driver.idCard" placeholder="请输入" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="驾驶证号">
            <el-input v-model="form.driver.licenseNo" placeholder="请输入" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="驾驶证有效期">
            <el-date-picker
              v-model="form.driver.licenseExpire"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="资格证号">
            <el-input
              v-model="form.driver.qualificationNo"
              placeholder="请输入"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="资格证有效期">
            <el-date-picker
              v-model="form.driver.qualificationExpire"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">车辆信息</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="车牌号" prop="vehicle.plateNumber">
            <el-input v-model="form.vehicle.plateNumber" placeholder="请输入" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="车辆类型">
            <el-input v-model="form.vehicle.vehicleType" placeholder="请输入" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="年检到期">
            <el-date-picker
              v-model="form.vehicle.inspectionExpire"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="保险到期">
            <el-date-picker
              v-model="form.vehicle.insuranceExpire"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="道路运输证号">
            <el-input
              v-model="form.vehicle.transportLicenseNo"
              placeholder="请输入"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="道路运输证有效期">
            <el-date-picker
              v-model="form.vehicle.transportLicenseExpire"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose(false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="onSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { selectCarriers } from '@/api/partner/carrier';
  import {
    addCarrierCapacity,
    updateCarrierCapacity,
    getCarrierCapacity
  } from '@/api/capacity/carrier-capacity';
  import type { CarrierCapacitySaveParam } from '@/api/capacity/carrier-capacity/model';

  const props = defineProps<{ visible: boolean; editId?: number | null }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance>();
  const saving = ref(false);
  const carrierLoading = ref(false);
  const carrierOptions = ref<{ id: number; carrierName: string }[]>([]);

  const createEmpty = (): CarrierCapacitySaveParam & { id?: number } => ({
    carrierId: undefined as unknown as number,
    remark: '',
    vehicle: { plateNumber: '' },
    driver: { name: '', phone: '' }
  });

  const form = reactive<CarrierCapacitySaveParam & { id?: number }>(
    createEmpty()
  );

  const rules: FormRules = {
    carrierId: [{ required: true, message: '请选择承运商', trigger: 'change' }],
    'driver.name': [{ required: true, message: '请输入姓名', trigger: 'blur' }],
    'driver.phone': [
      { required: true, message: '请输入手机号', trigger: 'blur' }
    ],
    'vehicle.plateNumber': [
      { required: true, message: '请输入车牌号', trigger: 'blur' }
    ]
  };

  const searchCarriers = async (keyword: string) => {
    carrierLoading.value = true;
    try {
      const list = await selectCarriers(keyword);
      carrierOptions.value = (list ?? []).map((c: any) => ({
        id: c.id,
        carrierName: c.carrierName ?? c.carrier_name ?? `承运商#${c.id}`
      }));
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      carrierLoading.value = false;
    }
  };

  const resetForm = () => {
    Object.assign(form, createEmpty());
  };

  const loadDetail = async (id: number) => {
    const d = await getCarrierCapacity(id);
    if (!d) return;
    form.id = d.id;
    form.carrierId = d.carrierId;
    form.remark = d.remark ?? '';
    form.vehicle = {
      plateNumber: d.vehicle?.plateNumber ?? d.plateNumber,
      vehicleType: d.vehicle?.vehicleType,
      inspectionExpire: d.vehicle?.inspectionExpire,
      insuranceExpire: d.vehicle?.insuranceExpire,
      transportLicenseNo: d.vehicle?.transportLicenseNo,
      transportLicenseExpire: d.vehicle?.transportLicenseExpire
    };
    form.driver = {
      name: d.driver?.name ?? d.driverName,
      phone: d.driver?.phone ?? d.driverPhone,
      idCard: d.driver?.idCard,
      licenseNo: d.driver?.licenseNo,
      licenseExpire: d.driver?.licenseExpire,
      qualificationNo: d.driver?.qualificationNo,
      qualificationExpire: d.driver?.qualificationExpire
    };
    if (d.carrierId) {
      carrierOptions.value = [
        {
          id: d.carrierId,
          carrierName: d.carrierName ?? `承运商#${d.carrierId}`
        }
      ];
    }
  };

  watch(
    () => props.visible,
    (v) => {
      if (v) {
        resetForm();
        if (props.editId) {
          loadDetail(props.editId);
        } else {
          searchCarriers('');
        }
      }
    }
  );

  const handleClose = (v: boolean) => {
    if (!v) emit('update:visible', false);
  };

  const onSubmit = async () => {
    if (!formRef.value) return;
    await formRef.value.validate(async (valid) => {
      if (!valid) return;
      saving.value = true;
      try {
        const payload: CarrierCapacitySaveParam = {
          carrierId: form.carrierId,
          remark: form.remark,
          vehicle: { ...form.vehicle },
          driver: { ...form.driver }
        };
        if (form.id) {
          await updateCarrierCapacity(form.id, payload);
        } else {
          await addCarrierCapacity(payload);
        }
        EleMessage.success({ message: '保存成功', plain: true });
        emit('update:visible', false);
        emit('done');
      } catch (e: any) {
        EleMessage.error({ message: e.message, plain: true });
      } finally {
        saving.value = false;
      }
    });
  };
</script>
