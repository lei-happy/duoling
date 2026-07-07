<template>
  <el-dialog
    title="承运运费试算"
    :model-value="visible"
    width="720px"
    align-center
    draggable
    :close-on-click-modal="false"
    class="freight-preview-dialog"
    @update:model-value="updateVisible"
  >
    <el-form label-width="0" @submit.prevent="">
      <el-row :gutter="16">
        <el-col :span="24">
          <div class="fp-carrier">
            <span class="fp-carrier__k">承运商</span>
            <span class="fp-carrier__v">{{ carrierName || '—' }}</span>
          </div>
        </el-col>
        <el-col :span="12">
          <el-form-item>
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
          <el-form-item>
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
      </el-row>

      <el-divider content-position="left" class="fp-divider"
        >车型明细</el-divider
      >
      <div v-for="(v, idx) in vehicles" :key="idx" class="fp-vehicle-row">
        <floating-label
          v-model="v.vehicleBrand"
          class="fp-vehicle-row__brand"
          label="品牌（选填）"
          type="select"
          filterable
          clearable
          @change="(name: string) => onBrandChange(v, name)"
        >
          <el-option
            v-for="b in brandOptions"
            :key="b.brandId"
            :label="b.brandNameCn"
            :value="b.brandNameCn"
          />
        </floating-label>
        <floating-label
          v-model="v.vehicleModel"
          class="fp-vehicle-row__model"
          label="车型（选填）"
          type="select"
          filterable
          clearable
          :disabled="!v._seriesOptions || !v._seriesOptions.length"
          @change="(name: string) => onSeriesChange(v, name)"
        >
          <el-option
            v-for="s in v._seriesOptions || []"
            :key="s.seriesId"
            :label="s.seriesName"
            :value="s.seriesName"
          />
        </floating-label>
        <el-input-number
          v-model="v.quantity"
          class="fp-vehicle-row__qty"
          :min="1"
          :step="1"
          controls-position="right"
        />
        <el-button
          v-if="vehicles.length > 1"
          text
          type="danger"
          class="fp-vehicle-row__del"
          @click="removeVehicle(idx)"
        >
          删除
        </el-button>
      </div>
      <el-button text type="primary" @click="addVehicle">+ 添加车型</el-button>
    </el-form>

    <div v-if="result" class="fp-result">
      <el-alert
        v-if="result.calcStatus !== 'success'"
        :title="result.errorMessage || '未匹配到承运价规则'"
        type="warning"
        :closable="false"
        show-icon
      />
      <template v-else>
        <div class="fp-result__total">
          <span class="fp-result__total-k">试算合计</span>
          <span class="fp-result__total-v">
            ¥ {{ (result.totalAmount ?? 0).toFixed(2) }}
          </span>
        </div>
        <el-table :data="result.items || []" border size="small" stripe>
          <el-table-column
            label="品牌/车型"
            min-width="150"
            :formatter="(row) => formatBrandModel(row)"
          />
          <el-table-column
            prop="quantity"
            label="台数"
            width="70"
            align="center"
          />
          <el-table-column label="计费模式" width="90" align="center">
            <template #default="{ row }">
              {{ billingModeText(row.billingMode) }}
            </template>
          </el-table-column>
          <el-table-column label="单价" width="110" align="right">
            <template #default="{ row }">
              {{
                row.unitPrice != null ? Number(row.unitPrice).toFixed(2) : '—'
              }}
            </template>
          </el-table-column>
          <el-table-column label="金额" width="110" align="right">
            <template #default="{ row }">
              {{ (row.amount ?? 0).toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90" align="center">
            <template #default="{ row }">
              <el-tag
                v-if="row.calcStatus === 'success'"
                type="success"
                size="small"
              >
                已匹配
              </el-tag>
              <el-tag v-else type="warning" size="small">
                {{ row.errorMessage || '未匹配' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </div>

    <template #footer>
      <el-button @click="updateVisible(false)">关闭</el-button>
      <el-button type="primary" :loading="loading" @click="runPreview">
        试算
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import type { CascaderProps } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { previewCarrierFreight } from '@/api/billing/carrier-contract';
  import type {
    CarrierFreightItem,
    CarrierFreightResult
  } from '@/api/billing/carrier-contract/model';
  import { listVehicleBrandOptions } from '@/api/basic-data/vehicle-brand';
  import { pageVehicleSeries } from '@/api/basic-data/vehicle-series';
  import { getRegionNavTree } from '@/api/basic-data/region';
  import type { VehicleBrandOption } from '@/api/basic-data/vehicle-brand/model';
  import type { VehicleSeries } from '@/api/basic-data/vehicle-series/model';
  import type { RegionNavNode } from '@/api/basic-data/region/model';
  import { findLeafRegionByCodePath } from '@/utils/region-nav-tree';

  interface VehicleRow {
    vehicleBrand?: string | null;
    vehicleModel?: string | null;
    brandId?: number | null;
    seriesId?: number | null;
    quantity: number;
    _seriesOptions?: VehicleSeries[];
  }

  const props = defineProps<{
    visible: boolean;
    carrierId?: number;
    carrierName?: string;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
  }>();

  const loading = ref(false);
  const result = ref<CarrierFreightResult | null>(null);
  const regionTree = ref<RegionNavNode[]>([]);
  const brandOptions = ref<VehicleBrandOption[]>([]);
  const originCodes = ref<string[]>([]);
  const destCodes = ref<string[]>([]);
  const originRegionId = ref<number | null>(null);
  const destinationRegionId = ref<number | null>(null);
  const vehicles = ref<VehicleRow[]>([{ quantity: 1 }]);

  const regionCascaderProps: CascaderProps = {
    value: 'code',
    label: 'name',
    children: 'children',
    emitPath: true,
    checkStrictly: true
  };

  const billingModeText = (m?: number | null) => {
    if (m === 1) return '单公里';
    if (m === 2) return '整单价';
    return '台单价';
  };

  const formatBrandModel = (row: CarrierFreightItem) => {
    const b = row.vehicleBrand?.trim();
    const m = row.vehicleModel?.trim();
    if (!b && !m) return '不限';
    return `${b || '不限'}/${m || '不限'}`;
  };

  const loadBaseData = async () => {
    const [regions, brands] = await Promise.all([
      getRegionNavTree().catch(() => []),
      listVehicleBrandOptions().catch(() => [])
    ]);
    regionTree.value = regions ?? [];
    brandOptions.value = brands ?? [];
  };

  const onOriginChange = (val?: string[]) => {
    if (val && val.length) {
      const leaf = findLeafRegionByCodePath(regionTree.value, val);
      originRegionId.value = leaf?.regionId ?? null;
    } else {
      originRegionId.value = null;
    }
  };

  const onDestChange = (val?: string[]) => {
    if (val && val.length) {
      const leaf = findLeafRegionByCodePath(regionTree.value, val);
      destinationRegionId.value = leaf?.regionId ?? null;
    } else {
      destinationRegionId.value = null;
    }
  };

  const onBrandChange = async (row: VehicleRow, brandName?: string | null) => {
    row.vehicleModel = null;
    row.seriesId = null;
    row._seriesOptions = [];
    const name = brandName?.trim();
    const brand = name
      ? brandOptions.value.find((b) => b.brandNameCn === name)
      : undefined;
    if (brand) {
      row.brandId = brand.brandId;
      try {
        const data = await pageVehicleSeries({
          brandId: brand.brandId,
          page: 1,
          limit: 200
        });
        row._seriesOptions = data?.list ?? [];
      } catch (_) {
        row._seriesOptions = [];
      }
    } else {
      row.brandId = null;
      row.vehicleBrand = null;
    }
  };

  const onSeriesChange = (row: VehicleRow, seriesName?: string) => {
    if (!seriesName) {
      row.seriesId = null;
      row.vehicleModel = null;
      return;
    }
    const item = (row._seriesOptions || []).find(
      (s) => s.seriesName === seriesName
    );
    row.seriesId = item ? item.seriesId : null;
  };

  const addVehicle = () => {
    vehicles.value.push({ quantity: 1 });
  };

  const removeVehicle = (idx: number) => {
    vehicles.value.splice(idx, 1);
  };

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const runPreview = async () => {
    if (!props.carrierId) {
      EleMessage.warning({ message: '缺少承运商信息', plain: true });
      return;
    }
    if (!originRegionId.value || !destinationRegionId.value) {
      EleMessage.warning({ message: '请选择出发地和目的地', plain: true });
      return;
    }
    const payloadVehicles = vehicles.value.map((v) => ({
      brandId: v.brandId ?? null,
      seriesId: v.seriesId ?? null,
      vehicleBrand: v.vehicleBrand ?? null,
      vehicleModel: v.vehicleModel ?? null,
      quantity: v.quantity || 0
    }));
    const totalQuantity = payloadVehicles.reduce(
      (s, v) => s + (v.quantity || 0),
      0
    );
    loading.value = true;
    try {
      result.value =
        (await previewCarrierFreight({
          carrierId: props.carrierId,
          originRegionId: originRegionId.value,
          destinationRegionId: destinationRegionId.value,
          totalQuantity,
          vehicles: payloadVehicles
        })) ?? null;
      if (!result.value) {
        EleMessage.info({ message: '未匹配到承运价规则', plain: true });
      }
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      loading.value = false;
    }
  };

  watch(
    () => props.visible,
    async (val) => {
      if (!val) return;
      result.value = null;
      originCodes.value = [];
      destCodes.value = [];
      originRegionId.value = null;
      destinationRegionId.value = null;
      vehicles.value = [{ quantity: 1 }];
      await loadBaseData();
    }
  );
</script>

<style scoped lang="scss">
  .fp-carrier {
    display: inline-flex;
    align-items: baseline;
    gap: 6px;
    margin-bottom: 14px;
    padding: 6px 12px;
    border-radius: 8px;
    background: var(--el-fill-color-light);
    font-size: 13px;
  }

  .fp-carrier__k {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .fp-carrier__v {
    color: var(--el-text-color-primary);
    font-weight: 500;
  }

  .fp-divider {
    margin: 6px 0 18px;
  }

  .fp-vehicle-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
  }

  .fp-vehicle-row__brand,
  .fp-vehicle-row__model {
    flex: 1;
    min-width: 0;
  }

  .fp-vehicle-row__qty {
    width: 120px;
    flex: 0 0 120px;
  }

  .fp-vehicle-row__del {
    flex: 0 0 auto;
  }

  .fp-result {
    margin-top: 18px;
  }

  .fp-result__total {
    display: flex;
    align-items: baseline;
    justify-content: flex-end;
    gap: 10px;
    margin-bottom: 12px;
  }

  .fp-result__total-k {
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .fp-result__total-v {
    color: var(--el-color-danger);
    font-size: 20px;
    font-weight: 600;
  }

  .freight-preview-dialog
    :deep(.floating-label-wrapper.is-focused .floating-label),
  .freight-preview-dialog
    :deep(.floating-label-wrapper.has-value .floating-label) {
    color: var(--el-color-primary);
  }
</style>
