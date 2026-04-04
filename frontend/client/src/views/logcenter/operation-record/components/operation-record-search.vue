<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入操作用户"
            type="input"
            v-model.trim="form.username"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入操作模块"
            type="input"
            v-model.trim="form.module"
            clearable
          />
        </el-col>
        <el-col :lg="8" :md="12" :sm="12" :xs="24">
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
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
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
  import type { OperationRecordParam } from '@/api/system/operation-record/model';

  const emit = defineEmits<{
    (e: 'search', where?: OperationRecordParam): void;
  }>();

  /** 表单数据 */
  const [form, resetFields] = useFormData<OperationRecordParam>({
    username: '',
    module: ''
  });

  /** 日期范围 */
  const dateRange = ref<[string, string]>(['', '']);

  /** 搜索 */
  const search = () => {
    const [createTimeStart, createTimeEnd] = dateRange.value || [];
    emit('search', { ...form, createTimeStart, createTimeEnd });
  };

  /**  重置 */
  const reset = () => {
    resetFields();
    dateRange.value = ['', ''];
    search();
  };
</script>
