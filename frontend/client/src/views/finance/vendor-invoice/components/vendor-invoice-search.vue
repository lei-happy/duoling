<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="发票号/供应商"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="状态"
            type="select"
            clearable
          >
            <el-option
              v-for="o in VENDOR_INVOICE_STATUS_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.vendorType"
            label="供应商类型"
            type="select"
            clearable
          >
            <el-option
              v-for="o in VENDOR_TYPE_OPTIONS"
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
            <el-checkbox v-model="form.onlyUnsettled">只看未核销完</el-checkbox>
          </div>
        </el-col>
      </el-row>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import type { VendorInvoiceParam } from '@/api/finance/vendor-invoice/model';
  import {
    VENDOR_INVOICE_STATUS_OPTIONS,
    VENDOR_TYPE_OPTIONS
  } from '../../status-config';

  export interface VendorInvoiceSearchForm extends VendorInvoiceParam {
    dateRange?: [string, string] | null;
  }

  const emit = defineEmits<{
    (e: 'search', where?: VendorInvoiceParam): void;
  }>();

  const [form, resetFields] = useFormData<VendorInvoiceSearchForm>({
    keyword: '',
    status: void 0,
    vendorType: void 0,
    dateRange: null,
    onlyUnsettled: false
  });

  const toWhere = (): VendorInvoiceParam => ({
    keyword: form.keyword || void 0,
    status: form.status,
    vendorType: form.vendorType,
    dateFrom: form.dateRange?.[0],
    dateTo: form.dateRange?.[1],
    onlyUnsettled: form.onlyUnsettled || void 0
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
