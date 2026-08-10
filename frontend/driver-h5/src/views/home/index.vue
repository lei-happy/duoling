<template>
  <PageContainer title="工作台" :show-tabbar="true" :hide-back="true">
    <div class="home">
      <!-- 顶部信息卡片 -->
      <div class="home-hero">
        <div class="hero-row">
          <div>
            <div class="hello">您好，{{ user.realName }}</div>
            <div class="tenant" @click="goSwitchTenant">
              <van-icon name="apartment-o" />
              <span class="tenant-name">{{ tenantName }}</span>
              <van-icon name="exchange" />
            </div>
          </div>
          <van-image
            v-if="user.userInfo?.avatar"
            round
            width="48"
            height="48"
            :src="user.userInfo.avatar"
          />
          <div v-else class="avatar-fallback">{{ user.realName.slice(0, 1) }}</div>
        </div>
        <div class="kpi-row">
          <div class="kpi" @click="goTask('1')">
            <div class="kpi-value">{{ kpi.waitLoad }}</div>
            <div class="kpi-label">待装车</div>
          </div>
          <div class="kpi" @click="goTask('3')">
            <div class="kpi-value">{{ kpi.inTransit }}</div>
            <div class="kpi-label">在途</div>
          </div>
          <div class="kpi" @click="goTask('4')">
            <div class="kpi-value">{{ kpi.waitSign }}</div>
            <div class="kpi-label">待交车</div>
          </div>
          <div class="kpi" @click="goFinance">
            <div class="kpi-value">¥{{ formatMoney(kpi.monthlyIncome) }}</div>
            <div class="kpi-label">本月收入</div>
          </div>
        </div>
      </div>

      <!-- 快捷入口 -->
      <div class="quick-entries card">
        <div class="entry" @click="goTask('1')">
          <van-icon name="logistics" />
          <span>我的任务</span>
        </div>
        <div class="entry" @click="goFinance">
          <van-icon name="balance-o" />
          <span>我的收入</span>
        </div>
        <div class="entry" @click="goAccounts">
          <van-icon name="bank-card" />
          <span>收款账户</span>
        </div>
        <div class="entry" @click="goProfile">
          <van-icon name="user-o" />
          <span>个人中心</span>
        </div>
      </div>

      <!-- 近期任务 -->
      <div class="section-header">
        <span>近期任务</span>
        <a class="more" @click="goTask()">全部 ›</a>
      </div>
      <div v-if="recent.length === 0" class="empty-block">
        <van-empty description="暂无任务" />
      </div>
      <TaskCard
        v-for="t in recent"
        :key="t.id"
        :task="t"
        @click="$router.push(`/task/${t.id}`)"
      />
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { onActivated, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import PageContainer from '@/components/PageContainer.vue';
import TaskCard from '@/components/TaskCard.vue';
import { useUserStore } from '@/store/user';
import { listMyTasks, type TaskListItem } from '@/api/task';
import { getFinanceSummary } from '@/api/finance';
import { formatMoney } from '@/utils/format';

const router = useRouter();
const user = useUserStore();

const tenantName = ref(user.userInfo?.tenantName || user.currentTenantCode || '');
const recent = ref<TaskListItem[]>([]);
const kpi = ref({ waitLoad: 0, inTransit: 0, waitSign: 0, monthlyIncome: 0 });
const loading = ref(false);

async function load() {
  if (loading.value) return;
  loading.value = true;
  try {
    const [r1, r2, r3, r4, summary] = await Promise.all([
      listMyTasks({ status: 1, page: 1, pageSize: 1 }),
      listMyTasks({ status: 3, page: 1, pageSize: 1 }),
      listMyTasks({ status: 4, page: 1, pageSize: 1 }),
      listMyTasks({ page: 1, pageSize: 5 }),
      getFinanceSummary().catch(() => ({
        totalIncome: 0,
        prepaidAmount: 0,
        supplementAmount: 0,
        settledAmount: 0,
        byMonth: []
      }))
    ]);
    kpi.value = {
      waitLoad: r1.total,
      inTransit: r2.total,
      waitSign: r3.total,
      monthlyIncome: summary.totalIncome
    };
    recent.value = r4.list;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
onActivated(load);

function goTask(status?: string) {
  router.push({ path: '/task', query: status ? { status } : undefined });
}
function goFinance() {
  router.push('/finance');
}
function goAccounts() {
  router.push('/finance/summary');
}
function goProfile() {
  router.push('/profile');
}
function goSwitchTenant() {
  router.push('/profile/switch-tenant');
}
</script>

<style lang="scss" scoped>
.home {
  padding-bottom: $spacing-xl;
}
.home-hero {
  background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%);
  color: #fff;
  padding: 20px $spacing-lg 24px;
  margin: 0 $spacing-md;
  margin-top: $spacing-md;
  border-radius: 14px;
  .hero-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
  }
  .hello {
    font-size: $font-size-lg;
    font-weight: 600;
  }
  .tenant {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-top: 4px;
    background: rgba(255, 255, 255, 0.18);
    padding: 3px 8px;
    border-radius: 10px;
    font-size: $font-size-xs;
  }
  .tenant-name {
    max-width: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .avatar-fallback {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.24);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 600;
  }
  .kpi-row {
    display: flex;
    background: rgba(255, 255, 255, 0.18);
    border-radius: 12px;
    padding: $spacing-md $spacing-sm;
  }
  .kpi {
    flex: 1;
    text-align: center;
    .kpi-value {
      font-size: 18px;
      font-weight: 600;
    }
    .kpi-label {
      font-size: $font-size-xs;
      opacity: 0.88;
      margin-top: 2px;
    }
    & + .kpi {
      border-left: 1px solid rgba(255, 255, 255, 0.24);
    }
  }
}
.quick-entries {
  margin: $spacing-md;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: $spacing-md;
  padding: $spacing-lg $spacing-md;
  .entry {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    font-size: $font-size-sm;
    color: $text-primary;
    :deep(.van-icon) {
      font-size: 24px;
      color: $brand-primary;
    }
  }
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-md $spacing-lg 0;
  font-size: $font-size-md;
  font-weight: 600;
  color: $text-primary;
  .more {
    font-size: $font-size-sm;
    color: $text-secondary;
    font-weight: 400;
  }
}
.empty-block {
  padding: $spacing-xl 0;
}
</style>
