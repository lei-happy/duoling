<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="16">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入机构名称"
            type="input"
            v-model.trim="form.organizationName"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请选择机构类型"
            type="select"
            v-model="form.organizationType"
            clearable
          >
            <el-option
              v-for="item in organizationTypeDicts"
              :key="item.dictDataCode"
              :label="item.dictDataName"
              :value="item.dictDataCode"
            />
          </floating-label>
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
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { useDictData } from '@/utils/use-dict-data';
  import type { OrganizationParam } from '@/api/system/organization/model';

  const emit = defineEmits<{
    (e: 'search', where?: OrganizationParam): void;
  }>();

  const [organizationTypeDicts] = useDictData(['organization_type']);

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
