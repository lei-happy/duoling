<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="80px" @keyup.enter="handleSearch" @submit.prevent="">
      <el-row :gutter="16">
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <el-form-item label="菜单名称">
            <el-input
              clearable
              v-model.trim="form.title"
              placeholder="请输入"
            />
          </el-form-item>
        </el-col>
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <el-form-item label="菜单地址">
            <el-input clearable v-model.trim="form.path" placeholder="请输入" />
          </el-form-item>
        </el-col>
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <el-form-item label="功能编码">
            <el-input
              clearable
              v-model.trim="form.featureCode"
              placeholder="请输入"
            />
          </el-form-item>
        </el-col>
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <el-form-item label-width="0px">
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
  import { useFormData } from '@/utils/use-form-data';
  import type { ClientMenuParam } from '@/api/system/client-menu/model';

  const emit = defineEmits<{
    (e: 'search', where?: ClientMenuParam): void;
  }>();

  const [form, resetFields] = useFormData<ClientMenuParam>({
    title: '',
    path: '',
    featureCode: ''
  });

  const handleSearch = () => {
    emit('search', { ...form });
  };

  const handleReset = () => {
    resetFields();
    handleSearch();
  };
</script>
