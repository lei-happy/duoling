<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="handleSearch" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <floating-label
            v-model="form.keyword"
            label="按功能编码 / 名称搜索"
            clearable
          />
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

  interface FeatureSearchParam {
    keyword?: string;
    status?: number;
  }

  const emit = defineEmits<{
    (e: 'search', where?: FeatureSearchParam): void;
  }>();

  const [form, resetFields] = useFormData<FeatureSearchParam>({
    keyword: void 0,
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
