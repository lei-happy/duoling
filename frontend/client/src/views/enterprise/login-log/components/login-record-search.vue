<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入用户账号"
            type="input"
            v-model.trim="form.username"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入用户名"
            type="input"
            v-model.trim="form.nickname"
            clearable
          />
        </el-col>
        <el-col :lg="8" :md="12" :sm="12" :xs="24">
          <floating-label
            label="登录时间"
            type="date"
            date-type="daterange"
            v-model="dateRange"
            range-separator="-"
            value-format="YYYY-MM-DD"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
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
  import type { LoginRecordParam } from '@/api/logcenter/login-record/model';

  const props = defineProps<{
    /** 默认搜索条件 */
    where?: LoginRecordParam;
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: LoginRecordParam): void;
  }>();

  /** 表单数据 */
  const [form, resetFields] = useFormData<LoginRecordParam>({
    username: '',
    nickname: '',
    ...(props.where || {})
  });

  /** 日期范围 */
  const dateRange = ref<[string, string]>(['', '']);

  /** 搜索 */
  const search = () => {
    const [d1, d2] = dateRange.value || [];
    emit('search', {
      ...form,
      createTimeStart: d1 ? `${d1} 00:00:00` : '',
      createTimeEnd: d2 ? `${d2} 23:59:59` : ''
    });
  };

  /**  重置 */
  const reset = () => {
    resetFields();
    dateRange.value = ['', ''];
    search();
  };
</script>
