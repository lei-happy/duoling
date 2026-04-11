<template>
  <el-drawer
    :model-value="visible"
    :title="isEdit ? '编辑运单' : '新增运单'"
    direction="rtl"
    size="680px"
    append-to-body
    destroy-on-close
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="waybill-edit-drawer"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      label-width="80px"
      class="waybill-edit-form waybill-edit-form--compact"
      @submit.prevent=""
    >
      <div class="waybill-section-title">基本信息</div>
      <el-row :gutter="10">
        <el-col :xs="24" :sm="12" :md="8">
          <el-form-item>
            <floating-label
              label="请输入运单编号"
              type="input"
              v-model.trim="form.waybillNo"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-form-item prop="customerId">
            <floating-label
              v-model="form.customerId"
              label="请选择客户"
              type="select"
              filterable
              :filter-method="setCustomerFilter"
              clearable
              @change="onCustomerChange"
            >
              <el-option
                v-for="item in customersShown"
                :key="item.id"
                :label="item.customerName"
                :value="item.id"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="24" :md="8">
          <el-form-item>
            <floating-label
              label="计划下达时间"
              type="date"
              date-type="datetime"
              v-model="form.planIssueTime"
              value-format="YYYY-MM-DD HH:mm:ss"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>

      <div class="waybill-section-title">运输信息</div>
      <el-row :gutter="10">
        <el-col :span="12" :xs="24">
          <el-form-item
            label="出发地"
            prop="originCode"
            class="waybill-item-tight-label"
          >
            <el-cascader
              v-model="originCodes"
              class="ele-fluid"
              :options="regionTree"
              :props="regionCascaderProps"
              placeholder="请选择出发地"
              filterable
              @change="onOriginChange"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12" :xs="24">
          <el-form-item
            label="目的地"
            prop="destinationCode"
            class="waybill-item-tight-label"
          >
            <el-cascader
              v-model="destCodes"
              class="ele-fluid"
              :options="regionTree"
              :props="regionCascaderProps"
              placeholder="请选择目的地"
              filterable
              @change="onDestChange"
            />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-form-item>
            <floating-label
              v-model="form.vehicleBrand"
              label="请选择商品车品牌"
              type="select"
              filterable
              :filter-method="setBrandFilter"
              clearable
              @change="onBrandChange"
            >
              <el-option
                v-for="b in brandsShown"
                :key="b.brandId"
                :label="b.brandNameCn"
                :value="b.brandNameCn"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-form-item>
            <floating-label
              v-model="form.vehicleModel"
              label="请选择车型"
              type="select"
              filterable
              :filter-method="setSeriesFilter"
              :disabled="!selectedBrandId"
              clearable
            >
              <el-option
                v-for="s in seriesShown"
                :key="s.seriesId"
                :label="s.seriesName"
                :value="s.seriesName"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-form-item
            label="台数"
            prop="quantity"
            class="waybill-item-tight-label"
          >
            <el-input-number
              v-model="form.quantity"
              :min="1"
              class="ele-fluid"
              controls-position="right"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <div class="waybill-section-title">收车门店</div>
      <el-row :gutter="10">
        <el-col :xs="24" :sm="12" :md="8">
          <el-form-item>
            <floating-label
              v-model="selectedDealerId"
              label="请选择经销商门店"
              type="select"
              filterable
              :filter-method="setDealerFilter"
              clearable
              @change="onDealerChange"
            >
              <el-option
                v-for="d in dealersShown"
                :key="d.dealerId"
                :label="d.dealerName"
                :value="d.dealerId"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-form-item>
            <floating-label
              label="请输入联系人"
              type="input"
              v-model.trim="form.dealerContact"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-form-item>
            <floating-label
              label="请输入电话"
              type="input"
              v-model.trim="form.dealerPhone"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <floating-label
              label="门店地址"
              type="input"
              v-model="form.dealerAddress"
              :disabled="true"
              :clearable="false"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <template v-if="freightCalcMode !== 'auto_required'">
        <div class="waybill-section-title">运费信息</div>
        <el-row :gutter="10" align="middle">
          <el-col :xs="24" :sm="10" :md="8">
            <el-form-item label="金额（元）" class="waybill-item-tight-label">
              <el-input-number
                v-model="form.freightAmount"
                :precision="2"
                :min="0"
                class="ele-fluid"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col
            v-if="freightCalcMode !== 'manual_only'"
            :xs="24"
            :sm="14"
            :md="16"
          >
            <el-form-item :label-width="0" class="waybill-freight-actions">
              <el-button
                type="success"
                :loading="calcLoading"
                @click="calcFreight"
              >
                计算运费
              </el-button>
              <span v-if="calcResult" class="waybill-calc-hint">
                匹配: {{ calcResult.contractNo }} ({{ calcResult.matchLevel }})
              </span>
            </el-form-item>
          </el-col>
        </el-row>
      </template>
    </el-form>
    <template #footer>
      <div class="waybill-edit-drawer__footer">
        <el-button @click="updateVisible(false)">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          保存
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch, computed } from 'vue';
  import type { FormInstance, FormRules, CascaderProps } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { addWaybill, updateWaybill } from '@/api/waybill';
  import { calculateFreight } from '@/api/billing/contract';
  import { selectCustomers } from '@/api/partner/customer';
  import { listVehicleBrandOptions } from '@/api/basic-data/vehicle-brand';
  import { pageVehicleSeries } from '@/api/basic-data/vehicle-series';
  import { getRegionNavTree } from '@/api/basic-data/region';
  import { pageDealers } from '@/api/basic-data/dealer';
  import { listConfigsByGroup } from '@/api/system/config';
  import type { Waybill } from '@/api/waybill/model';
  import type { FreightCalcResult } from '@/api/billing/contract/model';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import type { VehicleBrandOption } from '@/api/basic-data/vehicle-brand/model';
  import type { VehicleSeries } from '@/api/basic-data/vehicle-series/model';
  import type { RegionNavNode } from '@/api/basic-data/region/model';
  import type { Dealer } from '@/api/basic-data/dealer/model';
  import { pinyinMatch } from '@/utils/pinyin-match';

  const props = defineProps<{
    visible: boolean;
    data: Waybill | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const calcLoading = ref(false);
  const calcResult = ref<FreightCalcResult | null>(null);
  const form = reactive<Waybill>({});

  const customerOptions = ref<CustomerSelectItem[]>([]);
  const brandOptions = ref<VehicleBrandOption[]>([]);
  const seriesOptions = ref<VehicleSeries[]>([]);
  const regionTree = ref<RegionNavNode[]>([]);
  const dealerOptions = ref<Dealer[]>([]);
  const selectedBrandId = ref<number | null>(null);
  const selectedDealerId = ref<number | null>(null);
  const originCodes = ref<string[]>([]);
  const destCodes = ref<string[]>([]);
  const freightCalcMode = ref('auto_preferred');

  const filterQ = reactive({
    customer: '',
    brand: '',
    series: '',
    dealer: ''
  });

  const customersShown = computed(() => {
    const q = filterQ.customer.trim();
    if (!q) return customerOptions.value;
    return customerOptions.value.filter((c) =>
      pinyinMatch(c.customerName ?? '', q)
    );
  });

  const brandsShown = computed(() => {
    const q = filterQ.brand.trim();
    if (!q) return brandOptions.value;
    return brandOptions.value.filter((b) =>
      pinyinMatch(b.brandNameCn ?? '', q)
    );
  });

  const seriesShown = computed(() => {
    const q = filterQ.series.trim();
    if (!q) return seriesOptions.value;
    return seriesOptions.value.filter((s) =>
      pinyinMatch(s.seriesName ?? '', q)
    );
  });

  const dealersShown = computed(() => {
    const q = filterQ.dealer.trim();
    if (!q) return dealerOptions.value;
    return dealerOptions.value.filter((d) =>
      pinyinMatch(d.dealerName ?? '', q)
    );
  });

  const setCustomerFilter = (q: string) => {
    filterQ.customer = q;
  };
  const setBrandFilter = (q: string) => {
    filterQ.brand = q;
  };
  const setSeriesFilter = (q: string) => {
    filterQ.series = q;
  };
  const setDealerFilter = (q: string) => {
    filterQ.dealer = q;
  };

  const regionCascaderProps: CascaderProps = {
    value: 'code',
    label: 'name',
    children: 'children',
    emitPath: true,
    checkStrictly: true
  };

  const rules = reactive<FormRules>({
    customerId: [{ required: true, message: '请选择客户', trigger: 'change' }],
    originCode: [
      { required: true, message: '请选择出发地', trigger: 'change' }
    ],
    destinationCode: [
      { required: true, message: '请选择目的地', trigger: 'change' }
    ],
    quantity: [{ required: true, message: '请输入台数', trigger: 'blur' }]
  });

  const loadBaseData = async () => {
    try {
      const [customers, brands, regions, dealerData, configs] =
        await Promise.all([
          selectCustomers().catch(() => []),
          listVehicleBrandOptions().catch(() => []),
          getRegionNavTree().catch(() => []),
          pageDealers({ page: 1, limit: 500 }).catch(() => ({
            list: [],
            count: 0
          })),
          listConfigsByGroup('waybill').catch(() => [])
        ]);
      customerOptions.value = customers ?? [];
      brandOptions.value = brands ?? [];
      regionTree.value = regions ?? [];
      dealerOptions.value = dealerData?.list ?? [];

      const modeConfig = (configs ?? []).find(
        (c: any) => c.configKey === 'waybill.freight_calc_mode'
      );
      if (modeConfig?.configValue) {
        freightCalcMode.value = modeConfig.configValue;
      }
    } catch (_) {
      /* ignore */
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
    calcResult.value = null;
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
    calcResult.value = null;
  };

  const onDestChange = (val: string[]) => {
    if (val && val.length) {
      form.destinationCode = val[val.length - 1];
      form.destination = findRegionName(val);
    } else {
      form.destinationCode = undefined;
      form.destination = undefined;
    }
    calcResult.value = null;
  };

  const onDealerChange = (dealerId: number | undefined) => {
    if (dealerId == null) {
      form.dealerName = undefined;
      form.dealerAddress = undefined;
      return;
    }
    const dealer = dealerOptions.value.find((d) => d.dealerId === dealerId);
    if (dealer) {
      form.dealerName = dealer.dealerName;
      form.dealerAddress = [dealer.province, dealer.city, dealer.addressDetail]
        .filter(Boolean)
        .join(' ');
    }
  };

  const onCustomerChange = () => {
    const customer = customerOptions.value.find(
      (c) => c.id === form.customerId
    );
    if (customer) {
      form.customerName = customer.customerName;
    }
    calcResult.value = null;
  };

  watch(
    () => props.visible,
    async (val) => {
      if (!val) return;
      filterQ.customer = '';
      filterQ.brand = '';
      filterQ.series = '';
      filterQ.dealer = '';
      calcResult.value = null;
      selectedBrandId.value = null;
      selectedDealerId.value = null;
      originCodes.value = [];
      destCodes.value = [];
      seriesOptions.value = [];

      await loadBaseData();

      if (props.data?.id) {
        Object.assign(form, props.data);
        if (props.data.originCode) {
          originCodes.value = [props.data.originCode];
        }
        if (props.data.destinationCode) {
          destCodes.value = [props.data.destinationCode];
        }
        const brand = brandOptions.value.find(
          (b) => b.brandNameCn === props.data?.vehicleBrand
        );
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
        }
        const dealer = dealerOptions.value.find(
          (d) => d.dealerName === props.data?.dealerName
        );
        if (dealer) {
          selectedDealerId.value = dealer.dealerId;
        }
      } else {
        Object.keys(form).forEach((k) => {
          (form as any)[k] = undefined;
        });
        form.quantity = 1;
      }
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const calcFreight = async () => {
    if (!form.customerId) {
      EleMessage.warning({ message: '请先选择客户', plain: true });
      return;
    }
    if (!form.originCode || !form.destinationCode) {
      EleMessage.warning({
        message: '请先选择出发地和目的地',
        plain: true
      });
      return;
    }
    calcLoading.value = true;
    try {
      const result = await calculateFreight({
        customerId: form.customerId,
        originCode: form.originCode,
        destinationCode: form.destinationCode,
        vehicleBrand: form.vehicleBrand,
        vehicleModel: form.vehicleModel
      });
      if (result) {
        calcResult.value = result;
        form.freightAmount =
          result.totalAmount ?? result.unitPrice * (form.quantity || 1);
        form.freightSource = 0;
        form.contractId = result.contractId;
        form.rateId = result.rateId;
        EleMessage.success({ message: '运费计算成功', plain: true });
      } else {
        calcResult.value = null;
        EleMessage.warning({
          message: '未匹配到运价，请手动填写运费',
          plain: true
        });
      }
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      calcLoading.value = false;
    }
  };

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        if (isEdit.value) {
          await updateWaybill(form);
        } else {
          await addWaybill(form);
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
  .waybill-edit-drawer__footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }

  .waybill-section-title {
    margin: 0 0 6px;
    padding-bottom: 4px;
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-regular);
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  .waybill-section-title:not(:first-child) {
    margin-top: 8px;
  }

  .waybill-edit-form--compact :deep(.el-form-item) {
    margin-bottom: 8px;
  }

  .waybill-item-tight-label :deep(.el-form-item__label) {
    padding-bottom: 2px;
    line-height: 1.2;
    font-size: 12px;
  }

  .waybill-freight-actions {
    margin-bottom: 8px;
  }

  .waybill-freight-actions :deep(.el-form-item__content) {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }

  .waybill-calc-hint {
    font-size: 12px;
    color: var(--el-color-success);
    line-height: 1.4;
  }

  .waybill-edit-drawer :deep(.el-drawer__header) {
    margin-bottom: 8px;
    padding-bottom: 12px;
  }

  .waybill-edit-drawer :deep(.el-drawer__body) {
    padding: 8px 16px 12px;
    overflow-y: auto;
  }

  .waybill-edit-drawer :deep(.el-drawer__footer) {
    padding: 10px 16px;
    border-top: 1px solid var(--el-border-color-lighter);
  }
</style>
