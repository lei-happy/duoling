<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="72px" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="16">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <el-form-item label="机构名称">
            <el-input
              clearable
              v-model.trim="form.organizationName"
              placeholder="请输入"
            />
          </el-form-item>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <el-form-item label="机构类型">
            <dict-data
              code="organization_type"
              v-model="form.organizationType"
              placeholder="请选择"
            />
          </el-form-item>
        </el-col>
        <el-col :lg="12" :md="8" :sm="24" :xs="24">
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
  import { useFormData } from '@/utils/use-form-data';
  import type { OrganizationParam } from '@/api/system/organization/model';

  const emit = defineEmits<{
    (e: 'search', where?: OrganizationParam): void;
  }>();

  /** 表单数据 */
  const [form, resetFields] = useFormData<OrganizationParam>({
    organizationName: '',
    organizationFullName: '',
    organizationType: void 0
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
