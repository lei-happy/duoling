<!--
  运单工作台 - 按 pool 配置渲染的筛选栏
  ====================================

  - 根据 `pool.filterFields` 数组只渲染对应控件，组件化关键所在
  - 布局策略：
      - **紧凑单行**：全部筛选项 + 操作按钮能放进 24 栅格时（如已关闭 pool），
        各字段固定 lg=6，与四列主筛时单列宽度一致；
      - **双行**：主筛 4 列铺满第 1 行，创建时间 / 品牌车型 / 操作按钮在第 2 行。
  - 切换 pool 时由父组件通过 :key 触发重新挂载，无需手动 reset

  字段映射（来自 waybill-pool-registry）：
    keyword       → 运单编号
    customer      → 客户下拉
    origin        → 出发地（关键字）
    destination   → 目的地（关键字）
    vehicle       → 品牌/车型
    createdRange  → 创建时间区间
-->
<template>
  <ele-card search-form class="wb-filter-card">
    <el-form
      class="wb-filter"
      label-width="0"
      @keyup.enter="emitSearch"
      @submit.prevent=""
    >
      <!-- 紧凑单行：筛选项较少时一次放下（如已关闭） -->
      <el-row v-if="useCompactRow" :gutter="10" class="wb-filter__row">
        <el-col
          v-if="has('keyword')"
          :lg="fieldCol.lg"
          :md="fieldCol.md"
          :sm="fieldCol.sm"
          :xs="fieldCol.xs"
        >
          <floating-label
            label="运单编号"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col
          v-if="has('customer')"
          :lg="fieldCol.lg"
          :md="fieldCol.md"
          :sm="fieldCol.sm"
          :xs="fieldCol.xs"
        >
          <floating-label
            v-model="form.customerId"
            label="请选择客户"
            type="select"
            filterable
            clearable
          >
            <el-option
              v-for="item in customerOptions"
              :key="item.id"
              :label="item.customerName"
              :value="item.id"
            />
          </floating-label>
        </el-col>
        <el-col
          v-if="has('origin')"
          :lg="fieldCol.lg"
          :md="fieldCol.md"
          :sm="fieldCol.sm"
          :xs="fieldCol.xs"
        >
          <floating-label
            label="出发地"
            type="input"
            v-model.trim="form.originKeyword"
            clearable
          />
        </el-col>
        <el-col
          v-if="has('destination')"
          :lg="fieldCol.lg"
          :md="fieldCol.md"
          :sm="fieldCol.sm"
          :xs="fieldCol.xs"
        >
          <floating-label
            label="目的地"
            type="input"
            v-model.trim="form.destinationKeyword"
            clearable
          />
        </el-col>
        <el-col
          v-if="has('vehicle')"
          :lg="fieldCol.lg"
          :md="fieldCol.md"
          :sm="fieldCol.sm"
          :xs="fieldCol.xs"
        >
          <floating-label
            label="品牌/车型"
            type="input"
            v-model.trim="form.vehicleKeyword"
            clearable
          />
        </el-col>
        <el-col
          v-if="has('createdRange')"
          :lg="fieldCol.lg"
          :md="fieldCol.md"
          :sm="fieldCol.sm"
          :xs="fieldCol.xs"
        >
          <floating-label
            v-model="form.createdAtRange"
            label="运单创建时间"
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
      <template v-else>
      <el-row v-if="hasPrimaryRow" :gutter="10" class="wb-filter__row">
        <el-col
          v-if="has('keyword')"
          :lg="primaryColSpan.lg"
          :md="primaryColSpan.md"
          :sm="primaryColSpan.sm"
          :xs="primaryColSpan.xs"
        >
          <floating-label
            label="请输入运单编号"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col
          v-if="has('customer')"
          :lg="primaryColSpan.lg"
          :md="primaryColSpan.md"
          :sm="primaryColSpan.sm"
          :xs="primaryColSpan.xs"
        >
          <floating-label
            v-model="form.customerId"
            label="请选择客户"
            type="select"
            filterable
            clearable
          >
            <el-option
              v-for="item in customerOptions"
              :key="item.id"
              :label="item.customerName"
              :value="item.id"
            />
          </floating-label>
        </el-col>
        <el-col
          v-if="has('origin')"
          :lg="primaryColSpan.lg"
          :md="primaryColSpan.md"
          :sm="primaryColSpan.sm"
          :xs="primaryColSpan.xs"
        >
          <floating-label
            label="请输入出发地"
            type="input"
            v-model.trim="form.originKeyword"
            clearable
          />
        </el-col>
        <el-col
          v-if="has('destination')"
          :lg="primaryColSpan.lg"
          :md="primaryColSpan.md"
          :sm="primaryColSpan.sm"
          :xs="primaryColSpan.xs"
        >
          <floating-label
            label="请输入目的地"
            type="input"
            v-model.trim="form.destinationKeyword"
            clearable
          />
        </el-col>
      </el-row>
      <el-row
        :gutter="10"
        class="wb-filter__row"
        :class="{ 'wb-filter__row--second': hasPrimaryRow }"
      >
        <el-col
          v-if="has('vehicle')"
          :lg="fieldCol.lg"
          :md="fieldCol.md"
          :sm="fieldCol.sm"
          :xs="fieldCol.xs"
        >
          <floating-label
            label="请输入品牌/车型"
            type="input"
            v-model.trim="form.vehicleKeyword"
            clearable
          />
        </el-col>
        <el-col
          v-if="has('createdRange')"
          :lg="fieldCol.lg"
          :md="fieldCol.md"
          :sm="fieldCol.sm"
          :xs="fieldCol.xs"
        >
          <floating-label
            v-model="form.createdAtRange"
            label="请选择运单创建时间"
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
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref, watch } from 'vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { getLast3DaysDateRange } from '@/utils/date-util';
  import { selectCustomers } from '@/api/partner/customer';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import type { WaybillParam } from '@/api/waybill/model';
  import type { WaybillFilterField } from '../waybill-pool-registry';

  const props = defineProps<{
    /** 该 pool 启用的筛选字段（其他字段不渲染、不参与 buildWhere） */
    fields: WaybillFilterField[];
  }>();

  const emit = defineEmits<{
    (e: 'search', where: WaybillParam): void;
  }>();

  type FilterForm = {
    keyword: string;
    customerId: number | undefined;
    originKeyword: string;
    destinationKeyword: string;
    vehicleKeyword: string;
    createdAtRange: [string, string] | null;
  };

  /**
   * 仅在该 pool 启用 createdRange 字段时，默认填充最近 3 天，
   * 与原 waybill-search 行为一致；其他池不预填，避免误过滤。
   */
  const buildInitial = (): FilterForm => ({
    keyword: '',
    customerId: void 0,
    originKeyword: '',
    destinationKeyword: '',
    vehicleKeyword: '',
    createdAtRange: props.fields.includes('createdRange')
      ? ([...getLast3DaysDateRange()] as [string, string])
      : null
  });

  const [form, resetFields] = useFormData<FilterForm>(buildInitial());

  const has = (field: WaybillFilterField) => props.fields.includes(field);

  /** 与其他 pool 四列主筛时单列宽度一致 */
  const fieldCol = { lg: 6, md: 6, sm: 12, xs: 24 };
  const actionsCol = { lg: 4, md: 6, sm: 12, xs: 24 };

  /** 全部筛选项 + 操作列能放进一行时使用紧凑布局（如已关闭：6+6+6+4=22） */
  const useCompactRow = computed(
    () => props.fields.length * fieldCol.lg + actionsCol.lg <= 24
  );

  /** 第一行主筛选项：运单编号 / 客户 / 出发地 / 目的地 */
  const PRIMARY_FIELDS: WaybillFilterField[] = [
    'keyword',
    'customer',
    'origin',
    'destination'
  ];

  const primaryFieldCount = computed(
    () => PRIMARY_FIELDS.filter((field) => has(field)).length
  );

  const hasPrimaryRow = computed(() => primaryFieldCount.value > 0);

  /** lg/md 下均分 24 栅格，使第一行铺满整行 */
  const primaryColSpan = computed(() => {
    const n = primaryFieldCount.value;
    const span = n > 0 ? Math.floor(24 / n) : 24;
    return { lg: span, md: span, sm: 12, xs: 24 };
  });

  const customerOptions = ref<CustomerSelectItem[]>([]);
  /** 仅 pool 需要时才请求客户下拉 */
  const needCustomer = computed(() => has('customer'));

  const loadCustomerOptions = async () => {
    if (!needCustomer.value || customerOptions.value.length > 0) return;
    try {
      customerOptions.value = (await selectCustomers()) ?? [];
    } catch (_) {
      customerOptions.value = [];
    }
  };

  watch(needCustomer, () => loadCustomerOptions(), { immediate: false });

  /** 构造 WaybillParam：未启用的字段一律不写出，避免污染查询条件 */
  const buildWhere = (): WaybillParam => {
    const payload: WaybillParam = {};
    if (has('keyword') && form.keyword) payload.keyword = form.keyword;
    if (has('customer') && form.customerId != null) {
      payload.customerId = form.customerId;
    }
    if (has('origin') && form.originKeyword) {
      payload.originKeyword = form.originKeyword;
    }
    if (has('destination') && form.destinationKeyword) {
      payload.destinationKeyword = form.destinationKeyword;
    }
    if (has('vehicle') && form.vehicleKeyword) {
      payload.vehicleKeyword = form.vehicleKeyword;
    }
    if (has('createdRange')) {
      const range = form.createdAtRange;
      if (Array.isArray(range) && range.length === 2 && range[0] && range[1]) {
        payload.createdAtStart = range[0];
        payload.createdAtEnd = range[1];
      }
    }
    return payload;
  };

  const emitSearch = () => emit('search', buildWhere());

  const onReset = () => {
    resetFields();
    if (has('createdRange')) {
      form.createdAtRange = [...getLast3DaysDateRange()] as [string, string];
    }
    emitSearch();
  };

  onMounted(async () => {
    await loadCustomerOptions();
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
