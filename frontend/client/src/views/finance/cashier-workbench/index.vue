<!--
  出纳工作台（文档 10 §一）

  一个岗位一个台：钱在哪、今天要打多少、有哪笔到账还没认领，都在这一页收口。
  各 Tab 的表格与操作放在子组件里，本页只管指标与切页。
-->
<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '12px' }">
      <finance-kpi-cards :cards="kpiCards" @select="onKpiSelect" />

      <el-tabs v-model="activeTab" class="page-tabs">
        <el-tab-pane name="pay">
          <template #label>
            待打款
            <el-badge
              v-if="overview.payablePendingCount"
              :value="overview.payablePendingCount"
              :max="99"
              class="tab-badge"
            />
          </template>
          <payable-candidates v-if="loadedTabs.pay" @done="refreshAll" />
        </el-tab-pane>

        <el-tab-pane name="batch">
          <template #label>
            打款批次
            <el-badge
              v-if="overview.batchWaitingCount"
              :value="overview.batchWaitingCount"
              :max="99"
              class="tab-badge"
            />
          </template>
          <payment-batch-list v-if="loadedTabs.batch" @done="refreshAll" />
        </el-tab-pane>

        <el-tab-pane name="claim">
          <template #label>
            待认领到账
            <el-badge
              v-if="overview.pendingClaimCount"
              :value="overview.pendingClaimCount"
              :max="99"
              class="tab-badge"
            />
          </template>
          <receipt-claim-panel v-if="loadedTabs.claim" @done="refreshAll" />
        </el-tab-pane>

        <el-tab-pane label="付款日历" name="calendar">
          <pay-calendar v-if="loadedTabs.calendar" />
        </el-tab-pane>
      </el-tabs>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import FinanceKpiCards from '../components/finance-kpi-cards.vue';
  import type { FinanceKpiCard } from '../components/finance-kpi-cards.vue';
  import PayableCandidates from './components/payable-candidates.vue';
  import PaymentBatchList from './components/payment-batch-list.vue';
  import ReceiptClaimPanel from './components/receipt-claim-panel.vue';
  import PayCalendar from './components/pay-calendar.vue';
  import { getCashierOverview } from '@/api/finance/payment-batch';
  import type { CashierOverview } from '@/api/finance/payment-batch/model';
  import { formatMoney } from '../status-config';

  defineOptions({ name: 'FinanceCashierWorkbench' });

  const activeTab = ref('pay');
  const loadedTabs = reactive<Record<string, boolean>>({ pay: true });

  const overview = ref<CashierOverview>({
    pendingClaimCount: 0,
    pendingClaimAmount: 0,
    todayReceivedAmount: 0,
    accountCount: 0,
    balanceTotal: 0,
    payablePendingCount: 0,
    payablePendingAmount: 0,
    payableOverdueCount: 0,
    batchWaitingCount: 0,
    batchWaitingAmount: 0,
    receivablePendingCount: 0,
    receivablePendingAmount: 0,
    todayPaidAmount: 0
  });

  const kpiCards = computed<FinanceKpiCard[]>(() => [
    {
      key: 'balance',
      label: '账面余额合计',
      value: formatMoney(overview.value.balanceTotal),
      unit: '元',
      type: 'primary',
      hint: `${overview.value.accountCount} 个启用账户`
    },
    {
      key: 'pay',
      label: '待打款',
      value: formatMoney(overview.value.payablePendingAmount),
      unit: '元',
      type: overview.value.payableOverdueCount ? 'danger' : 'warning',
      clickable: true,
      hint: overview.value.payableOverdueCount
        ? `${overview.value.payablePendingCount} 单，其中 ${overview.value.payableOverdueCount} 单已过账期`
        : `${overview.value.payablePendingCount} 单已审批未入批`
    },
    {
      key: 'batch',
      label: '在批待执行',
      value: formatMoney(overview.value.batchWaitingAmount),
      unit: '元',
      type: 'warning',
      clickable: true,
      hint: `${overview.value.batchWaitingCount} 个批次等打款`
    },
    {
      key: 'claim',
      label: '待认领到账',
      value: formatMoney(overview.value.pendingClaimAmount),
      unit: '元',
      type: 'success',
      clickable: true,
      hint: `${overview.value.pendingClaimCount} 笔到账没认领`
    },
    {
      key: 'today',
      label: '今日收 / 付',
      value: `${formatMoney(overview.value.todayReceivedAmount)} / ${formatMoney(
        overview.value.todayPaidAmount
      )}`,
      unit: '元',
      type: 'info'
    },
    {
      key: 'receivable',
      label: '已审批未收妥',
      value: formatMoney(overview.value.receivablePendingAmount),
      unit: '元',
      type: 'info',
      hint: `${overview.value.receivablePendingCount} 张结算单待收款`
    }
  ]);

  const onKpiSelect = (key: string) => {
    if (key === 'pay') activeTab.value = 'pay';
    else if (key === 'batch') activeTab.value = 'batch';
    else if (key === 'claim') activeTab.value = 'claim';
  };

  const loadOverview = async () => {
    try {
      const res = await getCashierOverview();
      if (res) overview.value = res;
    } catch (e: unknown) {
      EleMessage.error({
        message:
          (e as { message?: string }).message || '指标加载失败，请刷新重试',
        plain: true
      });
    }
  };

  const refreshAll = () => loadOverview();

  watch(activeTab, (tab) => {
    loadedTabs[tab] = true;
  });

  onMounted(loadOverview);
</script>

<style lang="scss" scoped>
  .page-tabs {
    :deep(.el-tabs__header) {
      margin-bottom: 12px;
    }
  }

  .tab-badge {
    margin-left: 4px;
    vertical-align: middle;
  }
</style>
