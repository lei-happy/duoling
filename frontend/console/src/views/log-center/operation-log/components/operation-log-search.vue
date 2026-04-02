<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="16">
        <el-col :lg="4" :md="12" :sm="12" :xs="24">
          <floating-label
            label="租户"
            type="input"
            v-model.trim="form.tenantCode"
            clearable
          />
        </el-col>
        <el-col :lg="4" :md="12" :sm="12" :xs="24">
          <floating-label
            label="操作用户"
            type="input"
            v-model.trim="form.username"
            clearable
          />
        </el-col>
        <el-col :lg="4" :md="12" :sm="12" :xs="24">
          <floating-label
            label="操作模块"
            type="input"
            v-model.trim="form.module"
            clearable
          />
        </el-col>
        <el-col :lg="4" :md="12" :sm="12" :xs="24">
          <floating-label
            label="操作类型"
            type="input"
            v-model.trim="form.action"
            clearable
          />
        </el-col>
        <el-col :lg="5" :md="18" :sm="17" :xs="24">
          <floating-label
            label="操作时间"
            type="date"
            date-type="datetimerange"
            v-model="dateRange"
            range-separator="-"
            :value-format="DATE_TIME_FORMAT"
            :format="DATE_TIME_FORMAT"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            :unlink-panels="true"
            clearable
          />
        </el-col>
        <el-col :lg="3" :md="6" :sm="7" :xs="24">
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
  import { ref } from 'vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { DATE_TIME_FORMAT } from '@/utils/date-util';
  import type { TenantOperationLogParam } from '@/api/log-center/model';

  const emit = defineEmits<{
    (e: 'search', where?: TenantOperationLogParam): void;
  }>();

  const [form, resetFields] = useFormData<TenantOperationLogParam>({
    tenantCode: '',
    username: '',
    module: '',
    action: ''
  });

  const dateRange = ref<[string, string]>(['', '']);

  const search = () => {
    const [createTimeStart, createTimeEnd] = dateRange.value || [];
    emit('search', { ...form, createTimeStart, createTimeEnd });
  };

  const reset = () => {
    resetFields();
    dateRange.value = ['', ''];
    search();
  };
</script>
