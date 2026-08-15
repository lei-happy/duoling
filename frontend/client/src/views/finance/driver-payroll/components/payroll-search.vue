<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="工资单号/司机"
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
              v-for="o in PAYROLL_STATUS_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.payrollModel"
            label="工资模式"
            type="select"
            clearable
          >
            <el-option
              v-for="o in PAYROLL_MODEL_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.period"
            label="工资周期"
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
      </el-row>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import type { PayrollParam } from '@/api/finance/driver-payroll/model';
  import {
    PAYROLL_MODEL_OPTIONS,
    PAYROLL_STATUS_OPTIONS
  } from '../../status-config';

  export interface PayrollSearchForm extends PayrollParam {
    period?: [string, string] | null;
  }

  const emit = defineEmits<{
    (e: 'search', where?: PayrollParam): void;
  }>();

  const [form, resetFields] = useFormData<PayrollSearchForm>({
    keyword: '',
    status: void 0,
    payrollModel: void 0,
    period: null
  });

  const toWhere = (): PayrollParam => ({
    keyword: form.keyword || void 0,
    status: form.status,
    payrollModel: form.payrollModel,
    periodStart: form.period?.[0],
    periodEnd: form.period?.[1]
  });

  const search = () => emit('search', toWhere());
  const reset = () => {
    resetFields();
    search();
  };
</script>
