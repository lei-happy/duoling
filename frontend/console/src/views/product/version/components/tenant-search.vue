<!-- 企业搜索表单 -->
<template>
  <ele-card search-form>
    <el-form @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="16">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入企业名称/编码/联系人"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请选择状态"
            type="select"
            v-model="form.status"
            clearable
          >
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="0" />
            <el-option label="待审核" :value="2" />
            <el-option label="已过期" :value="3" />
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
  import type { TenantParam } from '@/api/tenant/model';

  const emit = defineEmits<{
    (e: 'search', where?: TenantParam): void;
  }>();

  /** 表单数据 */
  const [form, resetFields] = useFormData<TenantParam>({
    keyword: '',
    status: void 0
  });

  /** 搜索 */
  const search = () => {
    emit('search', { ...form });
  };

  /** 重置 */
  const reset = () => {
    resetFields();
    search();
  };
</script>
