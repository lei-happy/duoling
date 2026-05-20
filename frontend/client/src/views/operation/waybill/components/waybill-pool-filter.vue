<!--
  运单工作台 - 按 pool 配置渲染的筛选栏
  ====================================

  - 根据 `pool.filterFields` 数组只渲染对应控件，组件化关键所在
  - 布局策略：**单 el-row 自然换行**
      所有字段 + 操作按钮放在同一个 `el-row`，依靠 `el-col` 的 `lg/md/sm/xs`
      响应式宽度，由浏览器决定是否换行。
      → 少字段 pool（如 `closed`、`scheduling`）能在 1 行内完整放下；
      → 多字段 pool（如 `pending-confirm`）超过 24 列后自然落到第 2 行。
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
      <el-row :gutter="10" class="wb-filter__row">
        <el-col
          v-if="has('keyword')"
          :lg="5"
          :md="8"
          :sm="12"
          :xs="24"
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
          :lg="5"
          :md="8"
          :sm="12"
          :xs="24"
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
          :lg="5"
          :md="8"
          :sm="12"
          :xs="24"
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
          :lg="5"
          :md="8"
          :sm="12"
          :xs="24"
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
          :lg="4"
          :md="6"
          :sm="12"
          :xs="24"
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
          :lg="5"
          :md="8"
          :sm="12"
          :xs="24"
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
        <!--
          操作列恒展示；lg=4 比字段窄，目的是把 closed/scheduling 这类
          字段少的 pool 顶进 1 行（如 closed: 5+5+5+4=19 ≤ 24）。
        -->
        <el-col
          :lg="4"
          :md="6"
          :sm="12"
          :xs="24"
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
