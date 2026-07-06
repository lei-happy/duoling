<template>
  <PageContainer title="我的收入" :show-tabbar="true" :hide-back="true">
    <!-- 顶部汇总卡片 -->
    <div class="summary-card">
      <div class="summary-title">本月累计收入</div>
      <div class="summary-amount">¥ {{ formatMoney(summary.totalIncome) }}</div>
      <div class="summary-row">
        <div class="cell">
          <div class="cell-label">预付</div>
          <div class="cell-val">¥{{ formatMoney(summary.prepaidAmount) }}</div>
        </div>
        <div class="cell">
          <div class="cell-label">补款</div>
          <div class="cell-val">¥{{ formatMoney(summary.supplementAmount) }}</div>
        </div>
        <div class="cell">
          <div class="cell-label">结算</div>
          <div class="cell-val">¥{{ formatMoney(summary.settledAmount) }}</div>
        </div>
      </div>
      <div class="summary-entry" @click="$router.push('/finance/fund-account')">
        <span>我的资金账户（往来账）</span>
        <van-icon name="arrow" />
      </div>
    </div>

    <van-tabs v-model:active="docType" sticky @change="reload">
      <van-tab title="全部" name="" />
      <van-tab title="预付单" name="1" />
      <van-tab title="补款单" name="2" />
      <van-tab title="结算单" name="3" />
    </van-tabs>

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div v-for="d in list" :key="d.id" class="finance-card" @click="$router.push(`/finance/${d.id}`)">
          <div class="row-1">
            <span class="doc-no">{{ d.docNo }}</span>
            <StatusTag
              :label="FINANCE_STATUS[d.status]?.label || '未知'"
              :level="FINANCE_STATUS[d.status]?.level || 'default'"
            />
          </div>
          <div class="row-2">
            <span class="tag">{{ FINANCE_DOC_TYPE[d.docType] }}</span>
            <span class="task-no">关联任务：{{ d.taskNo || d.taskId }}</span>
          </div>
          <div class="row-3">
            <div class="amount">
              <span class="amount-label">实付</span>
              <span class="amount-val">¥{{ formatMoney(d.actualAmount ?? d.plannedAmount) }}</span>
            </div>
            <div class="time">{{ formatDate(d.actualPayTime || d.plannedPayTime) }}</div>
          </div>
        </div>
        <van-empty v-if="list.length === 0 && !loading" description="暂无费用单" />
      </van-list>
    </van-pull-refresh>
  </PageContainer>
</template>

<script setup lang="ts">
import { onActivated, onMounted, ref } from 'vue';
import PageContainer from '@/components/PageContainer.vue';
import StatusTag from '@/components/StatusTag.vue';
import {
  getFinanceSummary,
  listMyFinance,
  type FinanceDocItem,
  type FinanceSummary
} from '@/api/finance';
import { FINANCE_DOC_TYPE, FINANCE_STATUS } from '@/views/task/status-config';
import { formatDate, formatMoney } from '@/utils/format';

defineOptions({ name: 'FinanceList' });

const docType = ref<string>('');
const list = ref<FinanceDocItem[]>([]);
const loading = ref(false);
const finished = ref(false);
const refreshing = ref(false);
const page = ref(1);
const pageSize = 15;

const summary = ref<FinanceSummary>({
  totalIncome: 0,
  prepaidAmount: 0,
  supplementAmount: 0,
  settledAmount: 0,
  byMonth: []
});

async function fetchSummary() {
  try {
    summary.value = await getFinanceSummary();
  } catch (e) {
    console.error(e);
  }
}

async function onLoad() {
  try {
    const res = await listMyFinance({
      page: page.value,
      pageSize,
      docType: docType.value ? Number(docType.value) : undefined
    });
    list.value.push(...res.list);
    page.value += 1;
    finished.value = list.value.length >= res.total;
  } finally {
    loading.value = false;
  }
}

function reload() {
  page.value = 1;
  list.value = [];
  finished.value = false;
  loading.value = true;
  onLoad();
}

function onRefresh() {
  refreshing.value = true;
  Promise.all([fetchSummary(), (async () => reload())()]).finally(() => {
    refreshing.value = false;
  });
}

onMounted(() => {
  fetchSummary();
});
onActivated(() => {
  fetchSummary();
});
</script>

<style lang="scss" scoped>
.summary-card {
  margin: $spacing-md;
  background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%);
  color: #fff;
  border-radius: $border-radius-md;
  padding: $spacing-lg;
  .summary-title {
    font-size: $font-size-sm;
    opacity: 0.88;
  }
  .summary-amount {
    font-size: 28px;
    font-weight: 600;
    margin: 6px 0 $spacing-md;
  }
  .summary-row {
    display: flex;
    .cell {
      flex: 1;
      text-align: center;
      & + .cell {
        border-left: 1px solid rgba(255, 255, 255, 0.24);
      }
      .cell-label {
        font-size: $font-size-xs;
        opacity: 0.88;
      }
      .cell-val {
        font-size: $font-size-lg;
        font-weight: 600;
        margin-top: 2px;
      }
    }
  }
  .summary-entry {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: $spacing-md;
    padding-top: $spacing-md;
    border-top: 1px solid rgba(255, 255, 255, 0.24);
    font-size: $font-size-sm;
  }
}
.finance-card {
  margin: $spacing-md $spacing-md 0;
  background: #fff;
  border-radius: $border-radius-md;
  padding: $spacing-md $spacing-lg;
  box-shadow: $shadow-card;
  .row-1 {
    display: flex;
    justify-content: space-between;
    align-items: center;
    .doc-no {
      font-weight: 600;
    }
  }
  .row-2 {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    margin-top: 6px;
    font-size: $font-size-sm;
    color: $text-secondary;
    .tag {
      background: rgba(29, 78, 216, 0.1);
      color: $brand-primary;
      padding: 2px 6px;
      border-radius: $border-radius-sm;
      font-size: $font-size-xs;
    }
  }
  .row-3 {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-top: $spacing-sm;
    .amount-label {
      font-size: $font-size-xs;
      color: $text-secondary;
      margin-right: 4px;
    }
    .amount-val {
      font-size: $font-size-lg;
      font-weight: 600;
      color: $brand-primary;
    }
    .time {
      font-size: $font-size-xs;
      color: $text-muted;
    }
  }
}
</style>
