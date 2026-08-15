<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="结算单号/承运商"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.carrierId"
            label="承运商"
            type="select"
            filterable
            clearable
          >
            <el-option
              v-for="c in carriers"
              :key="c.id"
              :value="c.id"
              :label="c.carrierName"
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
              v-for="o in CARRIER_SETTLE_STATUS_OPTIONS"
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
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.invoiceMatched"
            label="收票情况"
            type="select"
            clearable
          >
            <el-option :value="0" label="未收齐票" />
            <el-option :value="1" label="票款相符" />
          </floating-label>
        </el-col>
      </el-row>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import type { CarrierSelectItem } from '@/api/partner/carrier/model';
  import type { CarrierSettleParam } from '@/api/finance/carrier-settlement/model';
  import { CARRIER_SETTLE_STATUS_OPTIONS } from '../../status-config';

  defineProps<{
    carriers: CarrierSelectItem[];
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: CarrierSettleParam): void;
  }>();

  const [form, resetFields] = useFormData<CarrierSettleParam>({
    keyword: '',
    carrierId: void 0,
    status: void 0,
    dueBefore: void 0,
    invoiceMatched: void 0
  });

  const toWhere = (): CarrierSettleParam => ({
    keyword: form.keyword || void 0,
    carrierId: form.carrierId,
    status: form.status,
    dueBefore: form.dueBefore,
    invoiceMatched: form.invoiceMatched
  });

  const search = () => emit('search', toWhere());
  const reset = () => {
    resetFields();
    search();
  };
</script>
