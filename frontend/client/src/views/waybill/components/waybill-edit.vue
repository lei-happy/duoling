<template>
  <el-dialog
    :title="isEdit ? '编辑运单' : '新增运单'"
    :model-value="visible"
    @update:model-value="updateVisible"
    width="800px"
    draggable
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="110px"
      @submit.prevent=""
    >
      <el-divider content-position="left">基本信息</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="运单编号">
            <el-input
              v-model="form.waybillNo"
              placeholder="留空自动生成"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="客户" prop="customerId">
            <el-select
              v-model="form.customerId"
              placeholder="请选择客户"
              filterable
              style="width: 100%"
              @change="onCustomerChange"
            >
              <el-option
                v-for="item in customerOptions"
                :key="item.id"
                :label="item.customerName"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="计划下达时间">
            <el-date-picker
              v-model="form.planIssueTime"
              type="datetime"
              value-format="YYYY-MM-DD HH:mm:ss"
              placeholder="请选择时间"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">运输信息</el-divider>
      <el-row :gutter="16">
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
        <el-col :span="12">
          <el-form-item label="商品车品牌" prop="vehicleBrand">
            <el-select
              v-model="form.vehicleBrand"
              placeholder="请选择品牌"
              filterable
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
              placeholder="请选择车型"
              filterable
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
        <el-col :span="12">
          <el-form-item label="台数" prop="quantity">
            <el-input-number
              v-model="form.quantity"
              :min="1"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">收车门店</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="门店名称">
            <el-select
              v-model="selectedDealerId"
              placeholder="请选择经销商门店"
              filterable
              style="width: 100%"
              @change="onDealerChange"
            >
              <el-option
                v-for="d in dealerOptions"
                :key="d.dealerId"
                :label="d.dealerName"
                :value="d.dealerId"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系人">
            <el-input
              v-model="form.dealerContact"
              placeholder="请输入联系人"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="电话">
            <el-input
              v-model="form.dealerPhone"
              placeholder="请输入电话"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="地址">
            <el-input
              v-model="form.dealerAddress"
              placeholder="请输入地址"
              disabled
            />
          </el-form-item>
        </el-col>
      </el-row>

      <template v-if="freightCalcMode !== 'auto_required'">
        <el-divider content-position="left">运费信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="运费金额">
              <el-input-number
                v-model="form.freightAmount"
                :precision="2"
                :min="0"
                placeholder="元"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="freightCalcMode !== 'manual_only'">
            <el-form-item>
              <el-button
                type="success"
                :loading="calcLoading"
                @click="calcFreight"
              >
                计算运费
              </el-button>
              <span
                v-if="calcResult"
                style="margin-left: 8px; color: #67c23a"
              >
                匹配: {{ calcResult.contractNo }} ({{ calcResult.matchLevel }})
              </span>
            </el-form-item>
          </el-col>
        </el-row>
      </template>
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

  const regionCascaderProps: CascaderProps = {
    value: 'code',
    label: 'name',
    children: 'children',
    emitPath: true,
    checkStrictly: true
  };

  const rules = reactive<FormRules>({
    customerId: [
      { required: true, message: '请选择客户', trigger: 'change' }
    ],
    originCode: [
      { required: true, message: '请选择出发地', trigger: 'change' }
    ],
    destinationCode: [
      { required: true, message: '请选择目的地', trigger: 'change' }
    ],
    quantity: [
      { required: true, message: '请输入台数', trigger: 'blur' }
    ]
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

  const onDealerChange = (dealerId: number) => {
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
    (val) => {
      if (val) {
        loadBaseData();
        calcResult.value = null;
        selectedBrandId.value = null;
        selectedDealerId.value = null;
        originCodes.value = [];
        destCodes.value = [];
        if (props.data) {
          Object.assign(form, props.data);
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
        }
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
        form.freightAmount = result.totalAmount ?? result.unitPrice * (form.quantity || 1);
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
