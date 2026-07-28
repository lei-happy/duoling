<template>
  <div class="waybill-edit-step waybill-edit-step--cargo">
    <div
      v-for="(row, idx) in cargoRows"
      :key="idx"
      class="waybill-cargo-card"
    >
      <div class="waybill-cargo-card__head">
        <span class="waybill-cargo-card__label">商品车 {{ idx + 1 }}</span>
        <el-button
          v-if="cargoRows.length > 1"
          type="danger"
          link
          size="small"
          @click="emit('remove', idx)"
        >
          删除
        </el-button>
      </div>

      <div class="waybill-cargo-card__main">
        <div class="waybill-cargo-card__thumb">
          <el-image
            v-if="rowImageSrc(row)"
            :src="rowImageSrc(row)"
            fit="cover"
            class="waybill-cargo-card__img"
            lazy
          >
            <template #error>
              <div class="waybill-cargo-card__placeholder">
                <el-icon :size="28"><Picture /></el-icon>
                <span>暂无图片</span>
              </div>
            </template>
          </el-image>
          <div v-else class="waybill-cargo-card__placeholder">
            <el-icon :size="28"><Picture /></el-icon>
            <span>{{ row.vehicleModel ? '暂无图片' : '选择车型后展示' }}</span>
          </div>
        </div>

        <div class="waybill-cargo-card__fields">
          <el-form-item class="waybill-cargo-field waybill-cargo-field--brand">
            <floating-label
              v-model="row.vehicleBrand"
              label="品牌"
              type="select"
              filterable
              :filter-method="setBrandFilter"
              clearable
              @change="() => emit('brand-change', row)"
            >
              <el-option
                v-for="b in brandsShown"
                :key="b.brandId"
                :label="b.brandNameCn"
                :value="b.brandNameCn"
              />
            </floating-label>
          </el-form-item>
          <el-form-item class="waybill-cargo-field waybill-cargo-field--model">
            <floating-label
              v-model="row.vehicleModel"
              label="车型"
              type="select"
              filterable
              :filter-method="setSeriesFilter"
              :disabled="!row.brandId"
              clearable
            >
              <el-option
                v-for="s in seriesShownForRow(row)"
                :key="s.seriesId"
                :label="s.seriesName"
                :value="s.seriesName"
              />
            </floating-label>
          </el-form-item>
          <el-form-item
            v-if="row.requireVin"
            class="waybill-cargo-field waybill-cargo-field--vin"
          >
            <floating-label
              label="VIN码"
              type="input"
              v-model.trim="row.vinStr"
              clearable
              :maxlength="50"
              show-word-limit
              @blur="emit('normalize-vin', row)"
            />
          </el-form-item>
          <el-form-item
            v-else
            class="waybill-cargo-field waybill-cargo-field--qty"
          >
            <floating-label
              label="台数"
              type="input"
              input-type="number"
              v-model="row.quantityStr"
              clearable
              @blur="emit('normalize-qty', row)"
            />
          </el-form-item>
        </div>
      </div>
    </div>

    <el-button
      type="primary"
      plain
      class="waybill-cargo-add"
      @click="emit('add')"
    >
      添加新车
    </el-button>
  </div>
</template>

<script lang="ts" setup>
  import { Picture } from '@element-plus/icons-vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import type { VehicleBrandOption } from '@/api/basic-data/vehicle-brand/model';
  import type { VehicleSeries } from '@/api/basic-data/vehicle-series/model';
  import type { CargoEditRow } from './waybill-edit-types';

  defineProps<{
    cargoRows: CargoEditRow[];
    brandsShown: VehicleBrandOption[];
    seriesShownForRow: (row: CargoEditRow) => VehicleSeries[];
    setBrandFilter: (q: string) => void;
    setSeriesFilter: (q: string) => void;
  }>();

  const emit = defineEmits<{
    (e: 'add'): void;
    (e: 'remove', idx: number): void;
    (e: 'brand-change', row: CargoEditRow): void;
    (e: 'normalize-vin', row: CargoEditRow): void;
    (e: 'normalize-qty', row: CargoEditRow): void;
  }>();

  function resolveMediaUrl(p?: string | null): string {
    const s = p?.trim();
    if (!s) return '';
    if (s.startsWith('http://') || s.startsWith('https://')) return s;
    return s.startsWith('/') ? s : `/${s}`;
  }

  function rowImageSrc(row: CargoEditRow): string {
    const model = row.vehicleModel?.trim();
    if (!model) return '';
    const series = row.seriesOptions.find((s) => s.seriesName === model);
    return resolveMediaUrl(series?.seriesImage);
  }
</script>

<style scoped>
  .waybill-cargo-card {
    margin-bottom: 12px;
    padding: 12px 14px 14px;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    background: var(--el-fill-color-blank);
    transition:
      border-color 0.15s ease,
      box-shadow 0.15s ease;
  }

  .waybill-cargo-card:hover {
    border-color: var(--el-border-color);
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  }

  .waybill-cargo-card__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
  }

  .waybill-cargo-card__label {
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .waybill-cargo-card__main {
    display: grid;
    grid-template-columns: 132px minmax(0, 1fr);
    gap: 14px;
    align-items: stretch;
  }

  .waybill-cargo-card__thumb {
    border-radius: 8px;
    overflow: hidden;
    background: var(--el-fill-color-light);
    min-height: 96px;
    align-self: stretch;
  }

  .waybill-cargo-card__img {
    width: 100%;
    height: 100%;
    min-height: 96px;
    display: block;
  }

  .waybill-cargo-card__placeholder {
    width: 100%;
    height: 100%;
    min-height: 96px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    color: var(--el-text-color-placeholder);
    font-size: 12px;
    line-height: 1.3;
    padding: 8px;
    text-align: center;
    box-sizing: border-box;
  }

  .waybill-cargo-card__fields {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px 12px;
    align-content: start;
    min-width: 0;
  }

  .waybill-cargo-field {
    margin-bottom: 0 !important;
    min-width: 0;
  }

  .waybill-cargo-field--vin,
  .waybill-cargo-field--qty {
    grid-column: 1 / -1;
  }

  .waybill-cargo-add {
    margin-top: 4px;
    width: 100%;
  }

  @media (max-width: 640px) {
    .waybill-cargo-card__main {
      grid-template-columns: 1fr;
    }

    .waybill-cargo-card__thumb,
    .waybill-cargo-card__img,
    .waybill-cargo-card__placeholder {
      min-height: 140px;
    }

    .waybill-cargo-card__fields {
      grid-template-columns: 1fr;
    }

    .waybill-cargo-field--vin,
    .waybill-cargo-field--qty {
      grid-column: auto;
    }
  }
</style>
