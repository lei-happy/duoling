<!-- 任务单列表搜索 -->
<template>
  <ele-card search-form class="task-search-card">
    <el-form
      class="task-search-bar"
      label-width="0"
      @keyup.enter="search"
      @submit.prevent=""
    >
      <el-row :gutter="10" class="task-search-bar__row">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="任务单号/司机/车牌/承运商"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="4" :md="6" :sm="12" :xs="24">
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
            v-model="form.carrierType"
            label="承运方式"
            type="select"
            clearable
          >
            <el-option
              v-for="o in CARRIER_TYPE_OPTIONS"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </floating-label>
        </el-col>
        <el-col :lg="4" :md="6" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="任务状态"
            type="select"
            clearable
          >
            <el-option
              v-for="o in TASK_STATUS_OPTIONS"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </floating-label>
        </el-col>
        <el-col :lg="4" :md="6" :sm="12" :xs="24">
          <floating-label
            label="起点关键字"
            type="input"
            v-model.trim="form.originKeyword"
            clearable
          />
        </el-col>
        <el-col :lg="3" :md="6" :sm="12" :xs="24">
          <floating-label
            label="终点关键字"
            type="input"
            v-model.trim="form.destinationKeyword"
            clearable
          />
        </el-col>
      </el-row>
      <el-row
        :gutter="10"
        class="task-search-bar__row task-search-bar__row--second"
      >
        <el-col :lg="6" :md="10" :sm="12" :xs="24">
          <floating-label
            v-model="form.createdAtRange"
            label="任务单创建时间"
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
          :lg="8"
          :md="12"
          :sm="12"
          :xs="24"
          class="task-search-bar__col-actions"
        >
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
  import type { TaskParam } from '@/api/operation/task/model';
  import { CARRIER_TYPE_OPTIONS, TASK_STATUS_OPTIONS } from '../status-config';

  const emit = defineEmits<{
    (e: 'search', where?: TaskParam): void;
  }>();

  const customerOptions = ref<CustomerSelectItem[]>([]);

  type SearchForm = {
    keyword: string;
    customerId: number | undefined;
    carrierType: number | undefined;
    status: number | undefined;
    originKeyword: string;
    destinationKeyword: string;
    createdAtRange: [string, string] | null;
  };

  const [form, resetFields] = useFormData<SearchForm>({
    keyword: '',
    customerId: void 0,
    carrierType: void 0,
    status: void 0,
    originKeyword: '',
    destinationKeyword: '',
    createdAtRange: [...getLast3DaysDateRange()] as [string, string]
  });

  const buildWhere = (): TaskParam => {
    const payload: TaskParam = {
      keyword: form.keyword,
      customerId: form.customerId,
      carrierType: form.carrierType,
      status: form.status,
      originKeyword: form.originKeyword,
      destinationKeyword: form.destinationKeyword
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
  .task-search-bar__row--second {
    margin-top: 12px;
    padding-top: 2px;
  }

  .task-search-bar__col-actions :deep(.el-form-item) {
    margin-bottom: 0;
    display: flex;
    justify-content: flex-start;
  }

  .task-search-bar__col-actions :deep(.el-form-item__content) {
    justify-content: flex-start;
    flex-wrap: nowrap;
  }
</style>

<style>
  .task-search-card.task-search-card {
    padding-bottom: 6px;
  }

  .task-search-bar .floating-label-wrapper.is-date-picker {
    min-height: 40px;
  }
</style>
