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
            label="请输入权限标识"
            type="input"
            v-model.trim="form.authority"
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
