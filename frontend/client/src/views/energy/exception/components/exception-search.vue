<template>
  <ele-card search-form>
    <div class="stats">
      <span class="stats__item">待处理 {{ stats.pending || 0 }}</span>
      <span class="stats__item">已处理 {{ stats.processed || 0 }}</span>
      <span class="stats__item">已忽略 {{ stats.ignored || 0 }}</span>
    </div>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="8" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="处理状态"
            type="select"
            clearable
          >
            <el-option
              v-for="o in EXCEPTION_STATUSES"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </floating-label>
        </el-col>
        <el-col :lg="16" :md="16" :sm="12" :xs="24">
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
  import { EXCEPTION_STATUSES } from '../../_shared/options';

  export interface ExceptionSearchParam {
    status?: string;
  }

  defineProps<{
    stats: Record<string, number>;
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: ExceptionSearchParam): void;
  }>();

  const [form, resetFields] = useFormData<ExceptionSearchParam>({
    status: void 0
  });

  const search = () => emit('search', { ...form });
  const reset = () => {
    resetFields();
    search();
  };
</script>

<style scoped>
  .stats {
    display: flex;
    gap: 16px;
    margin-bottom: 12px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .stats__item {
    white-space: nowrap;
  }
</style>
