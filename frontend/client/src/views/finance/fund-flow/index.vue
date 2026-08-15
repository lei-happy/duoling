<template>
  <ele-page>
    <finance-kpi-cards :cards="kpiCards" />
    <fund-flow-search
      :accounts="accounts"
      @search="(next) => reload(next, 1)"
    />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="flowId"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="FinanceFundFlowTable"
      >
        <template #direction="{ row }">
          <el-tag
            :type="row.direction === 1 ? 'success' : 'warning'"
            size="small"
            effect="plain"
          >
            {{ row.direction === 1 ? '收款' : '付款' }}
          </el-tag>
        </template>

        <template #doc="{ row }">
          <div>{{ row.docNo || '--' }}</div>
          <div class="muted">
            {{ row.docKindLabel || '' }}
            <template v-if="row.batchDocNo">
              · 批次 {{ row.batchDocNo }}</template
            >
          </div>
        </template>

        <template #amount="{ row }">
          <span
            class="num-cell strong"
            :class="row.direction === 1 ? 'inflow' : 'outflow'"
          >
            {{ row.direction === 1 ? '+' : '-' }} {{ formatMoney(row.amount) }}
          </span>
        </template>

        <template #account="{ row }">
          <div>{{ row.bankAccountLabel || '--' }}</div>
          <div v-if="row.bankSerialNo" class="muted">
            流水号 {{ row.bankSerialNo }}
          </div>
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref } from 'vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import FinanceKpiCards from '../components/finance-kpi-cards.vue';
  import type { FinanceKpiCard } from '../components/finance-kpi-cards.vue';
  import FundFlowSearch from './components/fund-flow-search.vue';
  import { pageFundFlow } from '@/api/finance/payment-batch';
  import type {
    FundFlowParam,
    FundFlowSummary
  } from '@/api/finance/payment-batch/model';
  import { listBankAccountOptions } from '@/api/finance/bank-account';
  import type { BankAccountOption } from '@/api/finance/bank-account/model';
  import { formatDate } from '@/utils/date-util';
  import { formatMoney } from '../status-config';

  defineOptions({ name: 'FinanceFundFlow' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const where = reactive<FundFlowParam>({});
  const accounts = ref<BankAccountOption[]>([]);
  const summary = ref<FundFlowSummary>({
    inAmount: 0,
    outAmount: 0,
    netAmount: 0
  });

  const kpiCards = computed<FinanceKpiCard[]>(() => [
    {
      key: 'in',
      label: '当前筛选收款',
      value: formatMoney(summary.value.inAmount),
      unit: '元',
      type: 'success'
    },
    {
      key: 'out',
      label: '当前筛选付款',
      value: formatMoney(summary.value.outAmount),
      unit: '元',
      type: 'warning'
    },
    {
      key: 'net',
      label: '净流入',
      value: formatMoney(summary.value.netAmount),
      unit: '元',
      type: summary.value.netAmount >= 0 ? 'primary' : 'danger',
      hint: '只统计已登记到账与已打款成功的笔'
    }
  ]);

  const columns = computed<Columns>(() => [
    {
      prop: 'occurredAt',
      label: '发生时间',
      width: 165,
      align: 'center',
      formatter: (row) => formatDate(row.occurredAt) || '--'
    },
    {
      prop: 'direction',
      label: '方向',
      width: 90,
      align: 'center',
      slot: 'direction'
    },
    { columnKey: 'doc', label: '关联单据', minWidth: 190, slot: 'doc' },
    { prop: 'counterparty', label: '对方', minWidth: 150 },
    {
      columnKey: 'amount',
      label: '金额',
      width: 150,
      align: 'right',
      slot: 'amount'
    },
    { prop: 'methodLabel', label: '方式', width: 110, align: 'center' },
    { columnKey: 'account', label: '收付账户', minWidth: 180, slot: 'account' },
    { prop: 'remark', label: '备注', minWidth: 140 }
  ]);

  const datasource: DatasourceFunction = ({ pages, where: tableWhere }) => {
    return pageFundFlow({ ...(tableWhere || where), ...pages }).then((res) => {
      if (res?.summary) summary.value = res.summary;
      return { list: res?.list ?? [], count: res?.count ?? 0 };
    });
  };

  const reload = (next?: FundFlowParam, page?: number) => {
    if (next) Object.assign(where, next);
    tableRef.value?.reload?.({ where: { ...where }, page });
  };

  onMounted(async () => {
    try {
      accounts.value = await listBankAccountOptions();
    } catch {
      // 账户下拉失败不影响流水查询
    }
  });
</script>

<style lang="scss" scoped>
  .num-cell {
    font-variant-numeric: tabular-nums;
  }

  .strong {
    font-weight: 600;
  }

  .inflow {
    color: var(--el-color-success);
  }

  .outflow {
    color: var(--el-color-warning);
  }

  .muted {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }
</style>
