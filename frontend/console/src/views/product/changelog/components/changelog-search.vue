<!-- 更新记录搜索表单 -->
<template>
  <ele-card search-form>
    <el-form @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="16">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请选择状态"
            type="select"
            v-model="form.status"
            clearable
          >
            <el-option label="已发布" :value="1" />
            <el-option label="停用" :value="0" />
          </floating-label>
        </el-col>
        <el-col :lg="12" :md="8" :sm="24" :xs="24">
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
  import type { ChangelogParam } from '@/api/changelog/model';

  const emit = defineEmits<{
    (e: 'search', where?: ChangelogParam): void;
  }>();

  /** 表单数据 */
  const [form, resetFields] = useFormData<ChangelogParam>({
    status: void 0
  });

  /** 搜索 */
  const search = () => {
    emit('search', { ...form });
  };

  /** 重置 */
  const reset = () => {
    resetFields();
    search();
  };
</script>
