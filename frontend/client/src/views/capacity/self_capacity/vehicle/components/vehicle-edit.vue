<template>
  <el-dialog
    :title="isEdit ? '编辑车辆' : '新增车辆'"
    :model-value="visible"
    @update:model-value="updateVisible"
    width="700px"
    draggable
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      @submit.prevent=""
    >
      <el-divider content-position="left">基础信息</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item prop="plateNumber">
            <floating-label
              label="请输入车牌号"
              type="input"
              v-model.trim="form.plateNumber"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.trailerId"
              label="请选择需要关联的挂车"
              type="select"
              :filterable="true"
              clearable
            >
              <el-option
                v-for="item in trailerOptions"
                :key="item.id"
                :label="item.plateNumber"
                :value="item.id"
              />
            </floating-label>
          </el-form-item>
        </el-col>
      </el-row>
      <el-divider content-position="left">详细信息</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.vehicleType"
              label="请选择车辆类型"
              type="select"
              :filterable="true"
              clearable
            >
              <el-option
                v-for="item in vehicleTypeDict"
                :key="item.dictDataCode"
                :label="item.dictDataName"
                :value="item.dictDataCode"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入品牌"
              type="input"
              v-model.trim="form.brand"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入型号"
              type="input"
              v-model.trim="form.model"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入颜色"
              type="input"
              v-model.trim="form.color"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入载重(吨)"
              type="input"
              input-type="number"
              v-model="loadCapacityStr"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入容积(m³)"
              type="input"
              input-type="number"
              v-model="volumeCapacityStr"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入车架号"
              type="input"
              v-model.trim="form.vin"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入发动机号"
              type="input"
              v-model.trim="form.engineNo"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请选择购买日期"
              type="date"
              date-type="date"
              v-model="form.purchaseDate"
              value-format="YYYY-MM-DD"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请选择保险到期日"
              type="date"
              date-type="date"
              v-model="form.insuranceExpire"
              value-format="YYYY-MM-DD"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请选择年检到期日"
              type="date"
              date-type="date"
              v-model="form.inspectionExpire"
              value-format="YYYY-MM-DD"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入GPS设备ID"
              type="input"
              v-model.trim="form.gpsDeviceId"
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
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch, computed } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import {
    addVehicle,
    updateVehicle,
    listAvailableTrailers
  } from '@/api/capacity/self_capacity/vehicle';
  import type { Vehicle, TrailerOption } from '@/api/capacity/self_capacity/vehicle/model';
  import { useDictData } from '@/utils/use-dict-data';
  import { DICT_CODE_VEHICLE_TYPE } from '@/constants/dict-codes';

  const props = defineProps<{
    visible: boolean;
    data: Vehicle | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Vehicle>({});
  const trailerOptions = ref<TrailerOption[]>([]);

  /** 车辆类型选项（数据字典 vehicle_type） */
  const [vehicleTypeDict] = useDictData([DICT_CODE_VEHICLE_TYPE]);

  const numToStr = (n: number | undefined | null) =>
    n != null && !Number.isNaN(Number(n)) ? String(n) : '';

  const loadCapacityStr = computed({
    get: () => numToStr(form.loadCapacity),
    set: (v: string) => {
      const t = v?.trim();
      if (t === '' || t == null) {
        form.loadCapacity = void 0;
        return;
      }
      const n = Number(t);
      form.loadCapacity = Number.isFinite(n) ? Math.round(n * 100) / 100 : void 0;
    }
  });

  const volumeCapacityStr = computed({
    get: () => numToStr(form.volumeCapacity),
    set: (v: string) => {
      const t = v?.trim();
      if (t === '' || t == null) {
        form.volumeCapacity = void 0;
        return;
      }
      const n = Number(t);
      form.volumeCapacity = Number.isFinite(n) ? Math.round(n * 100) / 100 : void 0;
    }
  });

  const rules = reactive<FormRules>({
    plateNumber: [
      { required: true, message: '请输入车牌号', trigger: 'blur' }
    ]
  });

  const loadTrailerOptions = async () => {
    try {
      const excludeId = isEdit.value ? props.data?.id : undefined;
      const list = await listAvailableTrailers(excludeId);
      trailerOptions.value = list ?? [];
    } catch {
      trailerOptions.value = [];
    }
  };

  watch(
    () => props.visible,
    (val) => {
      if (val) {
        loadTrailerOptions();
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
          await updateVehicle(form);
        } else {
          await addVehicle(form);
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
