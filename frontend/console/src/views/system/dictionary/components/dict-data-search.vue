<!-- 搜索表单 -->
<template>
  <el-form label-width="84px" @keyup.enter="search" @submit.prevent="">
    <el-row :gutter="16">
      <el-col :lg="8" :md="8" :sm="12" :xs="24">
        <el-form-item label="字典数据名">
          <el-input
            clearable
            v-model.trim="form.dictDataName"
            placeholder="请输入"
          />
        </el-form-item>
      </el-col>
      <el-col :lg="8" :md="8" :sm="12" :xs="24">
        <el-form-item label="字典数据值">
          <el-input
            clearable
            v-model.trim="form.dictDataCode"
            placeholder="请输入"
          />
        </el-form-item>
      </el-col>
      <el-col :lg="8" :md="8" :sm="12" :xs="24">
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
</template>

<script lang="ts" setup>
  import { useFormData } from '@/utils/use-form-data';
  import type { DictionaryDataParam } from '@/api/system/dictionary-data/model';

  const emit = defineEmits<{
    (e: 'search', where?: DictionaryDataParam): void;
  }>();

  /** 表单数据 */
  const [form, resetFields] = useFormData<DictionaryDataParam>({
    dictDataName: '',
    dictDataCode: ''
  });

  /** 搜索 */
  const search = () => {
    emit('search', { ...form });
  };

  /**  重置 */
  const reset = () => {
    resetFields();
    search();
  };
</script>
