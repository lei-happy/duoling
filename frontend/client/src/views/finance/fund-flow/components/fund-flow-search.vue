<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="单号/对方名称/银行流水号"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.direction"
            label="收付方向"
            type="select"
            clearable
          >
            <el-option
              v-for="o in FLOW_DIRECTION_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.bankAccountId"
            label="收付账户"
            type="select"
            filterable
            clearable
          >
            <el-option
              v-for="a in accounts"
              :key="a.id"
              :value="a.id"
              :label="a.displayLabel || a.accountName"
            />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.dateRange"
            label="发生日期"
            type="date"
            date-type="daterange"
            value-format="YYYY-MM-DD"
            start-placeholder="发生起"
            end-placeholder="发生止"
            unlink-panels
          />
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
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
  import type { BankAccountOption } from '@/api/finance/bank-account/model';
  import type { FundFlowParam } from '@/api/finance/payment-batch/model';
  import { FLOW_DIRECTION_OPTIONS } from '../../status-config';

  export interface FundFlowSearchForm extends FundFlowParam {
    dateRange?: [string, string] | null;
  }

  defineProps<{
    accounts: BankAccountOption[];
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: FundFlowParam): void;
  }>();

  const [form, resetFields] = useFormData<FundFlowSearchForm>({
    keyword: '',
    direction: void 0,
    bankAccountId: void 0,
    dateRange: null
  });

  const toWhere = (): FundFlowParam => ({
    keyword: form.keyword || void 0,
    direction: form.direction,
    bankAccountId: form.bankAccountId,
    dateFrom: form.dateRange?.[0],
    dateTo: form.dateRange?.[1]
  });

  const search = () => emit('search', toWhere());
  const reset = () => {
    resetFields();
    search();
  };
</script>
