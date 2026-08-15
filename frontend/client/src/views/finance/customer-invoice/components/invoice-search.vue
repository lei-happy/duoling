<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="申请单号/发票号/客户"
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
              v-for="o in CUSTOMER_INVOICE_STATUS_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.dateRange"
            label="开票日期"
            type="date"
            date-type="daterange"
            value-format="YYYY-MM-DD"
            start-placeholder="开票起"
            end-placeholder="开票止"
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
            <el-checkbox v-model="form.onlyRed">只看红字票</el-checkbox>
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
  import type { CustomerInvoiceParam } from '@/api/finance/customer-invoice/model';
  import { CUSTOMER_INVOICE_STATUS_OPTIONS } from '../../status-config';

  export interface InvoiceSearchForm extends CustomerInvoiceParam {
    dateRange?: [string, string] | null;
  }

  defineProps<{
    customers: CustomerSelectItem[];
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: CustomerInvoiceParam): void;
  }>();

  const [form, resetFields] = useFormData<InvoiceSearchForm>({
    keyword: '',
    customerId: void 0,
    status: void 0,
    dateRange: null,
    onlyRed: false
  });

  const toWhere = (): CustomerInvoiceParam => ({
    keyword: form.keyword || void 0,
    customerId: form.customerId,
    status: form.status,
    dateFrom: form.dateRange?.[0],
    dateTo: form.dateRange?.[1],
    onlyRed: form.onlyRed || void 0
  });

  const search = () => emit('search', toWhere());
  const reset = () => {
    resetFields();
    search();
  };
</script>

<style scoped lang="scss">
  @use '../../_shared/ui.scss';
</style>
