<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="8" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入地区名称"
            type="input"
            v-model.trim="form.name"
            clearable
          />
        </el-col>
        <el-col :lg="8" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.source"
            label="请选择来源"
            type="select"
            clearable
          >
            <el-option label="系统内置" :value="0" />
            <el-option label="用户自定义" :value="1" />
          </floating-label>
        </el-col>
        <el-col :lg="8" :md="8" :sm="24" :xs="24">
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
  import { watch } from 'vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';

  const props = defineProps<{
    parentCode?: string;
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: { name?: string; source?: number }): void;
  }>();

  const [form, resetFields] = useFormData({
    name: '',
    source: void 0 as number | undefined
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };

  watch(
    () => props.parentCode,
    () => {
      resetFields();
    }
  );
</script>
