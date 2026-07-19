<!-- 意见反馈搜索表单 -->
<template>
  <ele-card search-form>
    <el-form @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="16">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label label="关键词" v-model="form.keyword" clearable />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="处理状态"
            type="select"
            v-model="form.status"
            clearable
          >
            <el-option label="待处理" :value="0" />
            <el-option label="处理中" :value="1" />
            <el-option label="已解决" :value="2" />
            <el-option label="已关闭" :value="3" />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="反馈类型"
            type="select"
            v-model="form.feedback_type"
            clearable
          >
            <el-option label="建议" :value="0" />
            <el-option label="缺陷" :value="1" />
            <el-option label="投诉" :value="2" />
            <el-option label="其他" :value="3" />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="租户编码"
            v-model="form.tenant_code"
            clearable
          />
        </el-col>
        <el-col :lg="12" :md="16" :sm="24" :xs="24">
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
  import type { FeedbackParam } from '@/api/feedback/model';

  const emit = defineEmits<{
    (e: 'search', where?: FeedbackParam): void;
  }>();

  const [form, resetFields] = useFormData<FeedbackParam>({
    keyword: void 0,
    status: void 0,
    feedback_type: void 0,
    tenant_code: void 0
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };
</script>
