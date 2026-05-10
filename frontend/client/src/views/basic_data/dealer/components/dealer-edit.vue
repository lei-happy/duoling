<template>
  <ele-modal
    form
    :width="680"
    :title="isUpdate ? '编辑经销商' : '新增经销商'"
    :loading="loading"
    class="dealer-edit-modal"
    v-bind="modalProps"
  >
    <div class="dealer-edit-body">
      <el-alert
        v-if="regionResolveBanner"
        class="dealer-region-banner"
        type="warning"
        :closable="false"
        show-icon
      >
        {{ regionResolveBanner }}
      </el-alert>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        class="dealer-edit-form"
        :validate-on-rule-change="false"
        @submit.prevent=""
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item prop="dealerName">
              <floating-label
                label="请输入经销商名称"
                type="input"
                v-model.trim="form.dealerName"
                :maxlength="100"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="dealerType">
              <floating-label
                label="请输入经销商类型"
                type="input"
                v-model.trim="form.dealerType"
                :maxlength="50"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item prop="mainBrand">
              <floating-label
                label="请输入主营品牌"
                type="input"
                v-model.trim="form.mainBrand"
                :maxlength="100"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item prop="regionSelection" label="">
              <regions-select
                v-model="form.regionSelection"
                type="provinceCity"
                placeholder="请选择省、市"
                class="dealer-regions-select"
              />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item prop="addressDetail">
              <floating-label
                label="请输入详细地址"
                type="input"
                v-model.trim="form.addressDetail"
                :maxlength="255"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="longitude">
              <floating-label
                label="经度（选填，最多 6 位小数）"
                type="input"
                input-type="number"
                v-model="longitudeStr"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="latitude">
              <floating-label
                label="纬度（选填，最多 6 位小数）"
                type="input"
                input-type="number"
                v-model="latitudeStr"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>
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
  import { ref, computed, reactive, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import RegionsSelect from '@/components/RegionsSelect/index.vue';
  import {
    useRegionsData,
    filterData,
    getValueLabel
  } from '@/components/RegionsSelect/util';
  import { useFormData } from '@/utils/use-form-data';
  import { addDealer, updateDealer } from '@/api/basic-data/dealer';
  import type { Dealer } from '@/api/basic-data/dealer/model';
  import {
    resolveRegionCodesFromLegacyNames,
    normalizeWhitespace
  } from '../utils/resolve-dealer-region';

  const props = defineProps<{
    data?: Dealer | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(false);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);

  const regionsData = useRegionsData();
  const regionAutoResolved = ref(false);
  const regionResolveBanner = ref('');

  const [form, _resetFields, assignFields] = useFormData({
    dealerId: void 0 as number | undefined,
    dealerName: '',
    dealerType: '',
    mainBrand: '',
    province: '',
    city: '',
    addressDetail: '',
    longitude: undefined as number | undefined,
    latitude: undefined as number | undefined,
    /** 省市区级联选中值 [省code, 市code]，与 RegionsSelect 一致 */
    regionSelection: [] as string[]
  });

  const cascaderProvinceCity = computed(() =>
    filterData(regionsData.value ?? [], 'provinceCity')
  );

  function applyLabelsFromCodes(codes: string[]) {
    if (!codes || codes.length !== 2) {
      form.province = '';
      form.city = '';
      return;
    }
    const labels = getValueLabel(codes, cascaderProvinceCity.value);
    if (labels.length >= 2) {
      form.province = labels[0] ?? '';
      form.city = labels[1] ?? '';
    }
  }

  watch(
    () => form.regionSelection,
    (codes) => {
      if (!codes || codes.length !== 2) {
        form.province = '';
        form.city = '';
        return;
      }
      applyLabelsFromCodes(codes);
    },
    { deep: true }
  );

  function buildResolveBanner(
    reason: 'no_match' | 'ambiguous' | 'empty',
    legacy: { province: string; city: string }
  ): string {
    const p = legacy.province || '（空）';
    const c = legacy.city || '（空）';
    if (reason === 'ambiguous') {
      return `无法在标准行政区中唯一匹配（原数据：省「${p}」市「${c}」），请重新选择省、市。`;
    }
    return `无法在标准行政区中匹配到省、市（原数据：省「${p}」市「${c}」），请重新选择省、市。`;
  }

  function tryResolveRegionFromLegacy() {
    const d = regionsData.value ?? [];
    if (!d.length || regionAutoResolved.value) return;

    const province = form.province;
    const city = form.city;
    if (!normalizeWhitespace(province) && !normalizeWhitespace(city)) {
      regionAutoResolved.value = true;
      regionResolveBanner.value = '';
      form.regionSelection = [];
      return;
    }

    const legacy = { province, city };
    const res = resolveRegionCodesFromLegacyNames(d, province, city);

    if (res.ok) {
      form.regionSelection = [...res.codes];
      regionResolveBanner.value = '';
    } else {
      if (res.reason === 'empty') {
        regionResolveBanner.value = '';
      } else {
        regionResolveBanner.value = buildResolveBanner(res.reason, legacy);
      }
      form.regionSelection = [];
      form.province = '';
      form.city = '';
    }
    regionAutoResolved.value = true;
  }

  watch(
    () => regionsData.value,
    (d) => {
      if (d && d.length > 0) {
        tryResolveRegionFromLegacy();
      }
    },
    { immediate: true }
  );

  const numToStr = (n: number | undefined | null) =>
    n != null && !Number.isNaN(Number(n)) ? String(n) : '';

  const roundCoord = (n: number) => Math.round(n * 1e6) / 1e6;

  const longitudeStr = computed({
    get: () => numToStr(form.longitude),
    set: (v: string) => {
      const t = v?.trim();
      if (t === '' || t == null) {
        form.longitude = undefined;
        return;
      }
      const n = Number(t);
      form.longitude = Number.isFinite(n) ? roundCoord(n) : undefined;
    }
  });

  const latitudeStr = computed({
    get: () => numToStr(form.latitude),
    set: (v: string) => {
      const t = v?.trim();
      if (t === '' || t == null) {
        form.latitude = undefined;
        return;
      }
      const n = Number(t);
      form.latitude = Number.isFinite(n) ? roundCoord(n) : undefined;
    }
  });

  const validateCoord = (
    _rule: unknown,
    value: number | undefined,
    callback: (e?: Error) => void,
    min: number,
    max: number,
    label: string
  ) => {
    if (value == null || Number.isNaN(Number(value))) {
      callback();
      return;
    }
    const num = Number(value);
    if (num < min || num > max) {
      callback(new Error(`${label}有效范围 ${min} ~ ${max}`));
    } else {
      callback();
    }
  };

  const rules = reactive<FormRules>({
    dealerName: [
      { required: true, message: '请输入经销商名称', trigger: 'blur' }
    ],
    dealerType: [
      { required: true, message: '请输入经销商类型', trigger: 'blur' }
    ],
    mainBrand: [{ required: true, message: '请输入主营品牌', trigger: 'blur' }],
    regionSelection: [
      {
        validator: (_r, v, cb) => {
          const ok = Array.isArray(v) && v.length === 2 && !!v[0] && !!v[1];
          if (ok) cb();
          else cb(new Error('请选择省、市'));
        },
        trigger: 'change'
      }
    ],
    addressDetail: [
      { required: true, message: '请输入详细地址', trigger: 'blur' }
    ],
    longitude: [
      {
        validator: (_r, v, cb) =>
          validateCoord(_r, v as number | undefined, cb, -180, 180, '经度'),
        trigger: 'blur'
      }
    ],
    latitude: [
      {
        validator: (_r, v, cb) =>
          validateCoord(_r, v as number | undefined, cb, -90, 90, '纬度'),
        trigger: 'blur'
      }
    ]
  });

  const handleCancel = () => {
    closeModal();
  };

  const handleSave = () => {
    if (form.regionSelection?.length === 2) {
      applyLabelsFromCodes(form.regionSelection);
    }
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;

      const promise = isUpdate.value
        ? updateDealer(form.dealerId!, {
            dealerName: form.dealerName,
            dealerType: form.dealerType,
            mainBrand: form.mainBrand,
            province: form.province,
            city: form.city,
            addressDetail: form.addressDetail,
            longitude: form.longitude,
            latitude: form.latitude
          })
        : addDealer({
            dealerName: form.dealerName,
            dealerType: form.dealerType,
            mainBrand: form.mainBrand,
            province: form.province,
            city: form.city,
            addressDetail: form.addressDetail,
            longitude: form.longitude,
            latitude: form.latitude
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
    assignFields(
      {
        dealerId: props.data.dealerId,
        dealerName: props.data.dealerName ?? '',
        dealerType: props.data.dealerType ?? '',
        mainBrand: props.data.mainBrand ?? '',
        province: props.data.province ?? '',
        city: props.data.city ?? '',
        addressDetail: props.data.addressDetail ?? '',
        longitude: props.data.longitude ?? undefined,
        latitude: props.data.latitude ?? undefined
      },
      ['regionSelection']
    );
    isUpdate.value = true;
  }
</script>

<style scoped>
  .dealer-edit-body {
    padding: 4px 8px 0;
  }

  .dealer-region-banner {
    margin-bottom: 12px;
  }

  .dealer-edit-form {
    margin: 0;
  }

  .dealer-regions-select {
    width: 100%;
  }

  .dealer-edit-modal :deep(.floating-label-wrapper.is-focused .floating-label),
  .dealer-edit-modal :deep(.floating-label-wrapper.has-value .floating-label) {
    transform: translateY(-62%);
    padding: 2px 6px;
    z-index: 4;
    background-color: var(--el-bg-color) !important;
    box-shadow: 0 0 0 2px var(--el-bg-color);
  }

  .dealer-edit-modal :deep(.el-row > .el-col > .el-form-item) {
    margin-bottom: 14px;
  }
</style>
