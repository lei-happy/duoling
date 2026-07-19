<!-- 意见反馈筛选 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.feedback_type"
            label="反馈类型"
            type="select"
            clearable
          >
            <el-option label="建议" :value="0" />
            <el-option label="缺陷" :value="1" />
            <el-option label="投诉" :value="2" />
            <el-option label="其他" :value="3" />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="处理状态"
            type="select"
            clearable
          >
            <el-option label="待处理" :value="0" />
            <el-option label="处理中" :value="1" />
            <el-option label="已解决" :value="2" />
            <el-option label="已关闭" :value="3" />
          </floating-label>
        </el-col>
        <el-col :lg="10" :md="16" :sm="24" :xs="24">
          <floating-label
            label="提交时间"
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
  import type { FeedbackParam } from '@/api/feedback/model';

  const emit = defineEmits<{
    (e: 'search', where?: FeedbackParam): void;
  }>();

  const [form, resetFields] = useFormData<FeedbackParam>({
    feedback_type: void 0,
    status: void 0
  });

  const dateRange = ref<[string, string] | string[]>(['', '']);

  const search = () => {
    const [d1, d2] = (dateRange.value || []) as string[];
    emit('search', {
      ...form,
      created_from: d1 ? `${d1} 00:00:00` : undefined,
      created_to: d2 ? `${d2} 23:59:59` : undefined
    });
  };

  const reset = () => {
    resetFields();
    dateRange.value = ['', ''];
    search();
  };
</script>
