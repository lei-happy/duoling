<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="handleSearch" @submit.prevent="">
      <el-row :gutter="16">
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <floating-label
            label="请输入菜单名称"
            type="input"
            v-model.trim="form.title"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <floating-label
            label="请输入菜单地址"
            type="input"
            v-model.trim="form.path"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <floating-label
            label="请输入功能编码"
            type="input"
            v-model.trim="form.featureCode"
            clearable
          />
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
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
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
