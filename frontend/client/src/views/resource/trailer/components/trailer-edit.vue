<template>
  <el-dialog
    :title="isEdit ? '编辑挂车' : '新增挂车'"
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
      <el-divider content-position="left">基础信息</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="挂车车牌号" prop="plateNumber">
            <el-input
              v-model="form.plateNumber"
              placeholder="请输入挂车车牌号"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-divider content-position="left">详细信息</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="挂车类型">
            <el-input
              v-model="form.trailerType"
              placeholder="请输入挂车类型"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="轴数">
            <el-input-number
              v-model="form.axleCount"
              :min="1"
              :max="10"
              style="width: 100%"
            />
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
        <el-col :span="8">
          <el-form-item label="车厢长(m)">
            <el-input-number
              v-model="form.length"
              :min="0"
              :precision="2"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="车厢宽(m)">
            <el-input-number
              v-model="form.width"
              :min="0"
              :precision="2"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="车厢高(m)">
            <el-input-number
              v-model="form.height"
              :min="0"
              :precision="2"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="车位数">
            <el-input-number
              v-model="form.parkingSpots"
              :min="0"
              style="width: 100%"
            />
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
  import { addTrailer, updateTrailer } from '@/api/resource/trailer';
  import type { Trailer } from '@/api/resource/trailer/model';

  const props = defineProps<{
    visible: boolean;
    data: Trailer | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Trailer>({});

  const rules = reactive<FormRules>({
    plateNumber: [
      { required: true, message: '请输入挂车车牌号', trigger: 'blur' }
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
          await updateTrailer(form);
        } else {
          await addTrailer(form);
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
