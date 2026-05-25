<template>
  <div class="carrier-picker">
    <div
      class="carrier-picker__types"
      :class="{ 'carrier-picker__types--two': carrierTypeOptions.length === 2 }"
    >
      <button
        v-for="o in carrierTypeOptions"
        :key="o.value"
        type="button"
        class="carrier-picker__type-card"
        :class="{ 'is-active': local.carrierType === o.value }"
        :disabled="lockType"
        @click="selectCarrierType(o.value)"
      >
        <span class="carrier-picker__type-name">{{ o.label }}</span>
        <span class="carrier-picker__type-desc">{{
          CARRIER_TYPE_INTRO[o.value] || ''
        }}</span>
      </button>
    </div>

    <!-- A. 自有车 -->
    <template v-if="local.carrierType === 1">
      <el-alert
        v-if="simpleMode"
        type="info"
        :closable="false"
        class="carrier-picker__hint"
        title="自有车任务进入「待派车」后，由调度员在派车环节选择具体运力（司机/车牌），此处无需指定。"
      />
      <template v-else>
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
    </template>

    <!-- B. 承运商 -->
    <template v-if="local.carrierType === 2">
      <el-form-item label="选择承运商" :required="simpleMode">
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
            :label="carrierOptionLabel(c)"
          />
        </el-select>
      </el-form-item>
      <el-alert
        v-if="simpleMode"
        type="info"
        :closable="false"
        class="carrier-picker__hint"
        title="选定承运商后进入「待派车」，具体运力可在派车环节再绑定。"
      />
      <template v-else>
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
    </template>

    <!-- C. 社会运力 -->
    <template v-if="local.carrierType === 3">
      <template v-if="simpleMode">
        <el-form-item label="选择运力">
          <el-select
            v-model="local.socialDriverId"
            disabled
            placeholder="将从社会运力池选择（开发中）"
            style="width: 100%"
          />
        </el-form-item>
        <el-empty
          description="社会运力池功能开发中，暂无法选择具体运力"
          :image-size="72"
          class="carrier-picker__social-placeholder"
        />
      </template>
      <template v-else>
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
    </template>
  </div>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import type { TaskCarrierInfo } from '@/api/operation/task/model';
  import { pageCapacities } from '@/api/capacity/self-capacity/list';
  import type { Capacity } from '@/api/capacity/self-capacity/list/model';
  import { selectCarriers } from '@/api/partner/carrier';
  import type { CarrierSelectItem } from '@/api/partner/carrier/model';
  import { CARRIER_TYPE_INTRO, CARRIER_TYPE_OPTIONS } from '../status-config';

  const props = withDefaults(
    defineProps<{
      modelValue?: TaskCarrierInfo;
      /**
       * 简化模式：用于「待分配」阶段确认承运方式 —— 自有车任务无需选择具体运力，
       * 承运商仅需选定承运商；切换 carrier_type 仍可正常使用。
       */
      simpleMode?: boolean;
      /** 锁定承运方式：派车环节使用，禁止重新选择 carrierType。 */
      lockType?: boolean;
      /** 可选承运方式（默认全部）；批量分配时传 [1, 2] 排除社会运力。 */
      allowedCarrierTypes?: number[];
    }>(),
    {
      simpleMode: false,
      lockType: false
    }
  );
  const emit = defineEmits<{
    (e: 'update:modelValue', value: TaskCarrierInfo): void;
  }>();

  const carrierTypeOptions = computed(() => {
    const allowed = props.allowedCarrierTypes;
    if (!allowed?.length) return CARRIER_TYPE_OPTIONS;
    return CARRIER_TYPE_OPTIONS.filter((o) => allowed.includes(o.value));
  });

  const ensureAllowedCarrierType = () => {
    const allowed = props.allowedCarrierTypes;
    if (!allowed?.length) return;
    if (!allowed.includes(local.carrierType)) {
      local.carrierType = allowed[0]!;
      onTypeChange();
    }
  };

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
    () => props.allowedCarrierTypes,
    () => ensureAllowedCarrierType(),
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

  const carrierOptionLabel = (c: CarrierSelectItem) =>
    c.shortName ? `${c.carrierName}（${c.shortName}）` : c.carrierName;

  const searchCarriers = async (kw: string) => {
    try {
      carriers.value = await selectCarriers(kw);
    } catch {
      carriers.value = [];
    }
  };

  const onTypeChange = () => {
    local.capacityId = undefined;
    local.carrierId = undefined;
    local.socialDriverId = undefined;
    local.mainDriverName = '';
    local.mainDriverPhone = '';
    local.mainDriverIdCard = '';
    local.plateNumber = '';
    local.trailerPlateNumber = '';
    local.carrierName = '';
    local.carrierShortName = '';
  };

  const selectCarrierType = (value: number) => {
    if (props.lockType || local.carrierType === value) return;
    local.carrierType = value;
    onTypeChange();
    if (value === 2 && carriers.value.length === 0) {
      searchCarriers('');
    }
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
    ensureAllowedCarrierType();
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
    &__types {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 16px;

      &--two {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    &__type-card {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 6px;
      min-height: 88px;
      padding: 12px 14px;
      border: 1px solid var(--el-border-color);
      border-radius: 8px;
      background: var(--el-fill-color-blank);
      text-align: left;
      cursor: pointer;
      transition:
        border-color 0.2s,
        background-color 0.2s,
        box-shadow 0.2s;

      &:hover:not(:disabled) {
        border-color: var(--el-color-primary-light-5);
        background: var(--el-color-primary-light-9);
      }

      &.is-active {
        border-color: var(--el-color-primary);
        background: var(--el-color-primary-light-9);
        box-shadow: inset 0 0 0 1px var(--el-color-primary);
      }

      &:disabled {
        cursor: not-allowed;
        opacity: 0.72;
      }
    }

    &__type-name {
      font-size: 15px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      line-height: 1.3;
    }

    &__type-desc {
      font-size: 12px;
      line-height: 1.5;
      color: var(--el-text-color-secondary);
    }

    &__hint {
      margin-bottom: 0;
    }

    &__social-placeholder {
      padding: 8px 0 0;

      :deep(.el-empty__description) {
        margin-top: 8px;
        font-size: 13px;
      }
    }
  }
</style>
