<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="8" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.accountId"
            label="能源账户"
            type="select"
            filterable
            clearable
          >
            <el-option
              v-for="a in accounts"
              :key="a.id"
              :label="a.accountName"
              :value="a.id"
            />
          </floating-label>
        </el-col>
        <el-col :lg="8" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="状态"
            type="select"
            clearable
          >
            <el-option
              v-for="o in RECON_DOC_STATUSES"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </floating-label>
        </el-col>
        <el-col :lg="8" :md="8" :sm="12" :xs="24">
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
  import { RECON_DOC_STATUSES } from '../../_shared/options';

  export interface ReconSearchParam {
    accountId?: number;
    status?: number;
  }

  defineProps<{
    accounts: Array<{ id: number; accountName: string }>;
  }>();

  const emit = defineEmits<{
    (e: 'search', where?: ReconSearchParam): void;
  }>();

  const [form, resetFields] = useFormData<ReconSearchParam>({
    accountId: void 0,
    status: void 0
  });

  const search = () => emit('search', { ...form });
  const reset = () => {
    resetFields();
    search();
  };
</script>
