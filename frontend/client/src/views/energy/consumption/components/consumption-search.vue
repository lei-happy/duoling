<template>
  <ele-card search-form class="consumption-search-card">
    <el-alert
      type="info"
      :closable="false"
      class="search-hint"
      title="油补是付给司机的补贴；这里的消费是付给供应商的能源费。司机垫付只作台账，不扣能源账户、不重复计成本。"
    />
    <el-form
      class="consumption-search-bar"
      label-width="0"
      @keyup.enter="search"
      @submit.prevent=""
    >
      <el-row :gutter="10" class="consumption-search-bar__row">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="单号/卡号/车牌"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.matchStatus"
            label="匹配状态"
            type="select"
            clearable
          >
            <el-option
              v-for="o in MATCH_STATUSES"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.energyType"
            label="能源类型"
            type="select"
            clearable
          >
            <el-option
              v-for="o in ENERGY_TYPES"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
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
  import { ENERGY_TYPES, MATCH_STATUSES } from '../../_shared/options';

  export interface ConsumptionSearchParam {
    keyword?: string;
    matchStatus?: string;
    energyType?: string;
  }

  const emit = defineEmits<{
    (e: 'search', where?: ConsumptionSearchParam): void;
  }>();

  const [form, resetFields] = useFormData<ConsumptionSearchParam>({
    keyword: '',
    matchStatus: void 0,
    energyType: void 0
  });

  const search = () => emit('search', { ...form });
  const reset = () => {
    resetFields();
    search();
  };
</script>

<style scoped>
  .search-hint {
    margin-bottom: 12px;
  }
</style>
