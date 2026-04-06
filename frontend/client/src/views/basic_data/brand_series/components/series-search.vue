<!-- 车系列表筛选 -->
<template>
  <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
    <el-row :gutter="16">
      <el-col :lg="6" :md="12" :sm="12" :xs="24">
        <floating-label
          label="请输入车系名称"
          type="input"
          v-model.trim="form.keyword"
          clearable
        />
      </el-col>
      <el-col :lg="6" :md="12" :sm="12" :xs="24">
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

  const emit = defineEmits<{
    (e: 'search', where?: { keyword?: string }): void;
  }>();

  const [form, resetFields] = useFormData<{ keyword: string }>({
    keyword: ''
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };
</script>
