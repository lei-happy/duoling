<template>
  <el-dialog
    :title="isEdit ? '编辑订单' : '新增订单'"
    :model-value="visible"
    @update:model-value="updateVisible"
    width="800px"
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
          <el-form-item label="客户名称" prop="customerName">
            <el-input
              v-model="form.customerName"
              placeholder="请输入客户名称"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="货物名称" prop="cargoName">
            <el-input v-model="form.cargoName" placeholder="请输入货物名称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="出发地" prop="origin">
            <el-input v-model="form.origin" placeholder="请输入出发地" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="目的地" prop="destination">
            <el-input v-model="form.destination" placeholder="请输入目的地" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="车牌号">
            <el-input v-model="form.plateNumber" placeholder="请输入车牌号" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="司机姓名">
            <el-input v-model="form.driverName" placeholder="请输入司机姓名" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="货物重量">
            <el-input-number
              v-model="form.cargoWeight"
              :min="0"
              :precision="2"
              placeholder="吨"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="货物体积">
            <el-input-number
              v-model="form.cargoVolume"
              :min="0"
              :precision="2"
              placeholder="立方米"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="运费金额">
            <el-input-number
              v-model="form.freightAmount"
              :min="0"
              :precision="2"
              placeholder="元"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="计划发车">
            <el-date-picker
              v-model="form.planDepartTime"
              type="datetime"
              placeholder="请选择计划发车时间"
              value-format="YYYY-MM-DD HH:mm:ss"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="计划到达">
            <el-date-picker
              v-model="form.planArriveTime"
              type="datetime"
              placeholder="请选择计划到达时间"
              value-format="YYYY-MM-DD HH:mm:ss"
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
  import { addOrder, updateOrder } from '@/api/business/order';
  import type { Order } from '@/api/business/order/model';

  const props = defineProps<{
    visible: boolean;
    data: Order | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Order>({});

  const rules = reactive<FormRules>({
    customerName: [
      { required: true, message: '请输入客户名称', trigger: 'blur' }
    ],
    cargoName: [{ required: true, message: '请输入货物名称', trigger: 'blur' }],
    origin: [{ required: true, message: '请输入出发地', trigger: 'blur' }],
    destination: [{ required: true, message: '请输入目的地', trigger: 'blur' }]
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
          await updateOrder(form);
        } else {
          await addOrder(form);
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
