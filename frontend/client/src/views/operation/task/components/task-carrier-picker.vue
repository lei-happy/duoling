<template>
  <div class="carrier-picker">
    <el-radio-group
      v-model="local.carrierType"
      @change="onTypeChange"
      class="carrier-picker__radio"
    >
      <el-radio-button
        v-for="o in CARRIER_TYPE_OPTIONS"
        :key="o.value"
        :value="o.value"
      >
        {{ o.label }}
      </el-radio-button>
    </el-radio-group>

    <!-- A. 自有车 -->
    <template v-if="local.carrierType === 1">
      <el-form-item label="选择运力">
        <el-select
          v-model="local.capacityId"
          remote
          filterable
          clearable
          :remote-method="searchCapacities"
          placeholder="搜索司机/车牌"
          style="width: 100%"
          @change="onCapacityChange"
        >
          <el-option
            v-for="c in capacities"
            :key="c.id"
            :value="c.id!"
            :label="`${c.driverName} / ${c.plateNumber}`"
          >
            <span>{{ c.driverName }}</span>
            <span class="ele-text-secondary" style="margin-left: 8px">
              {{ c.plateNumber }} · {{ c.driverPhone }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="主驾姓名">
            <el-input v-model="local.mainDriverName" placeholder="可手动覆盖" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="主驾电话">
            <el-input v-model="local.mainDriverPhone" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="车牌号">
            <el-input v-model="local.plateNumber" />
          </el-form-item>
        </el-col>
      </el-row>
    </template>

    <!-- B. 承运商 -->
    <template v-if="local.carrierType === 2">
      <el-form-item label="选择承运商">
        <el-select
          v-model="local.carrierId"
          remote
          filterable
          clearable
          :remote-method="searchCarriers"
          placeholder="搜索承运商名称"
          style="width: 100%"
          @change="onCarrierChange"
        >
          <el-option
            v-for="c in carriers"
            :key="c.id"
            :value="c.id!"
            :label="c.carrierName"
          >
            <span>{{ c.carrierName }}</span>
            <span
              v-if="c.shortName"
              class="ele-text-secondary"
              style="margin-left: 8px"
            >
              {{ c.shortName }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="承运商简称">
            <el-input v-model="local.carrierShortName" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="实际车牌（可选）">
            <el-input v-model="local.plateNumber" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="实际驾驶员（可选）">
            <el-input v-model="local.mainDriverName" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="驾驶员电话（可选）">
            <el-input v-model="local.mainDriverPhone" />
          </el-form-item>
        </el-col>
      </el-row>
    </template>

    <!-- C. 社会运力 -->
    <template v-if="local.carrierType === 3">
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="司机姓名" required>
            <el-input v-model="local.mainDriverName" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="司机电话" required>
            <el-input v-model="local.mainDriverPhone" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="身份证号">
            <el-input v-model="local.mainDriverIdCard" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="车牌号" required>
            <el-input v-model="local.plateNumber" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="挂车牌号">
            <el-input v-model="local.trailerPlateNumber" />
          </el-form-item>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script lang="ts" setup>
  import { reactive, ref, watch } from 'vue';
  import type { TaskCarrierInfo } from '@/api/operation/task/model';
  import { pageCapacities } from '@/api/capacity/self_capacity/list';
  import type { Capacity } from '@/api/capacity/self_capacity/list/model';
  import { selectCarriers } from '@/api/partner/carrier';
  import type { CarrierSelectItem } from '@/api/partner/carrier/model';
  import { CARRIER_TYPE_OPTIONS } from '../status-config';

  const props = defineProps<{
    modelValue?: TaskCarrierInfo;
  }>();
  const emit = defineEmits<{
    (e: 'update:modelValue', value: TaskCarrierInfo): void;
  }>();

  const local = reactive<TaskCarrierInfo>({
    carrierType: 1,
    capacityId: undefined,
    carrierId: undefined,
    mainDriverName: '',
    mainDriverPhone: '',
    mainDriverIdCard: '',
    plateNumber: '',
    trailerPlateNumber: '',
    carrierName: '',
    carrierShortName: '',
    ...(props.modelValue || {})
  });

  watch(
    () => props.modelValue,
    (v) => {
      if (!v) return;
      Object.assign(local, v);
    },
    { deep: true }
  );

  watch(
    () => ({ ...local }),
    (v) => emit('update:modelValue', v),
    { deep: true }
  );

  const capacities = ref<Capacity[]>([]);
  const carriers = ref<CarrierSelectItem[]>([]);

  const searchCapacities = async (kw: string) => {
    try {
      const res = await pageCapacities({
        keyword: kw,
        page: 1,
        limit: 20
      });
      capacities.value = res?.list || [];
    } catch {
      capacities.value = [];
    }
  };

  const searchCarriers = async (kw: string) => {
    try {
      carriers.value = await selectCarriers(kw);
    } catch {
      carriers.value = [];
    }
  };

  const onTypeChange = () => {
    // 切换类型时清理快照（避免脏数据残留）
    local.capacityId = undefined;
    local.carrierId = undefined;
    local.mainDriverName = '';
    local.mainDriverPhone = '';
    local.mainDriverIdCard = '';
    local.plateNumber = '';
    local.trailerPlateNumber = '';
    local.carrierName = '';
    local.carrierShortName = '';
  };

  const onCapacityChange = (id: number) => {
    const c = capacities.value.find((x) => x.id === id);
    if (c) {
      local.mainDriverName = c.driverName;
      local.mainDriverPhone = c.driverPhone;
      local.plateNumber = c.plateNumber;
      local.trailerPlateNumber = c.trailerPlateNumber || '';
    }
  };

  const onCarrierChange = (id: number) => {
    const c = carriers.value.find((x) => x.id === id);
    if (c) {
      local.carrierName = c.carrierName;
      local.carrierShortName = c.shortName || '';
    }
  };

  /** 触发一次初始搜索（弹窗打开时调用） */
  const init = () => {
    if (local.carrierType === 1 && capacities.value.length === 0) {
      searchCapacities('');
    }
    if (local.carrierType === 2 && carriers.value.length === 0) {
      searchCarriers('');
    }
  };
  defineExpose({ init });
</script>

<style lang="scss" scoped>
  .carrier-picker {
    &__radio {
      margin-bottom: 12px;
    }
  }
</style>
