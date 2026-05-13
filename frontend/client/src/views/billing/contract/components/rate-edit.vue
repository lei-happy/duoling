<template>
  <el-dialog
    :title="isEdit ? '编辑运价' : '新增运价'"
    :model-value="visible"
    width="920px"
    draggable
    :close-on-click-modal="false"
    class="rate-edit-dialog"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="rate-edit-form"
      @submit.prevent=""
    >
      <el-row :gutter="20">
        <el-col :span="24">
          <el-form-item prop="billingMode" class="rate-block-item">
            <div class="rate-block-cap">计费模式</div>
            <el-radio-group
              v-model="form.billingMode"
              @change="onBillingModeRadioChange"
            >
              <el-radio :value="0">台单价</el-radio>
              <el-radio :value="1">单公里单价</el-radio>
              <el-radio :value="2">整单价格</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="originCode">
            <floating-label
              v-model="originCodes"
              label="请选择出发地"
              type="cascader"
              :cascader-options="regionTree"
              :cascader-option-props="regionCascaderProps"
              :cascader-filterable="true"
              @change="onOriginChange"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="destinationCode">
            <floating-label
              v-model="destCodes"
              label="请选择目的地"
              type="cascader"
              :cascader-options="regionTree"
              :cascader-option-props="regionCascaderProps"
              :cascader-filterable="true"
              @change="onDestChange"
            />
          </el-form-item>
        </el-col>
        <template v-if="form.billingMode !== 2">
          <el-col :span="12">
            <el-form-item>
              <floating-label
                v-model="form.vehicleBrand"
                label="请选择品牌（选填）"
                type="select"
                filterable
                clearable
                @change="onBrandChange"
              >
                <el-option
                  v-for="b in brandOptions"
                  :key="b.brandId"
                  :label="b.brandNameCn"
                  :value="b.brandNameCn"
                />
              </floating-label>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item>
              <floating-label
                v-model="form.vehicleModel"
                label="请选择车型（选填）"
                type="select"
                filterable
                clearable
                :disabled="!selectedBrandId"
                @change="onSeriesNameChange"
              >
                <el-option
                  v-for="s in seriesOptions"
                  :key="s.seriesId"
                  :label="s.seriesName"
                  :value="s.seriesName"
                />
              </floating-label>
            </el-form-item>
          </el-col>
        </template>
        <el-col v-if="form.billingMode === 1" :span="12">
          <el-form-item prop="distanceKm" class="rate-num-item">
            <div class="rate-num-item__cap">线路公里数</div>
            <el-input-number
              v-model="form.distanceKm"
              class="rate-num-item__ctl ele-fluid"
              :precision="2"
              :min="0.01"
              controls-position="right"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="unitPrice" class="rate-num-item">
            <div class="rate-num-item__cap">{{ priceLabel }}</div>
            <el-input-number
              v-model="form.unitPrice"
              class="rate-num-item__ctl ele-fluid"
              :precision="2"
              :min="0"
              :placeholder="pricePlaceholder"
              controls-position="right"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="priceType" class="rate-block-item">
            <div class="rate-block-cap">运价类型</div>
            <el-radio-group v-model="form.priceType">
              <el-radio :value="0">明确运价</el-radio>
              <el-radio :value="1">预估运价</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="effectiveDate">
            <floating-label
              v-model="form.effectiveDate"
              label="请选择生效日期"
              type="date"
              value-format="YYYY-MM-DD"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="expiryDate">
            <floating-label
              v-model="form.expiryDate"
              label="请选择失效日期"
              type="date"
              value-format="YYYY-MM-DD"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item class="rate-num-item">
            <div class="rate-num-item__cap">最低运费(元，可空)</div>
            <el-input-number
              v-model="form.minAmount"
              class="rate-num-item__ctl ele-fluid"
              :precision="2"
              :min="0"
              controls-position="right"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item class="rate-num-item">
            <div class="rate-num-item__cap">优先级（数值越大越优先）</div>
            <el-input-number
              v-model="form.priority"
              class="rate-num-item__ctl ele-fluid"
              :min="0"
              :step="1"
              controls-position="right"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item class="rate-block-item">
            <div class="rate-block-cap">线路方向</div>
            <el-radio-group v-model="form.isBidirectional">
              <el-radio :value="0">单向</el-radio>
              <el-radio :value="1">双向</el-radio>
            </el-radio-group>
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
  import { ref, reactive, watch, computed, nextTick } from 'vue';
  import type { FormInstance, FormRules, CascaderProps } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { ElMessageBox } from 'element-plus';
  import {
    addRate,
    updateRate,
    checkRateConflict
  } from '@/api/billing/contract';
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
    customerId?: number;
    data: FreightRate | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<FreightRate>({
    billingMode: 0,
    priceType: 0,
    priority: 0,
    isBidirectional: 0
  });

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

  const onBillingModeRadioChange = () => {
    const v = Number(form.billingMode ?? 0);
    if (v === 2) {
      form.vehicleBrand = undefined;
      form.vehicleModel = undefined;
      selectedBrandId.value = null;
      seriesOptions.value = [];
    }
    if (v !== 1) {
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

  const onOriginChange = (val?: string[]) => {
    if (val && val.length) {
      form.originCode = val[val.length - 1];
      form.origin = findRegionName(val);
    } else {
      form.originCode = undefined;
      form.origin = undefined;
    }
  };

  const onDestChange = (val?: string[]) => {
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
    form.seriesId = null;
    seriesOptions.value = [];
    const brand = brandOptions.value.find((b) => b.brandNameCn === brandName);
    if (brand) {
      selectedBrandId.value = brand.brandId;
      form.brandId = brand.brandId;
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
      form.brandId = null;
    }
  };

  const onSeriesNameChange = (seriesName?: string) => {
    if (!seriesName) {
      form.seriesId = null;
      return;
    }
    const item = seriesOptions.value.find((s) => s.seriesName === seriesName);
    form.seriesId = item ? item.seriesId : null;
  };

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
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
        if (props.data.vehicleBrand) {
          const savedModel = props.data.vehicleModel;
          void (async () => {
            await onBrandChange(props.data!.vehicleBrand!);
            if (savedModel) {
              form.vehicleModel = savedModel;
            }
          })();
        }
      } else {
        Object.keys(form).forEach((k) => {
          (form as Record<string, unknown>)[k] = undefined;
        });
        form.billingMode = 0;
        form.priceType = 0;
        form.priority = 0;
        form.isBidirectional = 0;
      }
      if (props.customerId && !form.customerId) {
        form.customerId = props.customerId;
      }
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const buildConflictPayload = () => {
    return {
      rateId: form.id,
      contractId: props.contractId!,
      customerId: form.customerId!,
      originRegionId: form.originRegionId ?? null,
      originCode: form.originCode ?? null,
      destinationRegionId: form.destinationRegionId ?? null,
      destinationCode: form.destinationCode ?? null,
      brandId: form.brandId ?? null,
      seriesId: form.seriesId ?? null,
      priority: form.priority ?? 0,
      priceType: form.priceType ?? 0,
      isBidirectional: form.isBidirectional ?? 0,
      effectiveDate: form.effectiveDate ?? null,
      expiryDate: form.expiryDate ?? null
    };
  };

  const confirmConflict = async (
    conflicts: Array<{
      rateId: number;
      origin?: string;
      destination?: string;
      effectiveDate?: string | null;
      expiryDate?: string | null;
      severity?: string;
    }>
  ) => {
    const list = conflicts
      .slice(0, 5)
      .map((c, i) => {
        const sev = c.severity === 'error' ? '[强冲突]' : '[弱冲突]';
        const period = `${c.effectiveDate || ''}~${c.expiryDate || ''}`;
        return `${i + 1}. #${c.rateId} ${sev} ${c.origin || ''} → ${c.destination || ''} (${period})`;
      })
      .join('<br/>');
    return ElMessageBox.confirm(
      `检测到 ${conflicts.length} 条冲突运价，是否仍要保存？<br/>${list}`,
      '运价冲突提醒',
      {
        confirmButtonText: '继续保存',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )
      .then(() => true)
      .catch(() => false);
  };

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        try {
          if (form.customerId && props.contractId) {
            const conflict = await checkRateConflict(buildConflictPayload());
            if (conflict && conflict.count > 0) {
              const ok = await confirmConflict(conflict.conflicts);
              if (!ok) {
                loading.value = false;
                return;
              }
            }
          }
        } catch (_) {
          /* ignore conflict check errors and continue */
        }
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

<style scoped>
  .rate-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
</style>

<style scoped lang="scss">
  .rate-block-item {
    margin-bottom: 18px;
  }

  .rate-block-cap {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-bottom: 8px;
    font-weight: 500;
    line-height: 1.2;
  }

  .rate-num-item__cap {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-bottom: 6px;
    font-weight: 500;
    line-height: 1.2;
  }

  .rate-num-item__ctl {
    width: 100%;
  }

  .rate-edit-dialog :deep(.floating-label-wrapper.is-focused .floating-label),
  .rate-edit-dialog :deep(.floating-label-wrapper.has-value .floating-label) {
    color: var(--el-color-primary);
  }

  .rate-edit-dialog :deep(.el-input-number .el-input__wrapper) {
    width: 100%;
  }
</style>
