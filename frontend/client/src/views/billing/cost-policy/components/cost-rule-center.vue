<template>
  <div class="rule-center">
    <el-form :inline="true" @submit.prevent="">
      <el-form-item label="费用类型">
        <el-select
          v-model="where.feeType"
          placeholder="全部"
          clearable
          filterable
          style="width: 150px"
          @change="reload"
        >
          <el-option
            v-for="ft in meta.feeTypes"
            :key="ft.code"
            :label="ft.name"
            :value="ft.code"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="适用范围">
        <el-select
          v-model="where.scopeType"
          placeholder="全部"
          clearable
          style="width: 130px"
          @change="reload"
        >
          <el-option label="全局默认" :value="0" />
          <el-option label="指定承运商" :value="1" />
          <el-option label="指定司机" :value="2" />
          <el-option label="指定运力" :value="3" />
        </el-select>
      </el-form-item>
      <el-form-item label="承运类型">
        <el-select
          v-model="where.carrierType"
          placeholder="全部"
          clearable
          style="width: 120px"
          @change="reload"
        >
          <el-option label="自有车" :value="1" />
          <el-option label="承运商" :value="2" />
          <el-option label="社会运力" :value="3" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select
          v-model="where.status"
          placeholder="全部"
          clearable
          style="width: 100px"
          @change="reload"
        >
          <el-option label="启用" :value="1" />
          <el-option label="停用" :value="0" />
        </el-select>
      </el-form-item>
      <el-form-item label="关键字">
        <el-input
          v-model="where.keyword"
          placeholder="政策/线路/费用名"
          clearable
          style="width: 170px"
          @keyup.enter="reload"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="reload">查询</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="list" v-loading="loading" border size="small">
      <el-table-column label="费用类型" min-width="110">
        <template #default="{ row }">
          {{ row.feeName || row.feeType }}
        </template>
      </el-table-column>
      <el-table-column label="所属政策" min-width="180">
        <template #default="{ row }">
          <el-button link type="primary" @click="emit('open-policy', row)">
            {{ row.policyName }}
          </el-button>
          <div class="policy-no">{{ row.policyNo }}</div>
        </template>
      </el-table-column>
      <el-table-column label="范围" width="120" align="center">
        <template #default="{ row }">
          {{ scopeLabel(row.policyScopeType) }}
        </template>
      </el-table-column>
      <el-table-column label="承运类型" width="90" align="center">
        <template #default="{ row }">
          {{ carrierLabel(row.policyCarrierType) }}
        </template>
      </el-table-column>
      <el-table-column label="方向" width="70" align="center">
        <template #default="{ row }">
          <el-tag
            :type="row.direction === 1 ? 'success' : 'warning'"
            size="small"
          >
            {{ row.direction === 1 ? '加项' : '扣减' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="计价方式" width="100" align="center">
        <template #default="{ row }">
          {{ pricingLabel(row.pricingMethod) }}
        </template>
      </el-table-column>
      <el-table-column prop="unitPrice" label="单价" width="90" align="right" />
      <el-table-column label="线路" min-width="140">
        <template #default="{ row }">
          <span v-if="row.origin || row.destination">
            {{ row.origin || '任意' }} → {{ row.destination || '任意' }}
          </span>
          <span v-else>不限</span>
        </template>
      </el-table-column>
      <el-table-column label="生效期" min-width="180" align="center">
        <template #default="{ row }">
          {{ row.policyEffectiveDate || '-' }} ~
          {{ row.policyExpiryDate || '长期' }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="70" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
            {{ row.status === 1 ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
  import { reactive, ref, onMounted } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { listCostRulesCrossPolicy } from '@/api/billing/cost-policy';
  import type {
    CostMeta,
    CostRuleCenterParam,
    CostRuleWithPolicy
  } from '@/api/billing/cost-policy/model';

  const props = defineProps<{
    meta: CostMeta;
  }>();

  const emit = defineEmits<{
    (e: 'open-policy', row: CostRuleWithPolicy): void;
  }>();

  const list = ref<CostRuleWithPolicy[]>([]);
  const loading = ref(false);
  const where = reactive<CostRuleCenterParam>({});

  const scopeLabel = (t?: number) =>
    t == null
      ? '-'
      : ({ 0: '全局默认', 1: '指定承运商', 2: '指定司机', 3: '指定运力' }[t] ??
        '-');
  const carrierLabel = (t?: number | null) =>
    t == null
      ? '不限'
      : ({ 1: '自有车', 2: '承运商', 3: '社会运力' }[t] ?? '-');
  const pricingLabel = (v: string) =>
    props.meta.pricingMethods.find((p) => p.value === v)?.label ?? v;

  const reload = async () => {
    loading.value = true;
    try {
      list.value = (await listCostRulesCrossPolicy({ ...where })) ?? [];
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const resetSearch = () => {
    where.feeType = undefined;
    where.scopeType = undefined;
    where.carrierType = undefined;
    where.status = undefined;
    where.keyword = undefined;
    reload();
  };

  defineExpose({ reload });

  onMounted(reload);
</script>

<style scoped>
  .policy-no {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
</style>
