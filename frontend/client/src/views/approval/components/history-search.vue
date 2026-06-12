<!-- 审批历史搜索 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入单号/发起人"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.bizType"
            label="请选择审批场景"
            type="select"
            clearable
          >
            <el-option
              v-for="item in BIZ_TYPE_OPTIONS"
              :key="item.value"
              :value="item.value"
              :label="item.label"
            />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="请选择状态"
            type="select"
            clearable
          >
            <el-option
              v-for="item in INSTANCE_STATUS_OPTIONS"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
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
  import type { ApprovalListParam } from '@/api/approval/model';
  import { BIZ_TYPE_OPTIONS, INSTANCE_STATUS_OPTIONS } from '../constants';

  const emit = defineEmits<{
    (
      e: 'search',
      where: Pick<ApprovalListParam, 'keyword' | 'bizType' | 'status'>
    ): void;
  }>();

  const [form, resetFields] = useFormData<{
    keyword: string;
    bizType: string | undefined;
    status: number | undefined;
  }>({
    keyword: '',
    bizType: void 0,
    status: void 0
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };
</script>
