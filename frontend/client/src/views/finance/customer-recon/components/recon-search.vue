<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="对账单号/客户"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.customerId"
            label="客户"
            type="select"
            filterable
            clearable
          >
            <el-option
              v-for="c in customers"
              :key="c.id"
              :value="c.id"
              :label="c.customerName"
            />
          </floating-label>
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="状态"
            type="select"
            clearable
          >
            <el-option
              v-for="o in RECON_STATUS_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.period"
            label="对账周期"
            type="date"
            date-type="daterange"
            value-format="YYYY-MM-DD"
            start-placeholder="开始"
            end-placeholder="结束"
            unlink-panels
          />
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
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
        <el-col :span="24">
          <div class="search-flags">
            <el-checkbox v-model="form.onlyDirty">只看待重核</el-checkbox>
            <el-checkbox v-model="form.onlyDiff">只看有差异</el-checkbox>
          </div>
        </el-col>
      </el-row>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import type { ReconParam } from '@/api/finance/customer-recon/model';
  import { RECON_STATUS_OPTIONS } from '../../status-config';

  export interface ReconSearchParam extends ReconParam {
    period?: [string, string] | null;
  }

  defineProps<{
    customers: CustomerSelectItem[];
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: ReconParam): void;
  }>();

  const [form, resetFields] = useFormData<ReconSearchParam>({
    keyword: '',
    customerId: void 0,
    status: void 0,
    period: null,
    onlyDirty: false,
    onlyDiff: false
  });

  const toWhere = (): ReconParam => ({
    keyword: form.keyword || void 0,
    customerId: form.customerId,
    status: form.status,
    periodStart: form.period?.[0],
    periodEnd: form.period?.[1],
    onlyDirty: form.onlyDirty || void 0,
    onlyDiff: form.onlyDiff || void 0
  });

  const search = () => emit('search', toWhere());
  const reset = () => {
    resetFields();
    search();
  };

  defineExpose({
    setCustomer(customerId?: number) {
      form.customerId = customerId;
      search();
    }
  });
</script>

<style scoped lang="scss">
  @use '../../_shared/ui.scss';
</style>
