<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入司机姓名/车牌号"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.action"
            label="请选择操作类型"
            type="select"
            clearable
          >
            <el-option label="上车" :value="1" />
            <el-option label="下车" :value="2" />
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
  import type { CapacityLogParam } from '@/api/capacity/model';

  const emit = defineEmits<{
    (e: 'search', where: Pick<CapacityLogParam, 'keyword' | 'action'>): void;
  }>();

  const [form, resetFields] = useFormData<{
    keyword: string;
    action: number | undefined;
  }>({
    keyword: '',
    action: void 0
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };
</script>
