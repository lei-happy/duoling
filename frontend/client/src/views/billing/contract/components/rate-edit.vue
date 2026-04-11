<template>
  <el-dialog
    :title="isEdit ? '编辑运价' : '新增运价'"
    :model-value="visible"
    @update:model-value="updateVisible"
    width="640px"
    draggable
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :span="24">
          <el-form-item label="计费模式" prop="billingMode">
            <el-radio-group
              v-model="form.billingMode"
              @change="onBillingModeChange"
            >
              <el-radio :value="0">台单价</el-radio>
              <el-radio :value="1">单公里单价</el-radio>
              <el-radio :value="2">整单价格</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="出发地" prop="originCode">
            <el-cascader
              v-model="originCodes"
              :options="regionTree"
              :props="regionCascaderProps"
              placeholder="请选择出发地"
              filterable
              style="width: 100%"
              @change="onOriginChange"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="目的地" prop="destinationCode">
            <el-cascader
              v-model="destCodes"
              :options="regionTree"
              :props="regionCascaderProps"
              placeholder="请选择目的地"
              filterable
              style="width: 100%"
              @change="onDestChange"
            />
          </el-form-item>
        </el-col>
        <template v-if="form.billingMode !== 2">
          <el-col :span="12">
            <el-form-item label="品牌">
              <el-select
                v-model="form.vehicleBrand"
                placeholder="请选择品牌(选填)"
                filterable
                clearable
                style="width: 100%"
                @change="onBrandChange"
              >
                <el-option
                  v-for="b in brandOptions"
                  :key="b.brandId"
                  :label="b.brandNameCn"
                  :value="b.brandNameCn"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="车型">
              <el-select
                v-model="form.vehicleModel"
                placeholder="请选择车型(选填)"
                filterable
                clearable
                style="width: 100%"
                :disabled="!selectedBrandId"
              >
                <el-option
                  v-for="s in seriesOptions"
                  :key="s.seriesId"
                  :label="s.seriesName"
                  :value="s.seriesName"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </template>
        <el-col :span="12" v-if="form.billingMode === 1">
          <el-form-item label="线路公里数" prop="distanceKm">
            <el-input-number
              v-model="form.distanceKm"
              :precision="2"
              :min="0.01"
              placeholder="公里"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="priceLabel" prop="unitPrice">
            <el-input-number
              v-model="form.unitPrice"
              :precision="2"
              :min="0"
              :placeholder="pricePlaceholder"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="运价类型" prop="priceType">
            <el-radio-group v-model="form.priceType">
              <el-radio :value="0">明确运价</el-radio>
              <el-radio :value="1">预估运价</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="生效日期" prop="effectiveDate">
            <el-date-picker
              v-model="form.effectiveDate"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="请选择生效日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="失效日期" prop="expiryDate">
            <el-date-picker
              v-model="form.expiryDate"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="请选择失效日期"
              style="width: 100%"
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
  import type { FormInstance, FormRules, CascaderProps } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { addRate, updateRate } from '@/api/billing/contract';
  import { listVehicleBrandOptions } from '@/api/basic-data/vehicle-brand';
  import { pageVehicleSeries } from '@/api/basic-data/vehicle-series';
  import { getRegionNavTree } from '@/api/basic-data/region';
  import type { FreightRate } from '@/api/billing/contract/model';
  import type { VehicleBrandOption } from '@/api/basic-data/vehicle-brand/model';
  import type { VehicleSeries } from '@/api/basic-data/vehicle-series/model';
  import type { RegionNavNode } from '@/api/basic-data/region/model';

  const props = defineProps<{
    visible: boolean;
    contractId?: number;
    data: FreightRate | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<FreightRate>({ billingMode: 0, priceType: 0 });

  const regionTree = ref<RegionNavNode[]>([]);
  const brandOptions = ref<VehicleBrandOption[]>([]);
  const seriesOptions = ref<VehicleSeries[]>([]);
  const selectedBrandId = ref<number | null>(null);
  const originCodes = ref<string[]>([]);
  const destCodes = ref<string[]>([]);

  const priceLabel = computed(() => {
    if (form.billingMode === 1) return '单价(元/台·km)';
    if (form.billingMode === 2) return '整单价格(元)';
    return '单车运费(元/台)';
  });

  const pricePlaceholder = computed(() => {
    if (form.billingMode === 1) return '元/台/公里';
    if (form.billingMode === 2) return '元/整单';
    return '元/台';
  });

  const regionCascaderProps: CascaderProps = {
    value: 'code',
    label: 'name',
    children: 'children',
    emitPath: true,
    checkStrictly: true
  };

  const rules = computed<FormRules>(() => {
    const base: FormRules = {
      originCode: [
        { required: true, message: '请选择出发地', trigger: 'change' }
      ],
      destinationCode: [
        { required: true, message: '请选择目的地', trigger: 'change' }
      ],
      unitPrice: [{ required: true, message: '请输入单价', trigger: 'blur' }],
      effectiveDate: [
        { required: true, message: '请选择生效日期', trigger: 'change' }
      ],
      expiryDate: [
        { required: true, message: '请选择失效日期', trigger: 'change' }
      ]
    };
    if (form.billingMode === 1) {
      base.distanceKm = [
        { required: true, message: '请输入线路公里数', trigger: 'blur' }
      ];
    }
    return base;
  });

  const onBillingModeChange = (val: number) => {
    if (val === 2) {
      form.vehicleBrand = undefined;
      form.vehicleModel = undefined;
      selectedBrandId.value = null;
      seriesOptions.value = [];
    }
    if (val !== 1) {
      form.distanceKm = undefined;
    }
  };

  const loadBaseData = async () => {
    try {
      const [regions, brands] = await Promise.all([
        getRegionNavTree().catch(() => []),
        listVehicleBrandOptions().catch(() => [])
      ]);
      regionTree.value = regions ?? [];
      brandOptions.value = brands ?? [];
    } catch (_) {
      /* ignore */
    }
  };

  const findRegionName = (codes: string[]): string => {
    if (!codes.length) return '';
    const names: string[] = [];
    let nodes = regionTree.value;
    for (const code of codes) {
      const node = nodes.find((n) => n.code === code);
      if (node) {
        names.push(node.name);
        nodes = node.children ?? [];
      }
    }
    return names.join('/');
  };

  const onOriginChange = (val: string[]) => {
    if (val && val.length) {
      form.originCode = val[val.length - 1];
      form.origin = findRegionName(val);
    } else {
      form.originCode = undefined;
      form.origin = undefined;
    }
  };

  const onDestChange = (val: string[]) => {
    if (val && val.length) {
      form.destinationCode = val[val.length - 1];
      form.destination = findRegionName(val);
    } else {
      form.destinationCode = undefined;
      form.destination = undefined;
    }
  };

  const onBrandChange = async (brandName: string) => {
    form.vehicleModel = undefined;
    seriesOptions.value = [];
    const brand = brandOptions.value.find((b) => b.brandNameCn === brandName);
    if (brand) {
      selectedBrandId.value = brand.brandId;
      try {
        const data = await pageVehicleSeries({
          brandId: brand.brandId,
          page: 1,
          limit: 200
        });
        seriesOptions.value = data?.list ?? [];
      } catch (_) {
        seriesOptions.value = [];
      }
    } else {
      selectedBrandId.value = null;
    }
  };

  watch(
    () => props.visible,
    (val) => {
      if (val) {
        loadBaseData();
        selectedBrandId.value = null;
        originCodes.value = [];
        destCodes.value = [];
        if (props.data) {
          Object.assign(form, props.data);
          if (form.billingMode === undefined) form.billingMode = 0;
          if (form.priceType === undefined) form.priceType = 0;
          if (props.data.originCode) {
            originCodes.value = [props.data.originCode];
          }
          if (props.data.destinationCode) {
            destCodes.value = [props.data.destinationCode];
          }
        } else {
          Object.keys(form).forEach((k) => {
            (form as any)[k] = undefined;
          });
          form.billingMode = 0;
          form.priceType = 0;
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
          await updateRate(form.id!, form);
        } else {
          await addRate(props.contractId!, form);
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
