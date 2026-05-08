<!-- 承运商搜索表单 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="5" :md="8" :sm="12" :xs="24">
          <floating-label
            label="承运商名称/编码/联系人/电话"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.carrierType"
            label="承运商类型"
            type="select"
            clearable
          >
            <el-option label="公司车队" :value="0" />
            <el-option label="个体司机/小车队" :value="1" />
            <el-option label="其他" :value="2" />
          </floating-label>
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.inviteStatus"
            label="互联状态"
            type="select"
            clearable
          >
            <el-option label="未邀请" :value="0" />
            <el-option label="邀请中" :value="1" />
            <el-option label="已激活" :value="2" />
            <el-option label="A 已撤回" :value="5" />
            <el-option label="B 端解绑" :value="9" />
          </floating-label>
        </el-col>
        <el-col :lg="4" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="状态"
            type="select"
            clearable
          >
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="0" />
            <el-option label="黑名单" :value="2" />
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
  import type { CarrierParam } from '@/api/partner/carrier/model';

  const emit = defineEmits<{
    (e: 'search', where?: CarrierParam): void;
  }>();

  const [form, resetFields] = useFormData<CarrierParam>({
    keyword: '',
    carrierType: void 0,
    inviteStatus: void 0,
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
