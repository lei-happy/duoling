<!-- 合同详情内承运价明细筛选 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="7" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入出发地 / 目的地 / 品牌 / 车型"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.billingMode"
            label="请选择计费模式"
            type="select"
            clearable
          >
            <el-option label="台单价" :value="0" />
            <el-option label="单公里" :value="1" />
            <el-option label="整单价" :value="2" />
          </floating-label>
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.priceType"
            label="请选择运价类型"
            type="select"
            clearable
          >
            <el-option label="明确" :value="0" />
            <el-option label="预估" :value="1" />
          </floating-label>
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="请选择状态"
            type="select"
            clearable
          >
            <el-option label="生效" :value="1" />
            <el-option label="停用" :value="0" />
          </floating-label>
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
  import type { CarrierRateFilterParam } from '@/api/billing/carrier-contract/model';

  const emit = defineEmits<{
    (e: 'search', where?: CarrierRateFilterParam): void;
  }>();

  const [form, resetFields] = useFormData<CarrierRateFilterParam>({
    keyword: '',
    billingMode: void 0,
    priceType: void 0,
    status: void 0
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };
</script>
