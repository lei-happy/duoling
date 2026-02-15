<!-- 搜索表单 -->
<template>
  <el-form label-width="72px" @keyup.enter="search" @submit.prevent="">
    <el-row :gutter="16">
      <el-col :lg="6" :md="12" :sm="12" :xs="24">
        <el-form-item label="用户账号">
          <el-input
            clearable
            v-model.trim="form.username"
            placeholder="请输入"
          />
        </el-form-item>
      </el-col>
      <el-col :lg="6" :md="12" :sm="12" :xs="24">
        <el-form-item label="用户名">
          <el-input
            clearable
            v-model.trim="form.nickname"
            placeholder="请输入"
          />
        </el-form-item>
      </el-col>
      <el-col :lg="6" :md="12" :sm="12" :xs="24">
        <el-form-item label="性别">
          <dict-data code="sex" v-model="form.sex" placeholder="请选择" />
        </el-form-item>
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
</template>

<script lang="ts" setup>
  import { watch } from 'vue';
  import { useFormData } from '@/utils/use-form-data';
  import type { UserParam } from '@/api/system/user/model';

  const props = defineProps<{
    /** 机构 id */
    organizationId?: number;
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: UserParam): void;
  }>();

  /** 表单数据 */
  const [form, resetFields] = useFormData<UserParam>({
    username: '',
    nickname: '',
    sex: void 0
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

  /** 重置表单数据 */
  watch(
    () => props.organizationId,
    () => {
      resetFields();
    }
  );
</script>
