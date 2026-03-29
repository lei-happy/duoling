<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="72px" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="16">
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <el-form-item label="手机号">
            <el-input
              clearable
              v-model.trim="form.phone"
              placeholder="请输入"
            />
          </el-form-item>
        </el-col>
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <el-form-item label="用途">
            <el-select
              clearable
              v-model="form.purpose"
              placeholder="全部"
              class="ele-fluid"
            >
              <el-option label="验证码登录" :value="1" />
              <el-option label="重置密码" :value="2" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <el-form-item label="状态">
            <el-select
              clearable
              v-model="form.status"
              placeholder="全部"
              class="ele-fluid"
            >
              <el-option label="未使用" :value="0" />
              <el-option label="已使用" :value="1" />
              <el-option label="已过期" :value="2" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :lg="8" :md="18" :sm="17" :xs="24">
          <el-form-item label="创建时间">
            <el-date-picker
              unlink-panels
              type="daterange"
              v-model="dateRange"
              range-separator="-"
              value-format="YYYY-MM-DD"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              class="ele-fluid"
            />
          </el-form-item>
        </el-col>
        <el-col :lg="4" :md="6" :sm="7" :xs="24">
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
  import { useFormData } from '@/utils/use-form-data';
  import type { SmsCodeParam } from '@/api/system/sms-code/model';

  const props = defineProps<{
    where?: SmsCodeParam;
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: SmsCodeParam): void;
  }>();

  const [form, resetFields] = useFormData<SmsCodeParam>({
    phone: '',
    purpose: undefined,
    status: undefined,
    ...(props.where || {})
  });

  const dateRange = ref<[string, string]>(['', '']);

  const search = () => {
    const [d1, d2] = dateRange.value || [];
    emit('search', {
      ...form,
      createTimeStart: d1 ? `${d1} 00:00:00` : '',
      createTimeEnd: d2 ? `${d2} 23:59:59` : ''
    });
  };

  const reset = () => {
    resetFields();
    dateRange.value = ['', ''];
    search();
  };
</script>
