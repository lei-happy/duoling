<!--
  调度工作台 - 任务池筛选栏
  ==========================

  - pending-dispatch：双行栅格 + 浮动标签，布局对齐运单列表 waybill-pool-filter
  - default：单行关键字筛选
-->
<template>
  <ele-card search-form class="wb-filter-card">
    <el-form
      class="wb-filter"
      label-width="0"
      @keyup.enter="emitSearch"
      @submit.prevent=""
    >
      <template v-if="preset === 'pending-dispatch'">
        <el-row :gutter="10" class="wb-filter__row">
          <el-col :lg="6" :md="6" :sm="12" :xs="24">
            <floating-label
              label="请输入任务单号/运单号/任务名称"
              type="input"
              v-model.trim="form.keyword"
              clearable
            />
          </el-col>
          <el-col :lg="6" :md="6" :sm="12" :xs="24">
            <floating-label
              label="请输入出发地"
              type="input"
              v-model.trim="form.originKeyword"
              clearable
            />
          </el-col>
          <el-col :lg="6" :md="6" :sm="12" :xs="24">
            <floating-label
              label="请输入目的地"
              type="input"
              v-model.trim="form.destinationKeyword"
              clearable
            />
          </el-col>
          <el-col :lg="6" :md="6" :sm="12" :xs="24">
            <floating-label
              v-model="form.carrierType"
              label="请选择承运方式"
              type="select"
              clearable
            >
              <el-option
                v-for="o in CARRIER_TYPE_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </floating-label>
          </el-col>
        </el-row>
        <el-row :gutter="10" class="wb-filter__row wb-filter__row--second">
          <el-col
            v-if="showCarrierFilter"
            :lg="fieldCol.lg"
            :md="fieldCol.md"
            :sm="fieldCol.sm"
            :xs="fieldCol.xs"
          >
            <floating-label
              v-model="form.carrierId"
              label="请选择承运商"
              type="select"
              filterable
              remote
              clearable
              :remote-method="searchCarriers"
            >
              <el-option
                v-for="c in carrierOptions"
                :key="c.id"
                :value="c.id"
                :label="c.name"
              />
            </floating-label>
          </el-col>
          <el-col
            :lg="fieldCol.lg"
            :md="fieldCol.md"
            :sm="fieldCol.sm"
            :xs="fieldCol.xs"
          >
            <floating-label
              v-model="form.createdAtRange"
              label="请选择制单时间"
              type="date"
              date-type="daterange"
              value-format="YYYY-MM-DD"
              format="YYYY-MM-DD"
              unlink-panels
              start-placeholder="开始"
              end-placeholder="结束"
            />
          </el-col>
          <el-col
            :lg="actionsCol.lg"
            :md="actionsCol.md"
            :sm="actionsCol.sm"
            :xs="actionsCol.xs"
            class="wb-filter__col-actions"
          >
            <el-form-item label-width="0px">
              <btn-items
                :wrap="false"
                :items="[
                  { preset: 'search', onClick: () => emitSearch() },
                  { preset: 'reset', onClick: () => onReset() }
                ]"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </template>
      <el-row v-else :gutter="10" class="wb-filter__row">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入任务单号/司机/车牌/承运商"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col
          :lg="actionsCol.lg"
          :md="actionsCol.md"
          :sm="actionsCol.sm"
          :xs="actionsCol.xs"
          class="wb-filter__col-actions"
        >
          <el-form-item label-width="0px">
            <btn-items
              :wrap="false"
              :items="[
                { preset: 'search', onClick: () => emitSearch() },
                { preset: 'reset', onClick: () => onReset() }
              ]"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref, watch } from 'vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { getLast3DaysDateRange } from '@/utils/date-util';
  import { selectCarriers } from '@/api/partner/carrier';
  import type { CarrierSelectItem } from '@/api/partner/carrier/model';
  import type { TaskParam } from '@/api/operation/task/model';
  import { CARRIER_TYPE_OPTIONS } from '../../task/status-config';
  import type { WorkbenchToolbarPreset } from '../workbench-pool-registry';

  const props = defineProps<{
    preset: WorkbenchToolbarPreset;
    poolKey: string;
  }>();

  const emit = defineEmits<{
    (e: 'search', where: Partial<TaskParam>): void;
  }>();

  type FilterForm = {
    keyword: string;
    originKeyword: string;
    destinationKeyword: string;
    carrierType: number | undefined;
    carrierId: number | undefined;
    createdAtRange: [string, string] | null;
  };

  const buildInitial = (): FilterForm => ({
    keyword: '',
    originKeyword: '',
    destinationKeyword: '',
    carrierType: void 0,
    carrierId: void 0,
    createdAtRange:
      props.preset === 'pending-dispatch'
        ? ([...getLast3DaysDateRange()] as [string, string])
        : null
  });

  const [form, resetFields] = useFormData<FilterForm>(buildInitial());

  const fieldCol = { lg: 6, md: 6, sm: 12, xs: 24 };
  const actionsCol = { lg: 4, md: 6, sm: 12, xs: 24 };

  const showCarrierFilter = computed(
    () => form.carrierType === 2 || props.poolKey === 'pending-load'
  );

  const carrierOptions = ref<Array<{ id: number; name: string }>>([]);

  const searchCarriers = async (kw: string) => {
    try {
      const res: CarrierSelectItem[] = await selectCarriers(kw);
      carrierOptions.value = (res || []).map((c) => ({
        id: c.id,
        name: c.shortName ? `${c.shortName} · ${c.carrierName}` : c.carrierName
      }));
    } catch {
      carrierOptions.value = [];
    }
  };

  watch(
    () => form.carrierType,
    (v) => {
      if (v !== 2) {
        form.carrierId = void 0;
      }
    }
  );

  const buildWhere = (): Partial<TaskParam> => {
    const payload: Partial<TaskParam> = {};
    const kw = form.keyword.trim();
    if (kw) payload.keyword = kw;

    if (props.preset !== 'pending-dispatch') {
      return payload;
    }

    const origin = form.originKeyword.trim();
    const dest = form.destinationKeyword.trim();
    if (origin) payload.originKeyword = origin;
    if (dest) payload.destinationKeyword = dest;
    if (form.carrierType != null) payload.carrierType = form.carrierType;
    if (showCarrierFilter.value && form.carrierId != null) {
      payload.carrierId = form.carrierId;
    }
    const range = form.createdAtRange;
    if (Array.isArray(range) && range.length === 2 && range[0] && range[1]) {
      payload.createdAtStart = range[0];
      payload.createdAtEnd = range[1];
    }
    return payload;
  };

  const emitSearch = () => emit('search', buildWhere());

  const onReset = () => {
    resetFields();
    if (props.preset === 'pending-dispatch') {
      form.createdAtRange = [...getLast3DaysDateRange()] as [string, string];
    }
    emitSearch();
  };

  onMounted(() => {
    emitSearch();
  });
</script>

<style scoped>
  .wb-filter__row {
    row-gap: 12px;
  }

  .wb-filter__row--second {
    margin-top: 12px;
    padding-top: 2px;
  }

  .wb-filter__col-actions :deep(.el-form-item) {
    margin-bottom: 0;
    display: flex;
    justify-content: flex-start;
  }

  .wb-filter__col-actions :deep(.el-form-item__content) {
    justify-content: flex-start;
    flex-wrap: nowrap;
  }
</style>

<style>
  .wb-filter-card.wb-filter-card {
    padding-bottom: 6px;
  }

  .wb-filter .floating-label-wrapper.is-date-picker {
    min-height: 40px;
  }
</style>
