<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="7" :md="8" :sm="12" :xs="24">
          <floating-label
            label="供应商名称/编码"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.supplierType"
            label="供应商类型"
            type="select"
            clearable
          >
            <el-option
              v-for="o in SUPPLIER_TYPES"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
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
        <el-col :lg="7" :md="8" :sm="12" :xs="24">
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
  import { SUPPLIER_TYPES } from '../../_shared/options';

  export interface SupplierSearchParam {
    keyword?: string;
    supplierType?: number;
    status?: number;
  }

  const emit = defineEmits<{
    (e: 'search', where?: SupplierSearchParam): void;
  }>();

  const [form, resetFields] = useFormData<SupplierSearchParam>({
    keyword: '',
    supplierType: void 0,
    status: void 0
  });

  const search = () => emit('search', { ...form });
  const reset = () => {
    resetFields();
    search();
  };
</script>
