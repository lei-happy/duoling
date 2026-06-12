<!-- 审批流程搜索 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入流程名称"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.bizType"
            label="请选择审批场景"
            type="select"
            clearable
          >
            <el-option
              v-for="t in bizTypeOptions"
              :key="t.value"
              :value="t.value"
              :label="t.label"
            />
          </floating-label>
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

  const bizTypeOptions = [
    { value: 'social_capacity_audit', label: '社会运力准入审核' }
  ];

  const emit = defineEmits<{
    (
      e: 'search',
      where: { keyword: string; bizType: string | undefined }
    ): void;
  }>();

  const [form, resetFields] = useFormData<{
    keyword: string;
    bizType: string | undefined;
  }>({
    keyword: '',
    bizType: void 0
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };
</script>
