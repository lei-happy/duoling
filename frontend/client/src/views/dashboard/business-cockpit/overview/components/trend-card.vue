<!-- 经营驾驶舱 - 运单收入/单量趋势 + 按日联动的客户排行 -->
<template>
  <ele-card
    :header-style="{ paddingTop: 0, paddingBottom: 0 }"
    :body-style="{ padding: 0 }"
    class="trend-card"
  >
    <template #header>
      <ele-tabs
        type="plain"
        size="large"
        v-model="metric"
        :items="[
          { name: 'revenue', label: '运单收入趋势' },
          { name: 'waybill', label: '运单量趋势' }
        ]"
      />
    </template>
    <template #extra>
      <div class="hidden-xs-only trend-card-extra">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          unlink-panels
          range-separator="—"
          value-format="YYYY-MM-DD"
          start-placeholder="开始"
          end-placeholder="结束"
          :disabled-date="disabledDate"
          :clearable="false"
          class="trend-date-range"
          @calendar-change="onCalendarChange"
          @change="onDateRangeChange"
        />
      </div>
    </template>
    <div class="trend-body" v-loading="loading">
      <el-row :gutter="16" class="trend-row">
        <el-col :md="17" :sm="15" :xs="24" class="trend-chart-col">
          <div class="trend-chart-wrap">
            <v-chart
              ref="trendChartRef"
              :option="trendOption"
              class="trend-chart-inner"
              @click="onChartClick"
            />
          </div>
        </el-col>
        <el-col :md="7" :sm="9" :xs="24" class="trend-rank-col">
          <div class="trend-rank-meta">
            <ele-text
              v-if="selectedDate"
              type="placeholder"
              class="trend-rank-sub"
            >
              {{ selectedDate }}{{
                metric === 'revenue' ? ' · 按收入' : ' · 按商品车台数'
              }}
            </ele-text>
            <ele-text v-else type="placeholder" class="trend-rank-sub">
              选择柱图日期查看排行
            </ele-text>
          </div>
          <div class="rank-list">
            <div
              v-for="(item, index) in customerRank"
              :key="`${item.customerId ?? 'x'}-${index}`"
              class="rank-item"
            >
              <el-tag
                size="small"
                class="rank-num"
                :disable-transitions="true"
                :type="index < 3 ? void 0 : 'info'"
                :effect="index < 3 ? 'dark' : 'light'"
                :color="index < 3 ? '#314659' : void 0"
              >
                {{ index + 1 }}
              </el-tag>
              <div class="rank-item-body">
                <ele-ellipsis class="rank-name">
                  {{ item.customerName }}
                </ele-ellipsis>
                <div v-if="metric === 'revenue'" class="rank-tags">
                  <el-tag type="primary" effect="light" size="small">
                    ¥{{ formatNumber(Math.round(item.revenue)) }}
                  </el-tag>
                  <el-tag type="success" effect="light" size="small">
                    {{ item.waybillCount }} 单
                  </el-tag>
                </div>
                <div v-else class="rank-tags">
                  <el-tag type="warning" effect="light" size="small">
                    {{ item.vehicleQuantity }} 台
                  </el-tag>
                  <el-tag type="success" effect="light" size="small">
                    {{ item.waybillCount }} 单
                  </el-tag>
                </div>
              </div>
            </div>
            <div v-if="customerRank.length === 0" class="rank-empty">
              暂无客户数据
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import dayjs from 'dayjs';
  import { EleMessage } from 'ele-admin-plus';
  import { use } from 'echarts/core';
  import type { EChartsCoreOption } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { LineChart, BarChart } from 'echarts/charts';
  import {
    GridComponent,
    TooltipComponent,
    LegendComponent
  } from 'echarts/components';
  import VChart from 'vue-echarts';
  import { useEcharts } from '@/utils/use-echarts';
  import { getCustomerRank, getRevenueTrend } from '@/api/dashboard/cockpit';
  import type {
    CustomerRankItem,
    RevenueTrendPoint
  } from '@/api/dashboard/cockpit/model';

  use([
    CanvasRenderer,
    LineChart,
    BarChart,
    GridComponent,
    TooltipComponent,
    LegendComponent
  ]);

  const API_DT = 'YYYY-MM-DD HH:mm:ss';
  const MAX_RANGE_DAYS = 60;
  const DEFAULT_RANGE_DAYS = 15;
  /** 单日客户排行：取全量（受后端 limit 上限约束） */
  const RANK_LIMIT = 5000;

  const metric = ref<'revenue' | 'waybill'>('revenue');
  const loading = ref(false);
  const trendData = ref<RevenueTrendPoint[]>([]);
  const customerRank = ref<CustomerRankItem[]>([]);
  /** 当前选中的柱图日期（YYYY-MM-DD），右侧排行按该自然日统计 */
  const selectedDate = ref<string | null>(null);

  function defaultDateRange(): [string, string] {
    const end = dayjs().startOf('day');
    const start = end.subtract(DEFAULT_RANGE_DAYS - 1, 'day');
    return [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')];
  }

  const dateRange = ref<[string, string]>(defaultDateRange());
  /** 日历点选时用于限制跨度 60 天（与选中的另一端对齐） */
  const calendarAnchor = ref<dayjs.Dayjs | null>(null);

  const trendChartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([trendChartRef]);

  const trendOption: EChartsCoreOption = reactive({});

  const selectedBarIndex = computed(() => {
    if (!selectedDate.value) return null;
    const i = trendData.value.findIndex((p) => p.date === selectedDate.value);
    return i >= 0 ? i : null;
  });

  const formatNumber = (n: number) => {
    if (!Number.isFinite(n)) return '0';
    return n.toLocaleString('zh-CN');
  };

  function rangeSpanDays(range: [string, string]): number {
    return dayjs(range[1]).diff(dayjs(range[0]), 'day') + 1;
  }

  function toApiWindow(range: [string, string]): { start: string; end: string } {
    return {
      start: dayjs(range[0]).startOf('day').format(API_DT),
      end: dayjs(range[1]).add(1, 'day').startOf('day').format(API_DT)
    };
  }

  function dayWindow(dateStr: string): { start: string; end: string } {
    return {
      start: dayjs(dateStr).startOf('day').format(API_DT),
      end: dayjs(dateStr).add(1, 'day').startOf('day').format(API_DT)
    };
  }

  const disabledDate = (time: Date) => {
    const cur = dayjs(time).startOf('day');
    const today = dayjs().startOf('day');
    if (cur.isAfter(today)) return true;
    const anchor = calendarAnchor.value;
    if (!anchor) return false;
    const min = anchor.subtract(MAX_RANGE_DAYS - 1, 'day');
    const max = anchor.add(MAX_RANGE_DAYS - 1, 'day');
    return cur.isBefore(min, 'day') || cur.isAfter(max, 'day');
  };

  const barGradientRevenue = {
    type: 'linear' as const,
    x: 0,
    y: 0,
    x2: 0,
    y2: 1,
    colorStops: [
      { offset: 0, color: '#b0d0ff' },
      { offset: 0.4, color: '#80a9fa' },
      { offset: 1, color: '#5b8ff9' }
    ]
  };

  const barGradientWaybill = {
    type: 'linear' as const,
    x: 0,
    y: 0,
    x2: 0,
    y2: 1,
    colorStops: [
      { offset: 0, color: '#c2f0e0' },
      { offset: 0.4, color: '#7cd7b5' },
      { offset: 1, color: '#61ddaa' }
    ]
  };

  function barItems(
    values: number[],
    gradient: typeof barGradientRevenue,
    selIdx: number | null
  ) {
    return values.map((value, idx) => {
      const on = selIdx === null || selIdx === idx;
      const selected = selIdx === idx;
      return {
        value,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: gradient,
          opacity: on ? 1 : 0.88,
          borderColor: selected ? '#1d39c4' : 'transparent',
          borderWidth: selected ? 2 : 0,
          shadowBlur: selected ? 10 : 0,
          shadowColor: 'rgba(29,57,196,0.25)'
        }
      };
    });
  }

  const legendTop = {
    top: 2,
    left: 'center' as const,
    itemGap: 20,
    padding: 0
  };

  const baseGrid = {
    left: 8,
    right: 8,
    top: 44,
    bottom: 0,
    containLabel: true
  };

  const renderChart = () => {
    const points = trendData.value;
    const xData = points.map((p) => p.date);
    const sel = selectedBarIndex.value;
    if (metric.value === 'revenue') {
      Object.assign(trendOption, {
        grid: baseGrid,
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          valueFormatter: (val: unknown) => {
            if (typeof val === 'number') {
              return `¥ ${formatNumber(Math.round(val))}`;
            }
            return String(val ?? '');
          }
        },
        legend: { ...legendTop, data: ['运单收入', '运单数'] },
        xAxis: [
          {
            type: 'category',
            data: xData,
            boundaryGap: true,
            axisTick: { alignWithLabel: true },
            axisLabel: { margin: 2, hideOverlap: true }
          }
        ],
        yAxis: [
          {
            type: 'value',
            name: '收入 (元)',
            axisLabel: {
              formatter: (val: number) =>
                Math.abs(val) >= 10000 ? `${(val / 10000).toFixed(1)}万` : `${val}`
            }
          },
          { type: 'value', name: '运单数', alignTicks: true }
        ],
        series: [
          {
            name: '运单收入',
            type: 'bar',
            yAxisIndex: 0,
            barMaxWidth: 36,
            data: barItems(
              points.map((p) => p.revenue),
              barGradientRevenue,
              sel
            )
          },
          {
            name: '运单数',
            type: 'line',
            yAxisIndex: 1,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: { width: 2, color: '#975fe5' },
            itemStyle: { color: '#975fe5' },
            emphasis: { focus: 'series' as const },
            data: points.map((p) => p.waybillCount)
          }
        ]
      });
    } else {
      Object.assign(trendOption, {
        grid: baseGrid,
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { ...legendTop, data: ['运单数', '发运台数'] },
        xAxis: [
          {
            type: 'category',
            data: xData,
            boundaryGap: true,
            axisTick: { alignWithLabel: true },
            axisLabel: { margin: 2, hideOverlap: true }
          }
        ],
        yAxis: [
          { type: 'value', name: '运单数' },
          { type: 'value', name: '发运台数', alignTicks: true }
        ],
        series: [
          {
            name: '运单数',
            type: 'bar',
            yAxisIndex: 0,
            barMaxWidth: 36,
            data: barItems(
              points.map((p) => p.waybillCount),
              barGradientWaybill,
              sel
            )
          },
          {
            name: '发运台数',
            type: 'line',
            yAxisIndex: 1,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: { width: 2, color: '#ff9c6e' },
            itemStyle: { color: '#ff9c6e' },
            emphasis: { focus: 'series' as const },
            data: points.map((p) => p.vehicleQuantity)
          }
        ]
      });
    }
  };

  function syncSelectedDateAfterTrend() {
    const dates = trendData.value.map((p) => p.date);
    if (!dates.length) {
      selectedDate.value = null;
      return;
    }
    if (
      !selectedDate.value ||
      !dates.includes(selectedDate.value)
    ) {
      selectedDate.value = dates[dates.length - 1] ?? null;
    }
  }

  async function loadTrendSeries() {
    const win = toApiWindow(dateRange.value);
    const trend = await getRevenueTrend({
      start: win.start,
      end: win.end,
      granularity: 'day'
    });
    trendData.value = trend;
    syncSelectedDateAfterTrend();
    renderChart();
  }

  async function loadCustomerRankForSelection() {
    if (!selectedDate.value) {
      customerRank.value = [];
      return;
    }
    const win = dayWindow(selectedDate.value);
    const sort_by =
      metric.value === 'revenue' ? 'revenue' : 'vehicle_quantity';
    const rank = await getCustomerRank({
      start: win.start,
      end: win.end,
      limit: RANK_LIMIT,
      sort_by
    });
    customerRank.value = rank;
  }

  const load = async () => {
    loading.value = true;
    try {
      await loadTrendSeries();
      await loadCustomerRankForSelection();
    } catch (e: unknown) {
      const err = e as { message?: string };
      EleMessage.error({ message: err?.message || '加载趋势数据失败', plain: true });
    } finally {
      loading.value = false;
    }
  };

  watch(metric, () => {
    renderChart();
    loadCustomerRankForSelection().catch((e: unknown) => {
      const err = e as { message?: string };
      EleMessage.error({ message: err?.message || '加载排行失败', plain: true });
    });
  });

  const onDateRangeChange = () => {
    calendarAnchor.value = null;
    const r = dateRange.value;
    if (!r?.[0] || !r?.[1]) return;
    if (rangeSpanDays(r) > MAX_RANGE_DAYS) {
      EleMessage.warning({
        message: `时间范围最长 ${MAX_RANGE_DAYS} 天，请重新选择`,
        plain: true
      });
      dateRange.value = defaultDateRange();
      void load();
      return;
    }
    load();
  };

  const onCalendarChange = (dates: [Date, Date | null]) => {
    const start = dates?.[0];
    const end = dates?.[1];
    if (start && !end) {
      calendarAnchor.value = dayjs(start).startOf('day');
    } else {
      calendarAnchor.value = null;
    }
  };

  const onChartClick = (params: Record<string, unknown>) => {
    if (params.componentType !== 'series' || params.seriesType !== 'bar') {
      return;
    }
    const idx =
      typeof params.dataIndex === 'number' ? params.dataIndex : -1;
    const date = trendData.value[idx]?.date;
    if (!date) return;
    selectedDate.value = date;
    renderChart();
    loading.value = true;
    loadCustomerRankForSelection()
      .catch((e: unknown) => {
        const err = e as { message?: string };
        EleMessage.error({ message: err?.message || '加载排行失败', plain: true });
      })
      .finally(() => {
        loading.value = false;
      });
  };

  void load();
