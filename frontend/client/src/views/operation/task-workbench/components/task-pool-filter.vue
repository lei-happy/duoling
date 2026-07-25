<!--
  调度工作台 - 统一筛选栏（页面级，切换阶段卡时不重建）

  字段并集：任务单号/计划号/任务名称、出发地、目的地、承运方式、承运商、时间维度+区间
-->
<template>
  <ele-card search-form class="wb-filter-card">
    <el-form
      class="wb-filter"
      label-width="0"
      @keyup.enter="emitSearch"
      @submit.prevent=""
    >
      <el-row :gutter="10" class="wb-filter__row">
        <el-col :lg="4" :md="6" :sm="12" :xs="24">
          <floating-label
            label="请输入任务单号"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="4" :md="6" :sm="12" :xs="24">
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
          :lg="timeFieldCol.lg"
          :md="timeFieldCol.md"
          :sm="timeFieldCol.sm"
          :xs="timeFieldCol.xs"
          :lg-offset="showCarrierFilter ? 0 : 6"
          :md-offset="showCarrierFilter ? 0 : 6"
        >
          <floating-label
            v-model="form.timeField"
            label="时间类型"
            type="select"
            :clearable="false"
          >
            <el-option
              v-for="o in TASK_TIME_FIELD_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </floating-label>
        </el-col>
        <el-col
          :lg="timeRangeCol.lg"
          :md="timeRangeCol.md"
          :sm="timeRangeCol.sm"
          :xs="timeRangeCol.xs"
        >
          <floating-label
            v-model="form.timeRange"
            :label="timeRangeLabel"
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
  import type { TaskParam, TaskTimeField } from '@/api/operation/task/model';
  import { CARRIER_TYPE, CARRIER_TYPE_OPTIONS } from '../../task/status-config';
  import {
    TASK_TIME_FIELD_OPTIONS,
    resolveDefaultTimeField,
    timeFieldLabel
  } from '../workbench-time-filter';

  const props = withDefaults(
    defineProps<{
      /** 当前阶段卡 key，用于重置时恢复默认时间维度 */
      poolKey?: string;
    }>(),
    { poolKey: 'pending-assign' }
  );

  const emit = defineEmits<{
    (e: 'search', where: Partial<TaskParam>): void;
    (e: 'reset', where: Partial<TaskParam>): void;
  }>();

  type FilterForm = {
    keyword: string;
    originKeyword: string;
    destinationKeyword: string;
    carrierType: number | undefined;
    carrierId: number | undefined;
    timeField: TaskTimeField;
    timeRange: [string, string] | null;
  };

  const defaultTimeField = () => resolveDefaultTimeField(props.poolKey);

  const buildInitial = (): FilterForm => ({
    keyword: '',
    originKeyword: '',
    destinationKeyword: '',
    carrierType: void 0,
    carrierId: void 0,
    timeField: defaultTimeField(),
    timeRange: [...getLast3DaysDateRange()] as [string, string]
  });

  const [form, resetFields] = useFormData<FilterForm>(buildInitial());

  const showCarrierFilter = computed(
    () => form.carrierType === CARRIER_TYPE.CARRIER
  );

  const timeRangeLabel = computed(
    () => `请选择${timeFieldLabel(form.timeField)}`
  );

  /** 第二行与第一行四列对齐：承运商(6) | 时间类型(4)+时间范围(8)=出发地+目的地(12) | 操作(6) */
  const fieldCol = { lg: 6, md: 6, sm: 12, xs: 24 };
  const timeFieldCol = { lg: 4, md: 6, sm: 12, xs: 24 };
  const timeRangeCol = { lg: 8, md: 12, sm: 12, xs: 24 };
  const actionsCol = { lg: 6, md: 24, sm: 12, xs: 24 };

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

    const origin = form.originKeyword.trim();
    const dest = form.destinationKeyword.trim();
    if (origin) payload.originKeyword = origin;
    if (dest) payload.destinationKeyword = dest;
    if (form.carrierType != null) payload.carrierType = form.carrierType;
    if (showCarrierFilter.value && form.carrierId != null) {
      payload.carrierId = form.carrierId;
    }
    const range = form.timeRange;
    if (Array.isArray(range) && range.length === 2 && range[0] && range[1]) {
      payload.timeField = form.timeField;
      payload.timeStart = range[0];
      payload.timeEnd = range[1];
    }
    return payload;
  };

  const emitSearch = () => emit('search', buildWhere());

  const onReset = () => {
    resetFields();
    form.timeField = defaultTimeField();
    form.timeRange = [...getLast3DaysDateRange()] as [string, string];
    emit('reset', buildWhere());
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
