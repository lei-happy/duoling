<!-- 搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="姓名/手机号/编号"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="人事状态"
            type="select"
            clearable
          >
            <el-option label="在职" :value="1" />
            <el-option label="冻结" :value="0" />
            <el-option label="离职" :value="2" />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.operationStatus"
            label="运营状态"
            type="select"
            clearable
          >
            <el-option label="可接单" :value="1" />
            <el-option label="忙碌" :value="2" />
            <el-option label="休假" :value="3" />
            <el-option label="停运" :value="4" />
          </floating-label>
        </el-col>
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.driverType"
            label="司机类型"
            type="select"
            clearable
          >
            <el-option label="自有" :value="1" />
            <el-option label="外协" :value="2" />
            <el-option label="临时" :value="3" />
          </floating-label>
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
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
  import type { DriverParam } from '@/api/capacity/self_capacity/driver/model';

  const emit = defineEmits<{
    (e: 'search', where?: DriverParam): void;
  }>();

  const [form, resetFields] = useFormData<DriverParam>({
    keyword: '',
    status: void 0,
    operationStatus: void 0,
    driverType: void 0
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };
</script>
