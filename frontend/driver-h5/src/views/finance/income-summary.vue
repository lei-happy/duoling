<template>
  <PageContainer title="收入汇总与账户">
    <div class="page-body">
      <div class="card">
        <div class="section-title">收入汇总</div>
        <div class="summary-grid">
          <div class="cell">
            <div class="cell-label">累计收入</div>
            <div class="cell-val primary">¥{{ formatMoney(summary.totalIncome) }}</div>
          </div>
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
      </div>

      <div class="card">
        <div class="section-title">近 6 个月</div>
        <div v-if="summary.byMonth.length === 0" class="empty-block">
          <van-empty description="暂无数据" />
        </div>
        <div v-for="m in summary.byMonth" :key="m.month" class="month-row">
          <span>{{ m.month }}</span>
          <span class="amount">¥{{ formatMoney(m.amount) }}</span>
        </div>
      </div>

      <div class="card">
        <div class="section-title">我的收款账户</div>
        <div v-if="accounts.length === 0" class="empty-block">
          <van-empty description="暂未配置收款账户" />
        </div>
        <div v-for="a in accounts" :key="a.id" class="account-row">
          <div>
            <div class="acc-name">{{ a.accountName }}</div>
            <div class="acc-no">{{ maskBankAccount(a.accountNo) }}</div>
          </div>
          <div class="acc-type">{{ accountTypeLabel(a.accountType) }}</div>
        </div>
      </div>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import PageContainer from '@/components/PageContainer.vue';
import {
  getFinanceSummary,
  listMyAccounts,
  type DriverAccount,
  type FinanceSummary
} from '@/api/finance';
import { formatMoney, maskBankAccount } from '@/utils/format';

const summary = ref<FinanceSummary>({
  totalIncome: 0,
  prepaidAmount: 0,
  supplementAmount: 0,
  settledAmount: 0,
  byMonth: []
});
const accounts = ref<DriverAccount[]>([]);

function accountTypeLabel(t: number) {
  return { 1: '银行卡', 2: '油气款', 3: '积分' }[t] || '其他';
}

onMounted(async () => {
  const [s, a] = await Promise.all([getFinanceSummary().catch(() => summary.value), listMyAccounts().catch(() => [])]);
  summary.value = s;
  accounts.value = a;
});
</script>

<style lang="scss" scoped>
.page-body {
  padding-bottom: $spacing-xl;
}
.card {
  margin: $spacing-md;
  padding: $spacing-md $spacing-lg;
  background: #fff;
  border-radius: $border-radius-md;
  box-shadow: $shadow-card;
}
.section-title {
  font-weight: 600;
  margin-bottom: $spacing-sm;
}
.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-md;
  .cell {
    padding: $spacing-sm 0;
    border-radius: $border-radius-sm;
    .cell-label {
      font-size: $font-size-xs;
      color: $text-secondary;
    }
    .cell-val {
      font-size: $font-size-lg;
      font-weight: 600;
      margin-top: 4px;
      &.primary {
        color: $brand-primary;
        font-size: 22px;
      }
    }
  }
}
.month-row {
  display: flex;
  justify-content: space-between;
  padding: $spacing-sm 0;
  border-bottom: 1px dashed $border-color;
  &:last-child {
    border-bottom: none;
  }
  .amount {
    font-weight: 600;
    color: $brand-primary;
  }
}
.account-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md 0;
  border-bottom: 1px dashed $border-color;
  &:last-child {
    border-bottom: none;
  }
  .acc-name {
    font-weight: 500;
  }
  .acc-no {
    color: $text-secondary;
    font-size: $font-size-sm;
    margin-top: 2px;
  }
  .acc-type {
    background: rgba(29, 78, 216, 0.1);
    color: $brand-primary;
    padding: 2px 8px;
    border-radius: $border-radius-sm;
    font-size: $font-size-xs;
  }
}
.empty-block {
  padding: $spacing-md 0;
}
</style>
