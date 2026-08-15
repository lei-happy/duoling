<template>
  <ele-page>
    <finance-kpi-cards :cards="kpiCards" @select="onKpiSelect" />

    <ele-card class="chart-card" :body-style="{ paddingTop: '10px' }">
      <div class="chart-head">
        <span class="chart-title">账龄分布</span>
        <span class="chart-sub">
          统计基准日 {{ summary?.baseDate || where.baseDate || '今天' }}
          <template v-if="summary?.bucketLabels?.length">
            · 分档 {{ summary.bucketLabels.join(' / ') }}
          </template>
        </span>
      </div>
      <div class="chart-body" v-loading="summaryLoading">
        <v-chart
          ref="chartRef"
          :option="chartOption"
          class="chart-inner"
          autoresize
        />
        <div v-if="!hasBucketData && !summaryLoading" class="chart-empty">
          当前没有未收余额，账龄分布为空
        </div>
      </div>
    </ele-card>

    <aging-search
      ref="searchRef"
      :bucket-labels="bucketLabels"
      @search="onSearch"
    />

    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="customerId"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="FinanceArAgingTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'export',
                title: '导出',
                permission: 'finance:ar-aging:export',
                onClick: exportList
              }
            ]"
          />
        </template>

        <template #customer="{ row }">
          <div class="cust-name">{{
            row.customerName || `客户 ${row.customerId}`
          }}</div>
          <div class="cust-tags">
            <el-tag
              v-if="row.creditStatus !== 1"
              :type="
                (CREDIT_STATUS_MAP[row.creditStatus]?.type as any) || 'info'
              "
              size="small"
              effect="plain"
            >
              {{ row.creditStatusLabel }}
            </el-tag>
            <el-tag
              v-if="row.exceeded"
              type="danger"
              size="small"
              effect="plain"
            >
              超额 {{ formatMoney(row.exceededAmount) }}
            </el-tag>
          </div>
        </template>

        <template #unpaid="{ row }">
          <span class="num strong">¥ {{ formatMoney(row.unpaidAmount) }}</span>
        </template>

        <template #overdue="{ row }">
          <span class="num" :class="{ danger: row.overdueAmount > 0 }">
            ¥ {{ formatMoney(row.overdueAmount) }}
          </span>
          <div v-if="row.maxOverdueDays > 0" class="muted">
            最长 {{ row.maxOverdueDays }} 天
          </div>
        </template>

        <template
          v-for="(_, idx) in bucketLabels"
          :key="idx"
          #[`bucket${idx}`]="{ row }"
        >
          <span class="num">
            {{
              bucketAmount(row, idx)
                ? formatMoney(bucketAmount(row, idx))
                : '--'
            }}
          </span>
        </template>

        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :wrap="false"
            :items="actionItems(row)"
          />
        </template>
      </ele-pro-table>
    </ele-card>

    <aging-detail-drawer
      v-model:visible="detailVisible"
      :customer-id="detailCustomerId"
      :base-date="where.baseDate"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref } from 'vue';
  import { useRoute } from 'vue-router';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type { ButtonItem } from 'ele-admin-plus/es/ele-buttons/types';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { use } from 'echarts/core';
  import type { EChartsCoreOption } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { BarChart } from 'echarts/charts';
  import { GridComponent, TooltipComponent } from 'echarts/components';
  import VChart from 'vue-echarts';
  import { EyeOutlined } from '@/components/icons';
  import { useEcharts } from '@/utils/use-echarts';
  import FinanceKpiCards from '../components/finance-kpi-cards.vue';
  import type { FinanceKpiCard } from '../components/finance-kpi-cards.vue';
  import AgingDetailDrawer from './components/aging-detail-drawer.vue';
  import AgingSearch from './components/aging-search.vue';
  import {
    exportAging,
    getAgingSummary,
    pageAging
  } from '@/api/finance/ar-aging';
  import type {
    AgingCustomerRow,
    AgingParam,
    AgingSummary
  } from '@/api/finance/ar-aging/model';
  import { buildActionColumnItems } from '../_shared/action-column';
  import {
    CREDIT_STATUS_MAP,
    formatMoney
  } from '../status-config';

  defineOptions({ name: 'FinanceArAging' });

  use([CanvasRenderer, BarChart, GridComponent, TooltipComponent]);

  const route = useRoute();
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const searchRef = ref<InstanceType<typeof AgingSearch> | null>(null);
  const chartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([chartRef]);

  const where = reactive<AgingParam>({});
  const summary = ref<AgingSummary | null>(null);
  const summaryLoading = ref(false);
  const bucketLabels = ref<string[]>([]);

  const detailVisible = ref(false);
  const detailCustomerId = ref<number | null>(null);

  const chartOption: EChartsCoreOption = reactive({});

  const hasBucketData = computed(() =>
    (summary.value?.bucketDistribution || []).some((b) => b.amount > 0)
  );

  const kpiCards = computed<FinanceKpiCard[]>(() => {
    const k = summary.value?.kpi;
    return [
      {
        key: 'total',
        label: '未收余额',
        value: `¥ ${formatMoney(k?.totalUnpaid ?? 0)}`,
        type: 'primary',
        hint: `${k?.settleCount ?? 0} 张结算单 · ${k?.customerCount ?? 0} 个客户`
      },
      {
        key: 'notDue',
        label: '未到期',
        value: `¥ ${formatMoney(k?.notDueAmount ?? 0)}`,
        type: 'info',
        hint: '还在账期内，暂不用催'
      },
      {
        key: 'overdue',
        label: '已逾期',
        value: `¥ ${formatMoney(k?.overdueAmount ?? 0)}`,
        type: 'warning',
        clickable: true,
        hint: '点击只看逾期客户'
      },
      {
        key: 'lastBucket',
        label: k?.lastBucketLabel ? `${k.lastBucketLabel}` : '最长账龄档',
        value: `¥ ${formatMoney(k?.lastBucketAmount ?? 0)}`,
        type: 'danger',
        clickable: true,
        hint: '账龄最长的一档，优先处理'
      },
      {
        key: 'exceeded',
        label: '超信用额度客户',
        value: k?.exceededCustomerCount ?? 0,
        unit: '家',
        type: 'danger',
        clickable: true,
        hint: '点击只看超额度客户'
      }
    ];
  });

  const bucketAmount = (row: AgingCustomerRow, idx: number) =>
    row.bucketSummary?.find((b) => b.bucket === idx)?.amount ?? 0;

  const columns = computed<Columns>(() => {
    const base: Columns = [
      {
        prop: 'customerName',
        label: '客户',
        minWidth: 200,
        slot: 'customer'
      },
      {
        prop: 'unpaidAmount',
        label: '未收余额',
        width: 140,
        align: 'right',
        slot: 'unpaid'
      },
      {
        prop: 'overdueAmount',
        label: '其中逾期',
        width: 140,
        align: 'right',
        slot: 'overdue'
      },
      {
        prop: 'creditLimit',
        label: '信用额度',
        width: 130,
        align: 'right',
        formatter: (row) =>
          row.creditLimit === null || row.creditLimit === undefined
            ? '未设置'
            : `¥ ${formatMoney(row.creditLimit)}`
      }
    ];
    bucketLabels.value.forEach((label, idx) => {
      base.push({
        columnKey: `bucket${idx}`,
        label,
        width: 120,
        align: 'right',
        slot: `bucket${idx}`
      });
    });
    base.push({
      prop: 'settleCount',
      label: '结算单',
      width: 90,
      align: 'center'
    });
    base.push({
      columnKey: 'action',
      label: '操作',
      width: 120,
      minWidth: 120,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    });
    return base;
  });

  const datasource: DatasourceFunction = ({ pages, where: tableWhere }) => {
    return pageAging({ ...(tableWhere || where), ...pages }).then((res) => {
      if (res?.bucketLabels?.length) {
        bucketLabels.value = res.bucketLabels;
      }
      return { list: res?.list ?? [], count: res?.count ?? 0 };
    });
  };

  const reload = (page?: number) => {
    tableRef.value?.reload?.({ where: { ...where }, page });
  };

  const renderChart = () => {
    const dist = summary.value?.bucketDistribution || [];
    Object.assign(chartOption, {
      grid: { left: 8, right: 8, top: 16, bottom: 0, containLabel: true },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params: any) => {
          const arr = Array.isArray(params) ? params : [params];
          const p = arr[0];
          const cell = dist[p?.dataIndex ?? 0];
          return (
            `${p?.axisValue ?? ''}<br/>未收 ¥ ${formatMoney(cell?.amount)}` +
            `<br/>${cell?.count ?? 0} 张结算单`
          );
        }
      },
      xAxis: { type: 'category', data: dist.map((b) => b.label) },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: (v: number) =>
            v >= 10000 ? `${(v / 10000).toFixed(0)}万` : String(v)
        }
      },
      series: [
        {
          type: 'bar',
          barMaxWidth: 48,
          data: dist.map((b, idx) => ({
            value: b.amount,
            itemStyle: {
              color:
                idx === 0
                  ? '#409eff'
                  : idx >= dist.length - 1
                    ? '#f56c6c'
                    : '#e6a23c'
            }
          }))
        }
      ]
    });
  };

  const loadSummary = async () => {
    summaryLoading.value = true;
    try {
      const res = await getAgingSummary({
        keyword: where.keyword,
        creditStatus: where.creditStatus,
        baseDate: where.baseDate
      });
      summary.value = res ?? null;
      if (res?.bucketLabels?.length) {
        bucketLabels.value = res.bucketLabels;
      }
      renderChart();
    } catch (e: unknown) {
      const msg =
        (e as { message?: string }).message || '账龄统计加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      summaryLoading.value = false;
    }
  };

  const onSearch = async (next?: AgingParam) => {
    if (next) Object.assign(where, next);
    await loadSummary();
    reload(1);
  };

  const onKpiSelect = (key: string) => {
    if (key === 'overdue') {
      searchRef.value?.applyFlags({ onlyOverdue: true });
    } else if (key === 'exceeded') {
      searchRef.value?.applyFlags({ onlyExceeded: true });
    } else if (key === 'lastBucket') {
      const last = bucketLabels.value.length - 1;
      searchRef.value?.applyFlags({ bucket: last });
    }
  };

  const actionItems = (row: AgingCustomerRow): ButtonItem[] =>
    buildActionColumnItems([
      {
        title: '看明细',
        icon: EyeOutlined,
        permission: 'finance:ar-aging:detail',
        onClick: () => {
          detailCustomerId.value = row.customerId;
          detailVisible.value = true;
        }
      }
    ]);

  const exportList = async () => {
    const l = EleMessage.loading({
      message: '正在导出账龄表，请稍候…',
      plain: true
    });
    try {
      await exportAging({
        keyword: where.keyword,
        creditStatus: where.creditStatus,
        bucket: where.bucket,
        baseDate: where.baseDate
      });
      l.close();
      EleMessage.success({ message: '账龄表已开始下载', plain: true });
    } catch (e: unknown) {
      l.close();
      const msg = (e as { message?: string }).message || '导出失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    }
  };

  onMounted(async () => {
    await loadSummary();
    const fromQuery = Number(route.query.customerId);
    if (fromQuery) {
      where.customerId = fromQuery;
      detailCustomerId.value = fromQuery;
      detailVisible.value = true;
    }
  });
</script>

<style lang="scss" scoped>
  .chart-card {
    margin-bottom: 12px;
  }

  .chart-head {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }

  .chart-title {
    font-weight: 600;
    letter-spacing: -0.01em;
  }

  .chart-sub {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .chart-body {
    position: relative;
    height: 220px;
  }

  .chart-inner {
    width: 100%;
    height: 100%;
  }

  .chart-empty {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-secondary);
  }

  .cust-name {
    font-weight: 500;
  }

  .cust-tags {
    display: flex;
    gap: 4px;
    margin-top: 2px;
  }

  .num {
    font-variant-numeric: tabular-nums;
  }

  .strong {
    font-weight: 600;
  }

  .danger {
    color: var(--el-color-danger);
  }

  .muted {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }
</style>
