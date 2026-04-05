<template>
  <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
    <el-row :gutter="16">
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
          v-model="form.status"
          label="请选择状态"
          type="select"
          clearable
        >
          <el-option label="正常" :value="1" />
          <el-option label="停用" :value="0" />
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
</template>

<script lang="ts" setup>
  import { watch } from 'vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';

  const props = defineProps<{
    pcode?: number;
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: { name?: string; status?: number }): void;
  }>();

  const [form, resetFields] = useFormData({
    name: '',
    status: void 0 as number | undefined
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };

  watch(
    () => props.pcode,
    () => {
      resetFields();
    }
  );
</script>
