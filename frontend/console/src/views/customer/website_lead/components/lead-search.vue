<!-- 官网线索搜索表单 -->
<template>
  <ele-card search-form>
    <el-form @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="16">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="企业 / 联系人 / 手机号"
            v-model="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="跟进状态"
            type="select"
            v-model="form.status"
            clearable
          >
            <el-option
              v-for="o in STATUS_OPTIONS"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="测评档位"
            type="select"
            v-model="form.stage_band"
            clearable
          >
            <el-option v-for="b in STAGE_BANDS" :key="b" :label="b" :value="b" />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="车队规模"
            type="select"
            v-model="form.fleet_size"
            clearable
          >
            <el-option
              v-for="o in FLEET_OPTIONS"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </floating-label>
        </el-col>
        <el-col :lg="12" :md="16" :sm="24" :xs="24">
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
  import type { WebsiteLeadParam } from '@/api/website-lead/model';
  import { FLEET_OPTIONS, STAGE_BANDS, STATUS_OPTIONS } from '../constants';

  const emit = defineEmits<{
    (e: 'search', where?: WebsiteLeadParam): void;
  }>();

  const [form, resetFields] = useFormData<WebsiteLeadParam>({
    keyword: void 0,
    status: void 0,
    stage_band: void 0,
    fleet_size: void 0
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };
</script>
