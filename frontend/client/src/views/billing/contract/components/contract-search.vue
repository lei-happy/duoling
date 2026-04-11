<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入合同编号 / 名称 / 客户名称"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="请选择合同状态"
            type="select"
            clearable
          >
            <el-option label="草稿" :value="0" />
            <el-option label="生效" :value="1" />
            <el-option label="已过期" :value="2" />
            <el-option label="已终止" :value="3" />
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
  import type { FreightContractParam } from '@/api/billing/contract/model';

  const emit = defineEmits<{
    (e: 'search', where?: FreightContractParam): void;
  }>();

  const [form, resetFields] = useFormData<FreightContractParam>({
    keyword: '',
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
