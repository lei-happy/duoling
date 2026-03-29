<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="16">
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <floating-label
            label="请输入文件名称"
            type="input"
            v-model.trim="form.name"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <floating-label
            label="请输入文件路径"
            type="input"
            v-model.trim="form.path"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
          <floating-label
            label="请输入上传人"
            type="input"
            v-model.trim="form.createNickname"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="12" :sm="12" :xs="24">
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
  import type { FileRecordParam } from '@/api/system/file/model';

  const emit = defineEmits<{
    (e: 'search', where?: FileRecordParam): void;
  }>();

  /** 表单数据 */
  const [form, resetFields] = useFormData<FileRecordParam>({
    name: '',
    path: '',
    createNickname: ''
  });

  /** 搜索 */
  const search = () => {
    emit('search', { ...form });
  };

  /**  重置 */
  const reset = () => {
    resetFields();
    search();
  };
</script>
