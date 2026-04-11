<!-- 运单列表搜索 -->
<template>
  <ele-card search-form>
    <el-form label-width="0" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="运单编号/客户名称"
            type="input"
            v-model.trim="form.keyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.customerId"
            label="请选择客户"
            type="select"
            filterable
            clearable
          >
            <el-option
              v-for="item in customerOptions"
              :key="item.id"
              :label="item.customerName"
              :value="item.id"
            />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            v-model="form.status"
            label="请选择运单状态"
            type="select"
            clearable
          >
            <el-option label="待确认" :value="0" />
            <el-option label="已确认" :value="1" />
            <el-option label="已调度" :value="2" />
            <el-option label="运输中" :value="3" />
            <el-option label="已送达" :value="4" />
            <el-option label="已完成" :value="5" />
            <el-option label="已取消" :value="6" />
          </floating-label>
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="出发地"
            type="input"
            v-model.trim="form.originKeyword"
            clearable
          />
        </el-col>
      </el-row>
      <el-row :gutter="8" style="margin-top: 8px">
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="目的地"
            type="input"
            v-model.trim="form.destinationKeyword"
            clearable
          />
        </el-col>
        <el-col :lg="6" :md="8" :sm="12" :xs="24">
          <floating-label
            label="品牌/车型"
            type="input"
            v-model.trim="form.vehicleKeyword"
            clearable
          />
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
  import { ref, onMounted } from 'vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useFormData } from '@/utils/use-form-data';
  import { selectCustomers } from '@/api/partner/customer';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import type { WaybillParam } from '@/api/waybill/model';

  const emit = defineEmits<{
    (e: 'search', where?: WaybillParam): void;
  }>();

  const customerOptions = ref<CustomerSelectItem[]>([]);

  const [form, resetFields] = useFormData<{
    keyword: string;
    customerId: number | undefined;
    status: number | undefined;
    originKeyword: string;
    destinationKeyword: string;
    vehicleKeyword: string;
  }>({
    keyword: '',
    customerId: void 0,
    status: void 0,
    originKeyword: '',
    destinationKeyword: '',
    vehicleKeyword: ''
  });

  const search = () => {
    emit('search', { ...form });
  };

  const reset = () => {
    resetFields();
    search();
  };

  onMounted(async () => {
    try {
      customerOptions.value = (await selectCustomers()) ?? [];
    } catch (_) {
      customerOptions.value = [];
    }
  });
</script>
