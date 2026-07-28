<template>
  <div class="waybill-edit-step waybill-edit-step--basic">
    <el-row :gutter="12">
      <el-col :xs="24" :sm="12">
        <el-form-item prop="customerId">
          <floating-label
            v-model="form.customerId"
            label="请选择客户"
            type="select"
            filterable
            :filter-method="setCustomerFilter"
            clearable
            @change="emit('customer-change')"
          >
            <el-option
              v-for="item in customersShown"
              :key="item.id"
              :label="item.customerName"
              :value="item.id"
            />
          </floating-label>
        </el-form-item>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-form-item prop="waybillNo">
          <floating-label
            label="计划编号（唯一）"
            type="input"
            v-model.trim="form.waybillNo"
            clearable
          />
        </el-form-item>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-form-item prop="originCode">
          <floating-label
            label="请选择出发地"
            type="cascader"
            v-model="originCodesProxy"
            :cascader-options="regionTree"
            :cascader-option-props="regionCascaderProps"
            :cascader-filterable="true"
            @change="emit('origin-change', $event)"
          />
        </el-form-item>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-form-item prop="destinationCode">
          <floating-label
            label="请选择目的地"
            type="cascader"
            v-model="destCodesProxy"
            :cascader-options="regionTree"
            :cascader-option-props="regionCascaderProps"
            :cascader-filterable="true"
            @change="emit('dest-change', $event)"
          />
        </el-form-item>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-form-item prop="planIssueTime">
          <floating-label
            label="计划下达时间"
            type="date"
            date-type="datetime"
            v-model="form.planIssueTime"
            value-format="YYYY-MM-DD HH:mm:ss"
            clearable
          />
        </el-form-item>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-form-item prop="requiredDeliverTime">
          <floating-label
            label="要求送达时间"
            type="date"
            date-type="datetime"
            v-model="form.requiredDeliverTime"
            value-format="YYYY-MM-DD HH:mm:ss"
            clearable
          />
        </el-form-item>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { CascaderProps } from 'element-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import type { Waybill } from '@/api/waybill/model';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import type { RegionNavNode } from '@/api/basic-data/region/model';

  const props = defineProps<{
    form: Waybill;
    originCodes: string[];
    destCodes: string[];
    regionTree: RegionNavNode[];
    regionCascaderProps: CascaderProps;
    customersShown: CustomerSelectItem[];
    setCustomerFilter: (q: string) => void;
  }>();

  const emit = defineEmits<{
    (e: 'update:originCodes', v: string[]): void;
    (e: 'update:destCodes', v: string[]): void;
    (e: 'customer-change'): void;
    (e: 'origin-change', val: string[] | undefined): void;
    (e: 'dest-change', val: string[] | undefined): void;
  }>();

  const originCodesProxy = computed({
    get: () => props.originCodes,
    set: (v: string[]) => emit('update:originCodes', v ?? [])
  });

  const destCodesProxy = computed({
    get: () => props.destCodes,
    set: (v: string[]) => emit('update:destCodes', v ?? [])
  });
</script>
