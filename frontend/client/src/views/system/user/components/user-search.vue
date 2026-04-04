<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入手机号"
            type="input"
            v-model.trim="form.phone"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请输入用户名"
            type="input"
            v-model.trim="form.nickname"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.sex"
            label="请选择性别"
            type="select"
            clearable
          >
            <el-option
              v-for="item in sexDict"
              :key="item.dictDataCode"
              :label="item.dictDataName"
              :value="item.dictDataCode"
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
  import { watch } from 'vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { useDictData } from '@/utils/use-dict-data';
  import type { UserParam } from '@/api/system/user/model';

  const [sexDict] = useDictData(['sex']);

  const props = defineProps<{
    /** 机构 id */
    organizationId?: number;
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: UserParam): void;
  }>();

  /** 表单数据 */
  const [form, resetFields] = useFormData<UserParam>({
    phone: '',
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
