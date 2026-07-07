<template>
  <el-dialog
    :title="isEdit ? '编辑承运价' : '新增承运价'"
    :model-value="visible"
    width="680px"
    align-center
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
      :validate-on-rule-change="false"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <!-- 线路与车型（各计费模式通用） -->
        <el-col :span="24">
          <el-divider content-position="left" class="rate-section-divider">
            线路与车型
          </el-divider>
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

        <!-- 计费与单价 -->
        <el-col :span="24">
          <el-divider content-position="left" class="rate-section-divider">
            计费与单价
          </el-divider>
        </el-col>
        <el-col :span="24">
          <el-form-item prop="billingMode" class="rate-form-item--inline">
            <div class="rate-inline-field">
              <span class="rate-inline-field__label">计费模式</span>
              <el-radio-group
                v-model="form.billingMode"
                class="rate-inline-field__control rate-inline-field__radios"
                @change="onBillingModeRadioChange"
              >
                <el-radio :value="0">按台计价（元/台）</el-radio>
                <el-radio :value="1">按公里计价（元/台·公里）</el-radio>
                <el-radio :value="2">整单一口价（元）</el-radio>
              </el-radio-group>
            </div>
          </el-form-item>
        </el-col>
        <el-col v-if="form.billingMode === 1" :span="12">
          <el-form-item prop="distanceKm">
            <floating-label
              v-model="form.distanceKm"
              label="请输入线路公里数"
              type="input-number"
              :input-number-min="0.01"
              :input-number-precision="2"
              :input-number-step="0.1"
            />
          </el-form-item>
        </el-col>
        <el-col :span="form.billingMode === 1 ? 12 : 24">
          <el-form-item prop="unitPrice">
            <floating-label
              v-model="form.unitPrice"
              :label="priceLabel"
              type="input-number"
              :input-number-min="0"
              :input-number-precision="2"
              :input-number-step="0.01"
            />
          </el-form-item>
        </el-col>

        <!-- 运价属性 -->
        <el-col :span="24">
          <el-divider content-position="left" class="rate-section-divider">
            运价属性
          </el-divider>
        </el-col>
        <el-col :span="24">
          <div class="rate-attr-line">
            <div class="rate-attr-line__type">
              <el-form-item prop="priceType" class="rate-form-item--inline">
                <div class="rate-inline-field">
                  <span class="rate-inline-field__label">运价类型</span>
                  <el-radio-group
                    v-model="form.priceType"
                    class="rate-inline-field__control rate-inline-field__radios"
                  >
                    <el-radio :value="0">明确运价</el-radio>
                    <el-radio :value="1">预估运价</el-radio>
                  </el-radio-group>
                </div>
              </el-form-item>
            </div>
            <div class="rate-attr-line__period">
              <el-form-item
                prop="rateValidPeriod"
                class="rate-form-item--period"
              >
                <floating-label
                  v-model="form.rateValidPeriod"
                  label="有效期范围"
                  type="date"
                  date-type="daterange"
                  value-format="YYYY-MM-DD"
                  range-separator="至"
                  start-placeholder="生效日期"
                  end-placeholder="失效日期"
                  clearable
                />
              </el-form-item>
            </div>
          </div>
        </el-col>

        <!-- 其它 -->
        <el-col :span="24">
          <el-divider content-position="left" class="rate-section-divider">
            其它
          </el-divider>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.minAmount"
              label="最低运费(元，可空)"
              type="input-number"
              :input-number-min="0"
              :input-number-precision="2"
              :input-number-step="0.01"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item class="rate-form-item--inline">
            <div class="rate-inline-field rate-inline-field--priority">
              <span class="rate-inline-field__label">优先级</span>
              <div class="rate-inline-field__control">
                <el-input-number
                  v-model="form.priority"
                  class="rate-priority-input ele-fluid"
                  :min="0"
                  :step="1"
                  controls-position="right"
                />
                <span class="rate-inline-field__hint">数值越大越优先</span>
              </div>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item prop="isBidirectional" class="rate-form-item--inline">
            <div class="rate-inline-field">
              <span class="rate-inline-field__label">线路方向</span>
              <el-radio-group
                v-model="form.isBidirectional"
                class="rate-inline-field__control rate-inline-field__radios"
              >
                <el-radio :value="0">单向</el-radio>
                <el-radio :value="1">双向</el-radio>
              </el-radio-group>
            </div>
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
  import { addRate, updateRate } from '@/api/billing/carrier-contract';
  import { listVehicleBrandOptions } from '@/api/basic-data/vehicle-brand';
  import { pageVehicleSeries } from '@/api/basic-data/vehicle-series';
  import { getRegionNavTree } from '@/api/basic-data/region';
  import type { CarrierRate } from '@/api/billing/carrier-contract/model';
  import type { VehicleBrandOption } from '@/api/basic-data/vehicle-brand/model';
  import type { VehicleSeries } from '@/api/basic-data/vehicle-series/model';
  import type { RegionNavNode } from '@/api/basic-data/region/model';
  import {
    findLeafRegionByCodePath,
    findRegionCodePath
  } from '@/utils/region-nav-tree';

  type RateEditForm = CarrierRate & {
    rateValidPeriod?: [string, string] | null;
  };

  const props = defineProps<{
    visible: boolean;
    contractId?: number;
    carrierId?: number;
    data: CarrierRate | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<RateEditForm>({
    billingMode: 0,
    priceType: 0,
    priority: 0,
    isBidirectional: 0,
    rateValidPeriod: null
  });

  const regionTree = ref<RegionNavNode[]>([]);
  const brandOptions = ref<VehicleBrandOption[]>([]);
  const seriesOptions = ref<VehicleSeries[]>([]);
  const selectedBrandId = ref<number | null>(null);
  const originCodes = ref<string[]>([]);
  const destCodes = ref<string[]>([]);

  const priceLabel = computed(() => {
    if (form.billingMode === 1) return '单价(元/台·公里)';
    if (form.billingMode === 2) return '整单价格(元)';
    return '单车运费(元/台)';
  });

  const regionCascaderProps: CascaderProps = {
    value: 'code',
    label: 'name',
    children: 'children',
    emitPath: true,
    checkStrictly: true
  };

  const syncDatesFromRange = () => {
    const v = form.rateValidPeriod;
    if (v && v.length >= 2 && v[0] && v[1]) {
      form.effectiveDate = v[0];
      form.expiryDate = v[1];
    } else {
      form.effectiveDate = undefined;
      form.expiryDate = undefined;
    }
  };

  watch(
    () => form.rateValidPeriod,
    () => {
      syncDatesFromRange();
    },
    { deep: true }
  );

  /** 仅在点击「保存」时校验：不写 blur/change，避免填写过程中提前报错 */
  const rules = computed<FormRules>(() => {
    const base: FormRules = {
      originCode: [{ required: true, message: '请选择出发地', trigger: [] }],
      destinationCode: [
        { required: true, message: '请选择目的地', trigger: [] }
      ],
      unitPrice: [{ required: true, message: '请输入单价', trigger: [] }],
      rateValidPeriod: [
        {
          required: true,
          message: '请选择有效期范围',
          trigger: [],
          type: 'array'
        },
        {
          validator: (_rule, val, callback) => {
            if (!val || !Array.isArray(val) || val.length < 2) {
              callback(new Error('请选择完整的生效与失效日期'));
              return;
            }
            const [a, b] = val;
            if (!a || !b) {
              callback(new Error('请选择完整的生效与失效日期'));
              return;
            }
            if (a > b) {
              callback(new Error('失效日期不能早于生效日期'));
              return;
            }
            callback();
          },
          trigger: []
        }
      ]
    };
    if (form.billingMode === 1) {
      base.distanceKm = [
        { required: true, message: '请输入线路公里数', trigger: [] }
      ];
    }
    return base;
  });

  const onBillingModeRadioChange = () => {
    const v = Number(form.billingMode ?? 0);
    if (v === 2) {
      form.vehicleBrand = null;
      form.vehicleModel = null;
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
      const leaf = findLeafRegionByCodePath(regionTree.value, val);
      form.originRegionId = leaf?.regionId ?? undefined;
    } else {
      form.originCode = undefined;
      form.origin = undefined;
      form.originRegionId = undefined;
    }
  };

  const onDestChange = (val?: string[]) => {
    if (val && val.length) {
      form.destinationCode = val[val.length - 1];
      form.destination = findRegionName(val);
      const leaf = findLeafRegionByCodePath(regionTree.value, val);
      form.destinationRegionId = leaf?.regionId ?? undefined;
    } else {
      form.destinationCode = undefined;
      form.destination = undefined;
      form.destinationRegionId = undefined;
    }
  };

  const onBrandChange = async (brandName?: string | null) => {
    form.vehicleModel = null;
    form.seriesId = null;
    seriesOptions.value = [];
    const name = brandName?.trim();
    const brand = name
      ? brandOptions.value.find((b) => b.brandNameCn === name)
      : undefined;
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
      form.vehicleBrand = null;
    }
  };

  const onSeriesNameChange = (seriesName?: string) => {
    if (!seriesName) {
      form.seriesId = null;
      form.vehicleModel = null;
      return;
    }
    const item = seriesOptions.value.find((s) => s.seriesName === seriesName);
    form.seriesId = item ? item.seriesId : null;
  };

  watch(
    () => props.visible,
    async (val) => {
      if (!val) return;
      selectedBrandId.value = null;
      originCodes.value = [];
      destCodes.value = [];
      seriesOptions.value = [];

      await loadBaseData();

      if (props.data) {
        Object.assign(form, props.data);
        if (form.billingMode === undefined) form.billingMode = 0;
        if (form.priceType === undefined) form.priceType = 0;

        const d = props.data;
        if (d.originCode) {
          const path = findRegionCodePath(regionTree.value, d.originCode);
          originCodes.value = path ?? [d.originCode];
        }
        if (d.destinationCode) {
          const path = findRegionCodePath(regionTree.value, d.destinationCode);
          destCodes.value = path ?? [d.destinationCode];
        }

        const oLeaf = findLeafRegionByCodePath(
          regionTree.value,
          originCodes.value
        );
        const dLeaf = findLeafRegionByCodePath(
          regionTree.value,
          destCodes.value
        );
        if (oLeaf) form.originRegionId = oLeaf.regionId;
        if (dLeaf) form.destinationRegionId = dLeaf.regionId;

        if (form.effectiveDate && form.expiryDate) {
          form.rateValidPeriod = [form.effectiveDate, form.expiryDate];
        } else {
          form.rateValidPeriod = null;
        }

        const brandEntry =
          brandOptions.value.find(
            (b) =>
              (d.vehicleBrand?.trim() &&
                b.brandNameCn === d.vehicleBrand.trim()) ||
              (d.brandId != null && b.brandId === d.brandId)
          ) ?? null;

        if (brandEntry) {
          const savedModel = d.vehicleModel?.trim();
          const savedSeriesId = d.seriesId;
          await onBrandChange(brandEntry.brandNameCn);
          if (savedModel) {
            form.vehicleModel = savedModel;
          } else if (savedSeriesId != null) {
            const hit = seriesOptions.value.find(
              (s) => s.seriesId === savedSeriesId
            );
            if (hit) {
              form.vehicleModel = hit.seriesName;
            }
          }
        }
      } else {
        Object.keys(form).forEach((k) => {
          (form as Record<string, unknown>)[k] = undefined;
        });
        form.billingMode = 0;
        form.priceType = 0;
        form.priority = 0;
        form.isBidirectional = 0;
        form.rateValidPeriod = null;
      }
      if (props.carrierId && !form.carrierId) {
        form.carrierId = props.carrierId;
      }
      await nextTick();
      formRef.value?.clearValidate();
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const toPayload = (): CarrierRate => {
    const { rateValidPeriod: _rp, ...rest } = form;
    return rest;
  };

  const handleSubmit = () => {
    syncDatesFromRange();
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        const payload = toPayload();
        if (isEdit.value) {
          await updateRate(payload.id!, payload);
        } else {
          await addRate(props.contractId!, payload);
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

  .rate-form-item--inline :deep(.el-form-item__content) {
    margin-left: 0 !important;
    line-height: normal;
  }

  .rate-form-item--period :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }
</style>

<style scoped lang="scss">
  .rate-attr-line {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    column-gap: 16px;
    row-gap: 10px;
    width: 100%;
    margin-bottom: 18px;
  }

  .rate-attr-line :deep(.el-form-item) {
    margin-bottom: 0;
  }

  .rate-attr-line__type {
    flex: 0 0 auto;
  }

  .rate-attr-line__period {
    flex: 1 1 220px;
    min-width: 0;
  }

  .rate-section-divider {
    margin: 10px 0 22px;
  }

  .rate-section-divider :deep(.el-divider__text) {
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-regular);
    padding-left: 0;
    background: var(--el-bg-color);
  }

  /* 浮动标签有值/聚焦时会上移到输入框上沿外，预留垂直空间避免与分节标题重叠 */
  .rate-edit-dialog :deep(.el-form-item__content > .floating-label-wrapper) {
    margin-top: 10px;
  }

  .rate-inline-field {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    column-gap: 16px;
    row-gap: 8px;
    width: 100%;
    min-height: 32px;
  }

  .rate-inline-field__label {
    flex: 0 0 84px;
    width: 84px;
    text-align: right;
    font-size: 14px;
    color: var(--el-text-color-regular);
    line-height: 32px;
    box-sizing: border-box;
  }

  .rate-inline-field__label.is-required::before {
    content: '*';
    color: var(--el-color-danger);
    margin-right: 4px;
  }

  .rate-inline-field__control {
    flex: 1;
    min-width: 0;
  }

  .rate-inline-field__radios {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px 20px;
    line-height: 32px;
  }

  .rate-inline-field__radios :deep(.el-radio) {
    margin-right: 0;
    height: 32px;
    display: inline-flex;
    align-items: center;
  }

  .rate-inline-field__radios :deep(.el-radio__input) {
    display: flex;
    align-items: center;
  }

  .rate-inline-field__radios :deep(.el-radio__label) {
    line-height: 1.25;
    padding-left: 8px;
  }

  .rate-inline-field--priority {
    align-items: flex-start;
  }

  .rate-inline-field--priority .rate-inline-field__label {
    padding-top: 4px;
    line-height: 1.4;
  }

  .rate-inline-field__hint {
    display: block;
    margin-top: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.3;
  }

  .rate-priority-input {
    width: 100%;
    max-width: 200px;
  }

  .rate-attr-line__period :deep(.el-date-editor.el-date-editor--daterange) {
    width: 100%;
    max-width: 100%;
  }

  .rate-edit-dialog :deep(.floating-label-wrapper.is-focused .floating-label),
  .rate-edit-dialog :deep(.floating-label-wrapper.has-value .floating-label) {
    color: var(--el-color-primary);
  }

  .rate-edit-dialog :deep(.el-input-number .el-input__wrapper) {
    width: 100%;
  }
</style>
