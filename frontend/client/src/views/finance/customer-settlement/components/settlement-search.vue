<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="结算单号/客户"
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
              v-for="o in SETTLE_STATUS_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.dueBefore"
            label="到期日早于"
            type="date"
            date-type="date"
            value-format="YYYY-MM-DD"
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
            <el-checkbox v-model="form.onlyUnreceived">只看未收齐</el-checkbox>
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
  import type { SettleParam } from '@/api/finance/customer-settlement/model';
  import { SETTLE_STATUS_OPTIONS } from '../../status-config';

  defineProps<{
    customers: CustomerSelectItem[];
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: SettleParam): void;
  }>();

  const [form, resetFields] = useFormData<SettleParam>({
    keyword: '',
    customerId: void 0,
    status: void 0,
    dueBefore: void 0,
    onlyUnreceived: false
  });

  const toWhere = (): SettleParam => ({
    keyword: form.keyword || void 0,
    customerId: form.customerId,
    status: form.status,
    dueBefore: form.dueBefore,
    onlyUnreceived: form.onlyUnreceived || void 0
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
