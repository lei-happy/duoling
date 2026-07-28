<template>
  <div class="waybill-edit-step waybill-edit-step--receive">
    <div class="waybill-receive-layout">
      <div class="waybill-receive-layout__form">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12">
            <el-form-item prop="dealerName">
              <floating-label
                v-model="selectedDealerIdProxy"
                label="收车门店"
                type="select"
                filterable
                :filter-method="setDealerFilter"
                clearable
                @change="emit('dealer-change', $event)"
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
          <el-col :xs="24" :sm="12">
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
          <el-col :xs="24" :sm="12">
            <el-form-item prop="dealerContact">
              <floating-label
                label="联系人姓名"
                type="input"
                v-model.trim="form.dealerContact"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item prop="dealerPhone">
              <floating-label
                label="联系电话"
                type="input"
                v-model.trim="form.dealerPhone"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <div class="waybill-receive-layout__map">
        <div class="waybill-receive-layout__map-label">门店位置</div>
        <dealer-location-map
          :longitude="dealerLongitude"
          :latitude="dealerLatitude"
          :visible="mapVisible"
          :has-dealer="!!selectedDealerId"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import type { Waybill } from '@/api/waybill/model';
  import type { Dealer } from '@/api/basic-data/dealer/model';
  import DealerLocationMap from './dealer-location-map.vue';

  const props = defineProps<{
    form: Waybill;
    selectedDealerId: number | null;
    dealersShown: Dealer[];
    setDealerFilter: (q: string) => void;
    dealerLongitude?: number | null;
    dealerLatitude?: number | null;
    mapVisible?: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'update:selectedDealerId', v: number | null): void;
    (e: 'dealer-change', dealerId: number | undefined): void;
  }>();

  const selectedDealerIdProxy = computed({
    get: () => props.selectedDealerId,
    set: (v: number | null) => emit('update:selectedDealerId', v)
  });
</script>

<style scoped>
  .waybill-receive-layout {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .waybill-receive-layout__map {
    min-width: 0;
    margin-top: 4px;
  }

  .waybill-receive-layout__map-label {
    margin-bottom: 8px;
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    line-height: 1.3;
  }

  .waybill-receive-layout__map :deep(.dealer-location-map) {
    height: min(360px, calc(100vh - 420px));
    min-height: 280px;
  }
</style>
