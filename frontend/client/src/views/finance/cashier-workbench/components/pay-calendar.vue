<!-- 付款日历：未来若干天要准备多少钱，按天看资金缺口 -->
<template>
  <div>
    <div class="panel-toolbar">
      <el-radio-group v-model="days" @change="load">
        <el-radio-button :value="7">未来 7 天</el-radio-button>
        <el-radio-button :value="14">未来 14 天</el-radio-button>
        <el-radio-button :value="30">未来 30 天</el-radio-button>
      </el-radio-group>
      <span class="toolbar-tip">
        合计需备资金 ¥ {{ formatMoney(totalAmount) }}
      </span>
    </div>

    <div v-loading="loading" class="cal-grid">
      <div
        v-for="d in rows"
        :key="d.date"
        class="cal-day"
        :class="{ 'is-heavy': d.totalAmount > 0 }"
      >
        <div class="cal-date">
          {{ d.date.slice(5) }}
          <span class="cal-week">{{ weekLabel(d.date) }}</span>
        </div>
        <div class="cal-amount">
          {{ d.totalAmount > 0 ? `¥ ${formatMoney(d.totalAmount)}` : '—' }}
        </div>
        <div v-if="d.batchCount || d.docCount" class="cal-detail">
          <span v-if="d.batchCount">批次 {{ d.batchCount }}</span>
          <span v-if="d.docCount">应付 {{ d.docCount }}</span>
        </div>
      </div>
      <div v-if="!rows.length && !loading" class="cal-empty">
        近期没有需要准备资金的付款计划
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { getPayCalendar } from '@/api/finance/payment-batch';
  import type { PayCalendarDay } from '@/api/finance/payment-batch/model';
  import { formatMoney } from '../../status-config';

  const WEEK = ['日', '一', '二', '三', '四', '五', '六'];

  const loading = ref(false);
  const days = ref(14);
  const rows = ref<PayCalendarDay[]>([]);

  const totalAmount = computed(() =>
    rows.value.reduce((s, r) => s + Number(r.totalAmount || 0), 0)
  );

  const weekLabel = (date: string) => `周${WEEK[new Date(date).getDay()]}`;

  const load = async () => {
    loading.value = true;
    try {
      rows.value = await getPayCalendar({ days: days.value });
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '加载失败，请重试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  onMounted(load);
</script>

<style lang="scss" scoped>
  .panel-toolbar {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 12px;
  }

  .toolbar-tip {
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .cal-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(132px, 1fr));
    gap: 10px;
    min-height: 120px;
  }

  .cal-day {
    padding: 10px 12px;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 6px;

    &.is-heavy {
      border-color: var(--el-color-warning-light-5);
      background: var(--el-color-warning-light-9);
    }
  }

  .cal-date {
    display: flex;
    align-items: baseline;
    gap: 6px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .cal-week {
    font-size: 12px;
  }

  .cal-amount {
    margin-top: 6px;
    font-size: 16px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }

  .cal-detail {
    display: flex;
    gap: 8px;
    margin-top: 4px;
    color: var(--el-text-color-placeholder);
    font-size: 12px;
  }

  .cal-empty {
    grid-column: 1 / -1;
    padding: 28px 0;
    color: var(--el-text-color-secondary);
    text-align: center;
  }
</style>
