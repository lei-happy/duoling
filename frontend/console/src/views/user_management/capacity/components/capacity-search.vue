<template>
  <ele-card search-form>
    <el-form @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="16">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="司机姓名/手机号/车牌号"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="请选择状态"
            type="select"
            v-model="form.status"
            clearable
          >
            <el-option label="绑定中" :value="1" />
            <el-option label="已解绑" :value="0" />
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
  import type { PlatformCapacityParam } from '@/api/capacity/model';

  const emit = defineEmits<{
    (e: 'search', where?: PlatformCapacityParam): void;
  }>();

  const [form, resetFields] = useFormData<PlatformCapacityParam>({
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
