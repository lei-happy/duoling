<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="72px" @keyup.enter="handleSearch" @submit.prevent="">
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
          <el-form-item label="权限标识">
            <el-input
              clearable
              v-model.trim="form.authority"
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
  import type { MenuParam } from '@/api/system/menu/model';

  const emit = defineEmits<{
    (e: 'search', where?: MenuParam): void;
  }>();

  /** 表单数据 */
  const [form, resetFields] = useFormData<MenuParam>({
    title: '',
    path: '',
    authority: ''
  });

  /** 搜索 */
  const handleSearch = () => {
    emit('search', { ...form });
  };

  /**  重置 */
  const handleReset = () => {
    resetFields();
    handleSearch();
  };
</script>
