<!-- 挂车列表搜索 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入挂车车牌号"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="请选择状态"
            type="select"
            clearable
          >
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="0" />
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
  import type { TrailerParam } from '@/api/resource/trailer/model';

  const emit = defineEmits<{
    (e: 'search', where: Pick<TrailerParam, 'keyword' | 'status'>): void;
  }>();

  const [form, resetFields] = useFormData<{
    keyword: string;
    status: number | undefined;
  }>({
    keyword: '',
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
