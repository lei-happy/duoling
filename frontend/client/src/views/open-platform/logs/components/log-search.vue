<!-- 调用记录搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="能力编码，如 customer.query"
            type="input"
            v-model.trim="form.capability_code"
            clearable
          />
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
          <floating-label
            label="调用通道"
            type="select"
            v-model="form.channel"
            clearable
          >
            <el-option
              v-for="item in CHANNEL_OPTIONS"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </floating-label>
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
          <floating-label
            label="调用结果"
            type="select"
            v-model="form.status"
            clearable
          >
            <el-option
              v-for="item in CALL_STATUS_OPTIONS"
              :key="item.value"
              :label="item.label"
              :value="item.value"
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
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import type { CallLogParam } from '@/api/open-platform/model';
  import { CHANNEL_OPTIONS, CALL_STATUS_OPTIONS } from '../../constants';

  defineOptions({ name: 'OpenPlatformLogSearch' });

  const props = defineProps<{
    /** 默认搜索条件 */
    where?: CallLogParam;
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: CallLogParam): void;
  }>();

  /** 表单数据 */
  const [form, resetFields] = useFormData<CallLogParam>({
    capability_code: '',
    channel: '',
    status: '',
    ...(props.where || {})
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };
</script>
