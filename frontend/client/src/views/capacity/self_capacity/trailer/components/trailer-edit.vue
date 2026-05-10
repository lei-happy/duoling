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
      label-width="0"
      @submit.prevent=""
    >
      <el-divider content-position="left">基础信息</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item prop="plateNumber">
            <floating-label
              label="请输入挂车车牌号"
              type="input"
              v-model.trim="form.plateNumber"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-divider content-position="left">详细信息</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入挂车类型"
              type="input"
              v-model.trim="form.trailerType"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入轴数"
              type="input"
              input-type="number"
              v-model="axleCountStr"
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
        <el-col :span="8">
          <el-form-item>
            <floating-label
              label="请输入车厢长(m)"
              type="input"
              input-type="number"
              v-model="lengthStr"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <floating-label
              label="请输入车厢宽(m)"
              type="input"
              input-type="number"
              v-model="widthStr"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <floating-label
              label="请输入车厢高(m)"
              type="input"
              input-type="number"
              v-model="heightStr"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入车位数"
              type="input"
              input-type="number"
              v-model="parkingSpotsStr"
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
  import { addTrailer, updateTrailer } from '@/api/capacity/self_capacity/trailer';
  import type { Trailer } from '@/api/capacity/self_capacity/trailer/model';

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

  const round2 = (n: number) => Math.round(n * 100) / 100;

  const decStr = (key: 'loadCapacity' | 'volumeCapacity' | 'length' | 'width' | 'height') =>
    computed({
      get: () => {
        const n = form[key];
        return n != null && !Number.isNaN(Number(n)) ? String(n) : '';
      },
      set: (v: string) => {
        const t = v?.trim();
        if (t === '' || t == null) {
          form[key] = void 0;
          return;
        }
        const n = Number(t);
        form[key] = Number.isFinite(n) ? round2(n) : void 0;
      }
    });

  const loadCapacityStr = decStr('loadCapacity');
  const volumeCapacityStr = decStr('volumeCapacity');
  const lengthStr = decStr('length');
  const widthStr = decStr('width');
  const heightStr = decStr('height');

  const axleCountStr = computed({
    get: () =>
      form.axleCount != null && !Number.isNaN(Number(form.axleCount))
        ? String(form.axleCount)
        : '',
    set: (v: string) => {
      const t = v?.trim();
      if (t === '' || t == null) {
        form.axleCount = void 0;
        return;
      }
      const n = parseInt(t, 10);
      if (!Number.isFinite(n)) {
        form.axleCount = void 0;
        return;
      }
      form.axleCount = Math.min(10, Math.max(1, n));
    }
  });

  const parkingSpotsStr = computed({
    get: () =>
      form.parkingSpots != null && !Number.isNaN(Number(form.parkingSpots))
        ? String(form.parkingSpots)
        : '',
    set: (v: string) => {
      const t = v?.trim();
      if (t === '' || t == null) {
        form.parkingSpots = void 0;
        return;
      }
      const n = parseInt(t, 10);
      form.parkingSpots =
        Number.isFinite(n) && n >= 0 ? n : void 0;
    }
  });

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
