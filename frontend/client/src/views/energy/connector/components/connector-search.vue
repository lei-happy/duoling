<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="8" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.supplierId"
            label="供应商"
            type="select"
            filterable
            clearable
          >
            <el-option
              v-for="s in suppliers"
              :key="s.id"
              :label="s.supplierName"
              :value="s.id"
            />
          </floating-label>
        </el-col>
        <el-col :lg="16" :md="16" :sm="12" :xs="24">
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

  export interface ConnectorSearchParam {
    supplierId?: number;
  }

  defineProps<{
    suppliers: Array<{ id: number; supplierName: string }>;
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: ConnectorSearchParam): void;
  }>();

  const [form, resetFields] = useFormData<ConnectorSearchParam>({
    supplierId: void 0
  });

  const search = () => emit('search', { ...form });
  const reset = () => {
    resetFields();
    search();
  };
</script>
