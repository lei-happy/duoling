<!-- 搜索表单 -->
<template>
  <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
    <el-row :gutter="16">
      <el-col :lg="8" :md="8" :sm="12" :xs="24">
        <floating-label
          label="请输入字典数据名"
          type="input"
          v-model.trim="form.dictDataName"
          clearable
        />
      </el-col>
      <el-col :lg="8" :md="8" :sm="12" :xs="24">
        <floating-label
          label="请输入字典数据值"
          type="input"
          v-model.trim="form.dictDataCode"
          clearable
        />
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
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
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
