<template>
  <PageContainer title="我的账户">
    <!-- 余额卡片 -->
    <div
      class="fund-card"
      :class="{ frozen: account?.status === FUND_ACCOUNT_STATUS.FROZEN }"
    >
      <div class="fund-title">
        账户余额
        <span
          v-if="account?.status === FUND_ACCOUNT_STATUS.FROZEN"
          class="frozen-tag"
          >已冻结</span
        >
      </div>
      <div class="fund-amount">¥ {{ formatMoney(Math.abs(balanceNum)) }}</div>
      <div class="fund-hint">{{ balanceHint }}</div>
      <div class="fund-row">
        <div class="cell">
          <div class="cell-label">累计入账</div>
          <div class="cell-val">¥{{ formatMoney(account?.totalIn) }}</div>
        </div>
        <div class="cell">
          <div class="cell-label">累计出账</div>
          <div class="cell-val">¥{{ formatMoney(account?.totalOut) }}</div>
        </div>
      </div>
    </div>

    <div class="section-title">资金流水</div>
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div v-for="t in list" :key="t.id" class="txn-card">
          <div class="txn-row-1">
            <span class="txn-type">{{ bizTypeLabel(t.bizType) }}</span>
            <span
              class="txn-amount"
              :class="t.delta >= 0 ? 'in' : 'out'"
            >
              {{ t.delta >= 0 ? '+' : '-' }}¥{{ formatMoney(t.amount) }}
            </span>
          </div>
          <div class="txn-row-2">
            <span>{{ formatDate(t.createdAt) }}</span>
            <span>余额 ¥{{ formatMoney(t.balanceAfter) }}</span>
          </div>
          <div v-if="t.remark" class="txn-remark">{{ t.remark }}</div>
        </div>
        <van-empty v-if="list.length === 0 && !loading" description="暂无流水" />
      </van-list>
    </van-pull-refresh>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import PageContainer from '@/components/PageContainer.vue';
import {
  getMyFundAccount,
  listMyFundTransactions,
  type FundAccount,
  type FundTransaction
} from '@/api/finance';
import { formatDate, formatMoney } from '@/utils/format';
import {
  FUND_ACCOUNT_STATUS,
  fundBizTypeLabel
} from './fund-account.constants';

defineOptions({ name: 'FundAccount' });

const bizTypeLabel = fundBizTypeLabel;

const account = ref<FundAccount | null>(null);
const list = ref<FundTransaction[]>([]);
const loading = ref(false);
const finished = ref(false);
const refreshing = ref(false);
const page = ref(1);
const pageSize = 15;

const balanceNum = computed(() => Number(account.value?.balance ?? 0));
const balanceHint = computed(() => {
  if (balanceNum.value > 0) return '公司待付给您';
  if (balanceNum.value < 0) return '您暂占用公司预付款';
  return '账户已两清';
});

async function fetchAccount() {
  try {
    account.value = await getMyFundAccount();
  } catch (e) {
    console.error(e);
  }
}

async function onLoad() {
  try {
    const res = await listMyFundTransactions({ page: page.value, pageSize });
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
  Promise.all([fetchAccount(), (async () => reload())()]).finally(() => {
    refreshing.value = false;
  });
}

onMounted(() => {
  fetchAccount();
});
</script>

<style lang="scss" scoped>
.fund-card {
  margin: $spacing-md;
  background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
  color: #fff;
  border-radius: $border-radius-md;
  padding: $spacing-lg;
  &.frozen {
    background: linear-gradient(135deg, #6b7280 0%, #9ca3af 100%);
  }
  .fund-title {
    font-size: $font-size-sm;
    opacity: 0.9;
    display: flex;
    align-items: center;
    gap: 6px;
    .frozen-tag {
      background: rgba(255, 255, 255, 0.25);
      padding: 1px 6px;
      border-radius: $border-radius-sm;
      font-size: $font-size-xs;
    }
  }
  .fund-amount {
    font-size: 30px;
    font-weight: 600;
    margin: 6px 0 2px;
  }
  .fund-hint {
    font-size: $font-size-xs;
    opacity: 0.9;
    margin-bottom: $spacing-md;
  }
  .fund-row {
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
}
.section-title {
  margin: $spacing-md $spacing-md 0;
  font-size: $font-size-sm;
  color: $text-secondary;
}
.txn-card {
  margin: $spacing-sm $spacing-md 0;
  background: #fff;
  border-radius: $border-radius-md;
  padding: $spacing-md $spacing-lg;
  box-shadow: $shadow-card;
  .txn-row-1 {
    display: flex;
    justify-content: space-between;
    align-items: center;
    .txn-type {
      font-weight: 600;
    }
    .txn-amount {
      font-weight: 600;
      &.in {
        color: #16a34a;
      }
      &.out {
        color: #dc2626;
      }
    }
  }
  .txn-row-2 {
    display: flex;
    justify-content: space-between;
    margin-top: 6px;
    font-size: $font-size-xs;
    color: $text-muted;
  }
  .txn-remark {
    margin-top: 6px;
    font-size: $font-size-xs;
    color: $text-secondary;
  }
}
</style>
