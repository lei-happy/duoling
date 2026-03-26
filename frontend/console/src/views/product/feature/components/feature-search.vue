<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="handleSearch" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <floating-label
            v-model="form.module"
            label="请选择所属模块"
            type="select"
            :filterable="true"
            clearable
          >
            <el-option
              v-for="item in moduleDicts"
              :key="item.dictDataCode"
              :label="item.dictDataName"
              :value="item.dictDataCode"
            />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="请选择状态"
            type="select"
            clearable
          >
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="0" />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <el-form-item label-width="16px">
            <btn-items
              :wrap="false"
              :items="[
                { preset: 'search', onClick: () => handleSearch() },
                { preset: 'reset', onClick: () => handleReset() }
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
  import { useDictData } from '@/utils/use-dict-data';
  import { DICT_CODE_PRODUCT_MODULE } from '@/api/product/model';

  interface FeatureSearchParam {
    module?: string;
    status?: number;
  }

  const emit = defineEmits<{
    (e: 'search', where?: FeatureSearchParam): void;
  }>();

  const [moduleDicts] = useDictData([DICT_CODE_PRODUCT_MODULE]);

  const [form, resetFields] = useFormData<FeatureSearchParam>({
    module: void 0,
    status: void 0
  });

  const handleSearch = () => {
    emit('search', { ...form });
  };

  const handleReset = () => {
    resetFields();
    handleSearch();
  };
</script>
