<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form
      class="sms-code-search-form"
      label-width="0"
      @keyup.enter="search"
      @submit.prevent=""
    >
      <div class="sms-code-search-fields">
        <div class="sms-code-search-field">
          <floating-label
            label="请输入手机号"
            type="input"
            v-model.trim="form.phone"
            clearable
          />
        </div>
        <div class="sms-code-search-field">
          <floating-label
            label="请选择用途"
            type="select"
            v-model="form.purpose"
            clearable
          >
            <el-option label="验证码登录" :value="1" />
            <el-option label="重置密码" :value="2" />
            <el-option label="企业注册" :value="4" />
          </floating-label>
        </div>
        <div class="sms-code-search-field">
          <floating-label
            label="请选择状态"
            type="select"
            v-model="form.status"
            clearable
          >
            <el-option label="未使用" :value="0" />
            <el-option label="已使用" :value="1" />
            <el-option label="已过期" :value="2" />
          </floating-label>
        </div>
        <div class="sms-code-search-field sms-code-search-field--range">
          <floating-label
            label="创建时间"
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
        </div>
        <div class="sms-code-search-field sms-code-search-field--actions">
          <el-form-item label-width="0px">
            <btn-items
              :wrap="false"
              :items="[
                { preset: 'search', onClick: () => search() },
                { preset: 'reset', onClick: () => reset() }
              ]"
            />
          </el-form-item>
        </div>
      </div>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
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

<style lang="scss" scoped>
  .sms-code-search-fields {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px 16px;
  }

  .sms-code-search-field {
    flex: 1 1 200px;
    min-width: 0;
    max-width: 100%;
  }

  .sms-code-search-field--range {
    flex: 2 1 280px;
    min-width: 0;
  }

  .sms-code-search-field--actions {
    flex: 0 0 auto;
    margin-left: auto;
    display: flex;
    justify-content: flex-end;
    align-items: center;

    :deep(.el-form-item) {
      margin-bottom: 0;
    }
  }

  .sms-code-search-form {
    margin-bottom: 0;
  }
</style>
