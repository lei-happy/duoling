<!-- 利润总览 - 收入/成本/毛利趋势 + 毛利率线（双轴，支持 日/周/月） -->
<template>
  <ele-card
    :header-style="{ paddingTop: 0, paddingBottom: 0 }"
    :body-style="{ padding: 0 }"
    class="trend-card"
  >
    <template #header>
      <div class="trend-card-title">收入 · 成本 · 毛利趋势</div>
    </template>
    <template #extra>
      <div class="hidden-xs-only trend-card-extra">
        <el-radio-group v-model="granularity" size="default" @change="load">
          <el-radio-button value="day">日</el-radio-button>
          <el-radio-button value="week">周</el-radio-button>
          <el-radio-button value="month">月</el-radio-button>
        </el-radio-group>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          size="default"
          unlink-panels
          range-separator="-"
          value-format="YYYY-MM-DD"
          start-placeholder="开始"
          end-placeholder="结束"
          :disabled-date="disabledDate"
          :clearable="false"
          class="trend-date-range"
          @change="load"
        />
      </div>
    </template>
    <div class="trend-body" v-loading="loading">
      <v-chart
        ref="trendChartRef"
        :option="trendOption"
        class="trend-chart-inner"
        autoresize
      />
      <div v-if="trendData.length === 0 && !loading" class="trend-empty">
        暂无趋势数据
      </div>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { reactive, ref } from 'vue';
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
  import { getProfitTrend } from '@/api/dashboard/profit';
  import type { ProfitTrendPoint } from '@/api/dashboard/profit/model';

  use([
    CanvasRenderer,
    LineChart,
    BarChart,
    GridComponent,
    TooltipComponent,
    LegendComponent
  ]);

  const API_DT = 'YYYY-MM-DD HH:mm:ss';
  const DEFAULT_RANGE_DAYS = 30;

  const granularity = ref<'day' | 'week' | 'month'>('day');
  const loading = ref(false);
  const trendData = ref<ProfitTrendPoint[]>([]);

  function defaultDateRange(): [string, string] {
    const end = dayjs().startOf('day');
    const start = end.subtract(DEFAULT_RANGE_DAYS - 1, 'day');
    return [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')];
  }

  const dateRange = ref<[string, string]>(defaultDateRange());

  const trendChartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([trendChartRef]);

  const trendOption: EChartsCoreOption = reactive({});

  const disabledDate = (time: Date) =>
    dayjs(time).startOf('day').isAfter(dayjs().startOf('day'));

  const formatNumber = (n: number) => {
    if (!Number.isFinite(n)) return '0';
    return n.toLocaleString('zh-CN');
  };

  function toApiWindow(range: [string, string]): {
    start: string;
    end: string;
  } {
    return {
      start: dayjs(range[0]).startOf('day').format(API_DT),
      end: dayjs(range[1]).add(1, 'day').startOf('day').format(API_DT)
    };
  }

  const COLOR_REVENUE = '#165dff';
  const COLOR_COST = '#ff7d00';
  const COLOR_PROFIT = '#00b42a';
  const COLOR_MARGIN = '#722ed1';

  const renderChart = () => {
    const points = trendData.value;
    const xData = points.map((p) => p.date);
    Object.assign(trendOption, {
      grid: { left: 8, right: 8, top: 44, bottom: 0, containLabel: true },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params: any) => {
          const arr = Array.isArray(params) ? params : [params];
          const title = arr[0]?.axisValue ?? '';
          const lines = arr.map((p: any) => {
            const isMargin = p.seriesName === '毛利率';
            const v =
              p.value === null || p.value === undefined
                ? '—'
                : isMargin
                  ? `${(Number(p.value) * 100).toFixed(2)}%`
                  : `¥ ${formatNumber(Math.round(Number(p.value)))}`;
            return `${p.marker}${p.seriesName}: ${v}`;
          });
          return `${title}<br/>${lines.join('<br/>')}`;
        }
      },
      legend: {
        top: 2,
        left: 'center',
        itemGap: 18,
        data: ['收入', '成本', '毛利', '毛利率']
      },
      color: [COLOR_REVENUE, COLOR_COST, COLOR_PROFIT, COLOR_MARGIN],
      xAxis: [
        {
          type: 'category',
          data: xData,
          boundaryGap: true,
          axisTick: { alignWithLabel: true },
          axisLabel: { margin: 8, hideOverlap: true }
        }
      ],
      yAxis: [
        {
          type: 'value',
          name: '金额 (元)',
          axisLabel: {
            formatter: (val: number) =>
              Math.abs(val) >= 10000
                ? `${(val / 10000).toFixed(1)}万`
                : `${val}`
          }
        },
        {
          type: 'value',
          name: '毛利率',
          alignTicks: true,
          axisLabel: {
            formatter: (val: number) => `${(val * 100).toFixed(0)}%`
          }
        }
      ],
      series: [
        {
          name: '收入',
          type: 'bar',
          yAxisIndex: 0,
          barMaxWidth: 24,
          itemStyle: { borderRadius: [4, 4, 0, 0] },
          data: points.map((p) => p.revenue)
        },
        {
          name: '成本',
          type: 'bar',
          yAxisIndex: 0,
          barMaxWidth: 24,
          itemStyle: { borderRadius: [4, 4, 0, 0] },
          data: points.map((p) => p.cost)
        },
        {
          name: '毛利',
          type: 'line',
          yAxisIndex: 0,
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { width: 2, color: COLOR_PROFIT },
          itemStyle: { color: COLOR_PROFIT },
          data: points.map((p) => p.grossProfit)
        },
        {
          name: '毛利率',
          type: 'line',
          yAxisIndex: 1,
          smooth: true,
          symbol: 'circle',
          symbolSize: 5,
          connectNulls: true,
          lineStyle: { width: 2, type: 'dashed', color: COLOR_MARGIN },
          itemStyle: { color: COLOR_MARGIN },
          data: points.map((p) => p.grossMargin)
        }
      ]
    });
  };

  const load = async () => {
    loading.value = true;
    try {
      const win = toApiWindow(dateRange.value);
      trendData.value = await getProfitTrend({
        start: win.start,
        end: win.end,
        granularity: granularity.value
      });
      renderChart();
    } catch (e: unknown) {
      const err = e as { message?: string };
      EleMessage.error({
        message: err?.message || '加载趋势数据失败',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  void load();
</script>

<style lang="scss" scoped>
  .trend-card {
    margin-bottom: 16px;

    :deep(.ele-card-header) {
      min-height: 52px;
    }

    :deep(.ele-card-title) {
      flex: 1;
      min-width: 0;
    }
  }

  .trend-card-title {
    font-size: 16px;
    font-weight: 600;
  }

  .trend-card-extra {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
  }

  .trend-card-extra :deep(.el-date-editor.el-date-editor--daterange) {
    width: 250px;
  }

  .trend-body {
    position: relative;
    padding: 12px 8px 8px 8px;
    box-sizing: border-box;
  }

  .trend-chart-inner {
    width: 100%;
    height: 360px;
  }

  .trend-empty {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
    font-size: 13px;
  }
</style>