</script>

<style lang="scss" scoped>
  .trend-card {
    margin-bottom: 16px;
  }

  .trend-card-extra {
    display: flex;
    align-items: center;
  }

  .trend-date-range {
    width: 260px;
  }

  .trend-body {
    padding: 16px 0 8px 0;
  }

  .trend-row {
    align-items: stretch;
  }

  /* 与排行榜同高，保证左右底部对齐（≥768px 双栏时固定高度） */
  .trend-chart-col,
  .trend-rank-col {
    display: flex;
    flex-direction: column;
    min-height: 300px;
  }

  @media (min-width: 768px) {
    .trend-chart-col,
    .trend-rank-col {
      height: 320px;
      min-height: 320px;
    }
  }

  .trend-chart-wrap {
    flex: 1;
    min-height: 0;
    padding: 4px 8px 4px 12px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
  }

  .trend-chart-inner {
    flex: 1;
    width: 100%;
    min-height: 260px;
    height: 100%;
  }

  .trend-rank-meta {
    flex-shrink: 0;
    padding: 2px 12px 8px 20px;
    line-height: 1.3;
  }

  .trend-rank-sub {
    font-size: 12px;
  }

  .rank-list {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 0 6px 4px 12px;
    box-sizing: border-box;
  }

  .rank-item {
    display: flex;
    align-items: flex-start;
    padding: 8px 10px 8px 12px;
    margin-top: 0;
    box-sizing: border-box;
    border-radius: 4px;
  }

  .rank-item:nth-child(odd) {
    background-color: var(--el-fill-color-extra-light, rgba(0, 0, 0, 0.03));
  }

  .rank-item:nth-child(even) {
    background-color: transparent;
  }

  .rank-num {
    flex-shrink: 0;
    border: none !important;
    border-radius: 50% !important;
    width: 22px;
    height: 22px;
    padding: 0 !important;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .rank-item-body {
    flex: 1;
    min-width: 0;
    padding-left: 10px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .rank-name {
    font-size: 13px;
    line-height: 1.35;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .rank-tags {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
  }

  .rank-empty {
    padding: 24px 20px;
    color: var(--el-text-color-placeholder);
    font-size: 13px;
  }
</style>
