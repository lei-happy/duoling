<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="账户名/账号/开户行"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.accountType"
            label="账户类型"
            type="select"
            clearable
          >
            <el-option
              v-for="o in BANK_ACCOUNT_TYPE_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.usageScope"
            label="用途"
            type="select"
            clearable
          >
            <el-option
              v-for="o in ACCOUNT_USAGE_SCOPE_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
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
            <el-option :value="1" label="启用中" />
            <el-option :value="0" label="已停用" />
          </floating-label>
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
  import type { BankAccountParam } from '@/api/finance/bank-account/model';
  import {
    ACCOUNT_USAGE_SCOPE_OPTIONS,
    BANK_ACCOUNT_TYPE_OPTIONS
  } from '../../status-config';

  const emit = defineEmits<{
    (e: 'search', where?: BankAccountParam): void;
  }>();

  const [form, resetFields] = useFormData<BankAccountParam>({
    keyword: '',
    accountType: void 0,
    usageScope: void 0,
    status: void 0
  });

  const toWhere = (): BankAccountParam => ({
    keyword: form.keyword || void 0,
    accountType: form.accountType,
    usageScope: form.usageScope,
    status: form.status
  });

  const search = () => emit('search', toWhere());
  const reset = () => {
    resetFields();
    search();
  };
</script>
