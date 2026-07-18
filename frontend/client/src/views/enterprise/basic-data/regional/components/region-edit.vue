<template>
  <ele-modal
    form
    :width="720"
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
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="上级地区"
              type="input"
              :model-value="currentParentName"
              disabled
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="name">
            <floating-label
              label="请输入地区名称"
              type="input"
              v-model.trim="form.name"
              :maxlength="50"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item prop="longitude" class="is-map-coord">
        <region-coord-map
          :longitude="form.longitude"
          :latitude="form.latitude"
          :suggestion-city="mapSuggestionCity"
          @change="handleMapChange"
        />
        <div v-if="hasCoord" class="coord-text">
          经度 {{ form.longitude }}，纬度 {{ form.latitude }}
        </div>
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
  import RegionCoordMap from './region-coord-map.vue';

  const props = defineProps<{
    data?: Region | null;
    parentCode?: string;
    parentName?: string;
    /** 上级地区完整路径，如 北京市/市辖区 */
    parentPath?: string;
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
    status: 1
  });

  const hasCoord = computed(() => {
    return (
      form.longitude !== '' &&
      form.longitude != null &&
      form.latitude !== '' &&
      form.latitude != null
    );
  });

  const validateCoords = (
    _rule: any,
    _value: unknown,
    callback: (err?: Error) => void
  ) => {
    const lngRaw = form.longitude;
    const latRaw = form.latitude;
    if (
      lngRaw === '' ||
      lngRaw == null ||
      latRaw === '' ||
      latRaw == null
    ) {
      callback(new Error('请在地图上点选位置'));
      return;
    }
    const lng = Number(lngRaw);
    const lat = Number(latRaw);
    if (isNaN(lng) || isNaN(lat)) {
      callback(new Error('经纬度必须为数字'));
      return;
    }
    if (lng < -180 || lng > 180) {
      callback(new Error('经度范围: -180 ~ 180'));
      return;
    }
    if (lat < -90 || lat > 90) {
      callback(new Error('纬度范围: -90 ~ 90'));
      return;
    }
    callback();
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
        validator: validateCoords,
        trigger: 'change'
      }
    ]
  });

  const currentParentName = computed(() => {
    return props.parentPath || props.parentName || '—';
  });

  const mapSuggestionCity = computed(() => {
    const path = props.parentPath?.trim();
    if (path) {
      const parts = path.split('/').filter(Boolean);
      return parts[parts.length - 1] || '全国';
    }
    return props.parentName?.trim() || '全国';
  });

  const handleMapChange = (payload: { lng: number; lat: number }) => {
    form.longitude = payload.lng;
    form.latitude = payload.lat;
    formRef.value?.validateField?.('longitude');
  };

  const handleCancel = () => {
    closeModal();
  };

  const toNum = (v: string | number | null | undefined): number => {
    return Number(v);
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
            status: form.status,
            longitude: lng,
            latitude: lat
          })
        : addRegion({
            name: form.name,
            parentCode: props.parentCode,
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
      status: props.data.status ?? 1
    });
    isUpdate.value = true;
  }
</script>

<style scoped>
  .coord-text {
    margin-top: 8px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
    line-height: 1.4;
  }

  .is-map-coord :deep(.el-form-item__error) {
    padding-top: 4px;
  }
</style>
