<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="客户名称/编码/联系人"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.customerType"
            label="客户类型"
            type="select"
            clearable
          >
            <el-option label="主机厂" :value="0" />
            <el-option label="贸易商" :value="1" />
            <el-option label="经销商" :value="2" />
            <el-option label="个人" :value="3" />
            <el-option label="其他" :value="4" />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.settlementType"
            label="结算方式"
            type="select"
            clearable
          >
            <el-option label="月结" :value="0" />
            <el-option label="票结" :value="1" />
            <el-option label="预付" :value="2" />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="状态"
            type="select"
            clearable
          >
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="0" />
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
  import type { CustomerParam } from '@/api/partner/customer/model';

  const emit = defineEmits<{
    (e: 'search', where?: CustomerParam): void;
  }>();

  const [form, resetFields] = useFormData<CustomerParam>({
    keyword: '',
    customerType: void 0,
    settlementType: void 0,
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
