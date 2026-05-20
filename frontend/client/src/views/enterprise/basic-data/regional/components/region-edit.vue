<template>
  <ele-modal
    form
    :width="460"
    :title="isUpdate ? '修改地区' : '添加地区'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      @submit.prevent=""
    >
      <el-form-item>
        <floating-label
          label="上级地区"
          type="input"
          :model-value="currentParentName"
          disabled
        />
      </el-form-item>
      <el-form-item prop="name">
        <floating-label
          label="请输入地区名称"
          type="input"
          v-model.trim="form.name"
          :maxlength="50"
          clearable
        />
      </el-form-item>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item prop="longitude">
            <floating-label
              label="经度"
              type="input"
              v-model="form.longitude"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="latitude">
            <floating-label
              label="纬度"
              type="input"
              v-model="form.latitude"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item prop="sortOrder">
        <floating-label label="排序号" type="input-number">
          <el-input-number
            v-model="form.sortOrder"
            :min="0"
            :max="9999"
            controls-position="right"
            style="width: 100%"
          />
        </floating-label>
      </el-form-item>
      <el-form-item prop="status">
        <el-radio-group v-model="form.status">
          <el-radio :value="1">正常</el-radio>
          <el-radio :value="0">停用</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
          { preset: 'save', onClick: () => handleSave() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, reactive, computed } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { addRegion, updateRegion } from '@/api/basic-data/region';
  import type { Region } from '@/api/basic-data/region/model';

  const props = defineProps<{
    data?: Region | null;
    parentCode?: string;
    parentName?: string;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(false);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);

  const [form, _resetFields, assignFields] = useFormData({
    regionId: void 0 as number | undefined,
    name: '',
    longitude: '' as string | number,
    latitude: '' as string | number,
    sortOrder: 0,
    status: 1
  });

  const validateCoord = (
    _rule: any,
    value: string | number,
    callback: (err?: Error) => void,
    min: number,
    max: number,
    label: string
  ) => {
    if (value === '' || value == null) {
      callback();
      return;
    }
    const num = Number(value);
    if (isNaN(num)) {
      callback(new Error(`${label}必须为数字`));
    } else if (num < min || num > max) {
      callback(new Error(`${label}范围: ${min} ~ ${max}`));
    } else {
      callback();
    }
  };

  const rules = reactive<FormRules>({
    name: [
      {
        required: true,
        message: '请输入地区名称',
        type: 'string',
        trigger: 'blur'
      }
    ],
    longitude: [
      {
        validator: (_r: any, v: any, cb: any) =>
          validateCoord(_r, v, cb, -180, 180, '经度'),
        trigger: 'blur'
      }
    ],
    latitude: [
      {
        validator: (_r: any, v: any, cb: any) =>
          validateCoord(_r, v, cb, -90, 90, '纬度'),
        trigger: 'blur'
      }
    ]
  });

  const currentParentName = computed(() => {
    if (isUpdate.value && props.data) {
      return props.parentName || props.data.parentCode || '—';
    }
    return props.parentName || '—';
  });

  const handleCancel = () => {
    closeModal();
  };

  const toNum = (v: string | number | null | undefined): number | undefined => {
    if (v === '' || v == null) return undefined;
    const n = Number(v);
    return isNaN(n) ? undefined : n;
  };

  const handleSave = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;

      const lng = toNum(form.longitude);
      const lat = toNum(form.latitude);

      const promise = isUpdate.value
        ? updateRegion(form.regionId!, {
            name: form.name,
            sortOrder: form.sortOrder,
            status: form.status,
            longitude: lng,
            latitude: lat
          })
        : addRegion({
            name: form.name,
            parentCode: props.parentCode,
            sortOrder: form.sortOrder,
            status: form.status,
            longitude: lng,
            latitude: lat
          });

      promise
        .then((msg) => {
          loading.value = false;
          EleMessage.success({ message: msg, plain: true });
          emit('done');
          handleCancel();
        })
        .catch((e) => {
          loading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };

  if (props.data) {
    assignFields({
      regionId: props.data.regionId,
      name: props.data.name ?? '',
      longitude: props.data.longitude ?? '',
      latitude: props.data.latitude ?? '',
      sortOrder: props.data.sortOrder ?? 0,
      status: props.data.status ?? 1
    });
    isUpdate.value = true;
  }
</script>
