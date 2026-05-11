<!-- 运单列表搜索 -->
<template>
  <ele-card search-form class="waybill-search-card">
    <el-form
      class="waybill-search-bar"
      label-width="0"
      @keyup.enter="search"
      @submit.prevent=""
    >
      <el-row :gutter="10" class="waybill-search-bar__row">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="运单编号"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
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
        <el-col :lg="4" :md="6" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="运单状态"
            type="select"
            clearable
          >
            <el-option label="待确认" :value="0" />
            <el-option label="已确认" :value="1" />
            <el-option label="已调度" :value="2" />
            <el-option label="运输中" :value="3" />
            <el-option label="已送达" :value="4" />
            <el-option label="已完成" :value="5" />
            <el-option label="已取消" :value="6" />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="出发地"
            type="input"
            v-model.trim="form.originKeyword"
            clearable
          />
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="目的地"
            type="input"
            v-model.trim="form.destinationKeyword"
            clearable
          />
        </el-col>
      </el-row>
      <el-row :gutter="10" class="waybill-search-bar__row waybill-search-bar__row--second">
        <el-col :lg="8" :md="10" :sm="24" :xs="24">
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
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="品牌/车型"
            type="input"
            v-model.trim="form.vehicleKeyword"
            clearable
          />
        </el-col>
        <el-col :lg="8" :md="12" :sm="12" :xs="24" class="waybill-search-bar__col-actions">
          <el-form-item label-width="0px">
            <btn-items
              :wrap="false"
              :items="[
                { preset: 'search', onClick: () => search() },
                { preset: 'reset', onClick: () => reset() }
              ]"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { getLast3DaysDateRange } from '@/utils/date-util';
  import { selectCustomers } from '@/api/partner/customer';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import type { WaybillParam } from '@/api/waybill/model';

  const emit = defineEmits<{
    (e: 'search', where?: WaybillParam): void;
  }>();

  const customerOptions = ref<CustomerSelectItem[]>([]);

  type SearchForm = {
    keyword: string;
    customerId: number | undefined;
    status: number | undefined;
    originKeyword: string;
    destinationKeyword: string;
    vehicleKeyword: string;
    createdAtRange: [string, string] | null;
  };

  const [form, resetFields] = useFormData<SearchForm>({
    keyword: '',
    customerId: void 0,
    status: void 0,
    originKeyword: '',
    destinationKeyword: '',
    vehicleKeyword: '',
    createdAtRange: [...getLast3DaysDateRange()] as [string, string]
  });

  const buildWhere = (): WaybillParam => {
    const payload: WaybillParam = {
      keyword: form.keyword,
      customerId: form.customerId,
      status: form.status,
      originKeyword: form.originKeyword,
      destinationKeyword: form.destinationKeyword,
      vehicleKeyword: form.vehicleKeyword
    };
    const range = form.createdAtRange;
    if (Array.isArray(range) && range.length === 2 && range[0] && range[1]) {
      payload.createdAtStart = range[0];
      payload.createdAtEnd = range[1];
    }
    return payload;
  };

  const search = () => {
    emit('search', buildWhere());
  };

  const reset = () => {
    resetFields();
    form.createdAtRange = [...getLast3DaysDateRange()] as [string, string];
    search();
  };

  onMounted(async () => {
    try {
      customerOptions.value = (await selectCustomers()) ?? [];
    } catch (_) {
      customerOptions.value = [];
    }
    search();
  });
</script>

<style scoped>
  .waybill-search-bar__row--second {
    margin-top: 12px;
    padding-top: 2px;
  }

  .waybill-search-bar__col-actions :deep(.el-form-item) {
    margin-bottom: 0;
    display: flex;
    justify-content: flex-start;
  }

  .waybill-search-bar__col-actions :deep(.el-form-item__content) {
    justify-content: flex-start;
    flex-wrap: nowrap;
  }
</style>

<style>
  .waybill-search-card.waybill-search-card {
    padding-bottom: 6px;
  }

  .waybill-search-bar .floating-label-wrapper.is-date-picker {
    min-height: 40px;
  }
</style>
