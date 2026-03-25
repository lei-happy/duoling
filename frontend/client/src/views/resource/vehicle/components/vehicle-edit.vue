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
      label-width="100px"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="车牌号" prop="plateNumber">
            <el-input v-model="form.plateNumber" placeholder="请输入车牌号" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="车辆类型" prop="vehicleType">
            <el-input
              v-model="form.vehicleType"
              placeholder="请输入车辆类型"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="品牌">
            <el-input v-model="form.brand" placeholder="请输入品牌" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="型号">
            <el-input v-model="form.model" placeholder="请输入型号" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="颜色">
            <el-input v-model="form.color" placeholder="请输入颜色" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="载重(吨)">
            <el-input-number
              v-model="form.loadCapacity"
              :min="0"
              :precision="2"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="容积(m³)">
            <el-input-number
              v-model="form.volumeCapacity"
              :min="0"
              :precision="2"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="车架号">
            <el-input v-model="form.vin" placeholder="请输入VIN" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="发动机号">
            <el-input v-model="form.engineNo" placeholder="请输入发动机号" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="购买日期">
            <el-date-picker
              v-model="form.purchaseDate"
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
              v-model="form.insuranceExpire"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="年检到期">
            <el-date-picker
              v-model="form.inspectionExpire"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择日期"
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
  import { addVehicle, updateVehicle } from '@/api/resource/vehicle';
  import type { Vehicle } from '@/api/resource/vehicle/model';

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

  const rules = reactive<FormRules>({
    plateNumber: [
      { required: true, message: '请输入车牌号', trigger: 'blur' }
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
