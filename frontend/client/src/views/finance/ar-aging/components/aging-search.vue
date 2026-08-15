<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="客户名称"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.creditStatus"
            label="信用状态"
            type="select"
            clearable
          >
            <el-option
              v-for="o in CREDIT_STATUS_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.bucket"
            label="账龄档"
            type="select"
            clearable
          >
            <el-option
              v-for="(label, idx) in bucketLabels"
              :key="idx"
              :value="idx"
              :label="label"
            />
          </floating-label>
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.baseDate"
            label="统计基准日"
            type="date"
            date-type="date"
            value-format="YYYY-MM-DD"
          />
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
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
        <el-col :span="24">
          <div class="search-flags">
            <el-checkbox v-model="form.onlyOverdue">只看逾期</el-checkbox>
            <el-checkbox v-model="form.onlyExceeded">只看超额度</el-checkbox>
          </div>
        </el-col>
      </el-row>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import type { AgingParam } from '@/api/finance/ar-aging/model';
  import { CREDIT_STATUS_OPTIONS } from '../../status-config';

  defineProps<{
    bucketLabels: string[];
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: AgingParam): void;
  }>();

  const [form, resetFields] = useFormData<AgingParam>({
    keyword: '',
    creditStatus: void 0,
    bucket: void 0,
    baseDate: void 0,
    onlyOverdue: false,
    onlyExceeded: false
  });

  const toWhere = (): AgingParam => ({
    keyword: form.keyword || void 0,
    creditStatus: form.creditStatus,
    bucket: form.bucket,
    baseDate: form.baseDate,
    onlyOverdue: form.onlyOverdue || void 0,
    onlyExceeded: form.onlyExceeded || void 0
  });

  const search = () => emit('search', toWhere());
  const reset = () => {
    resetFields();
    search();
  };

  defineExpose({
    applyFlags(next: Partial<AgingParam>) {
      Object.assign(form, {
        onlyOverdue: false,
        onlyExceeded: false,
        bucket: void 0,
        ...next
      });
      search();
    }
  });
</script>

<style scoped lang="scss">
  @use '../../_shared/ui.scss';
</style>
