<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.supplierId"
            label="所属供应商"
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
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
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
        <el-col :lg="7" :md="8" :sm="12" :xs="24">
          <floating-label
            label="站点名称/编码/地址"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
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
  import { ENERGY_TYPES } from '../../_shared/options';

  export interface StationSearchParam {
    supplierId?: number;
    energyType?: string;
    keyword?: string;
  }

  defineProps<{
    suppliers: Array<{ id: number; supplierName: string }>;
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: StationSearchParam): void;
  }>();

  const [form, resetFields] = useFormData<StationSearchParam>({
    supplierId: void 0,
    energyType: void 0,
    keyword: ''
  });

  const search = () => emit('search', { ...form });
  const reset = () => {
    resetFields();
    search();
  };

  const setSupplier = (supplierId?: number) => {
    form.supplierId = supplierId;
    form.keyword = '';
    search();
  };

  defineExpose({ setSupplier });
</script>
