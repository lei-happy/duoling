<!-- 利润总览 - 核心 KPI 卡片（收入 / 成本 / 毛利 / 毛利率） -->
<template>
  <el-row :gutter="16">
    <el-col
      :md="6"
      :sm="12"
      :xs="24"
      v-for="(item, idx) in kpiItems"
      :key="item.key"
    >
      <ele-card class="kpi-card" v-loading="loading">
        <ele-text type="placeholder" class="kpi-header">
          <div class="kpi-header-text">{{ item.title }}</div>
          <ele-tooltip :content="item.tooltip" placement="top" :offset="6">
            <el-icon class="kpi-header-tip">
              <QuestionCircleOutlined />
            </el-icon>
          </ele-tooltip>
        </ele-text>
        <ele-text size="xxl" class="kpi-value">
          {{ formatMainValue(item) }}
        </ele-text>
        <v-chart
          v-if="item.trend30d.length > 0"
          :ref="(el: any) => assignChartRef(idx, el)"
          :option="item.chartOption"
          style="height: 36px"
        />
        <div v-else class="kpi-empty">暂无趋势数据</div>
        <el-divider />
        <div class="kpi-footer">
          <div
            class="kpi-trend-text"
            :class="{ 'kpi-trend-text--muted': item.dayOverDayRate === null }"
          >
            <div>{{ compareLine('日环比', item, item.dayOverDayRate) }}</div>
            <ele-text
              v-if="item.dayOverDayRate !== null"
              :type="item.dayOverDayRate >= 0 ? 'danger' : 'success'"
              :icon="item.dayOverDayRate >= 0 ? CaretUpFilled : CaretDownFilled"
            />
          </div>
          <div
            class="kpi-trend-text"
            :class="{ 'kpi-trend-text--muted': item.weekOverWeekRate === null }"
          >
            <div>{{ compareLine('周环比', item, item.weekOverWeekRate) }}</div>
            <ele-text
              v-if="item.weekOverWeekRate !== null"
              :type="item.weekOverWeekRate >= 0 ? 'danger' : 'success'"
              :icon="
                item.weekOverWeekRate >= 0 ? CaretUpFilled : CaretDownFilled
              "
            />
          </div>
        </div>
      </ele-card>
    </el-col>
  </el-row>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { use } from 'echarts/core';
  import type { EChartsCoreOption } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { LineChart, BarChart } from 'echarts/charts';
  import { GridComponent, TooltipComponent } from 'echarts/components';
  import VChart from 'vue-echarts';
  import {
    QuestionCircleOutlined,
    CaretUpFilled,
    CaretDownFilled
  } from '@/components/icons';
  import { useEcharts } from '@/utils/use-echarts';
  import { getProfitKpiSummary } from '@/api/dashboard/profit';
  import type {
    ProfitKpiSummary,
    ProfitSparklinePoint
  } from '@/api/dashboard/profit/model';

  use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent]);

  type KpiKey = 'revenue' | 'cost' | 'grossProfit' | 'grossMargin';

  interface KpiItem {
    key: KpiKey;
    title: string;
    tooltip: string;
    /** amount: 元→万元；margin: 比率→百分比 */
    kind: 'amount' | 'margin';
    color: string;
    chartType: 'line' | 'bar';
    todayValue: number | null;
    weekOverWeekRate: number | null;
    dayOverDayRate: number | null;
    trend30d: ProfitSparklinePoint[];
    chartOption: EChartsCoreOption;
  }

  const loading = ref(false);
  const chartRef0 = ref<InstanceType<typeof VChart> | null>(null);
  const chartRef1 = ref<InstanceType<typeof VChart> | null>(null);
  const chartRef2 = ref<InstanceType<typeof VChart> | null>(null);
  const chartRef3 = ref<InstanceType<typeof VChart> | null>(null);
  const chartRefs = [chartRef0, chartRef1, chartRef2, chartRef3];
  useEcharts(chartRefs);

  const assignChartRef = (
    idx: number,
    el: InstanceType<typeof VChart> | null
  ) => {
    if (chartRefs[idx]) {
      chartRefs[idx].value = el;
    }
  };

  const makeChartOption = (
    points: ProfitSparklinePoint[],
    color: string,
    type: 'line' | 'bar',
    kind: 'amount' | 'margin'
  ): EChartsCoreOption => {
    const dot = (c: string) =>
      `<i style="background: ${c};width: 10px;height: 10px;margin-right: 5px;border-radius: 50%;display: inline-block;"></i>`;

    const formatTipVal = (val: number | null) => {
      if (val === null || !Number.isFinite(val)) return '—';
      if (kind === 'margin') return `${(val * 100).toFixed(2)}%`;
      return `${(val / 10000).toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })} 万元`;
    };

    const axisTooltipFormatter = (params: unknown) => {
      const p = Array.isArray(params) ? params[0] : params;
      if (!p || typeof p !== 'object') return '';
      const px = p as {
        axisValue?: string;
        value?: number;
        dataIndex?: number;
      };
      const date = px.axisValue ?? points[px.dataIndex ?? 0]?.date ?? '';
      const raw = px.value;
      const val = typeof raw === 'number' ? raw : null;
      return `${dot(color)}${date}: ${formatTipVal(val)}`;
    };

    const data = points.map((d) => d.value);
    if (type === 'bar') {
      return {
        tooltip: { trigger: 'axis', formatter: axisTooltipFormatter },
        grid: { top: 0, bottom: 0, left: 0, right: 0 },
        xAxis: [
          { show: false, type: 'category', data: points.map((d) => d.date) }
        ],
        yAxis: [{ show: false, type: 'value', splitLine: { show: false } }],
        series: [
          {
            type: 'bar',
            data,
            itemStyle: {
              borderRadius: [2, 2, 0, 0],
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: color + 'cc' },
                  { offset: 0.45, color },
                  { offset: 1, color: color + '99' }
                ]
              }
            }
          }
        ]
      };
    }
    return {
      color,
      tooltip: { trigger: 'axis', formatter: axisTooltipFormatter },
      grid: { top: 0, bottom: 0, left: 0, right: 0 },
      xAxis: [
        {
          show: false,
          type: 'category',
          boundaryGap: false,
          data: points.map((d) => d.date)
        }
      ],
      yAxis: [{ show: false, type: 'value', splitLine: { show: false } }],
      series: [
        {
          type: 'line',
          smooth: true,
          symbol: 'none',
          connectNulls: true,
          lineStyle: { width: 1.38, color },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: `${color}99` },
                { offset: 1, color: `${color}18` }
              ]
            }
          },
          data
        }
      ]
    };
  };

  const META: Record<
    KpiKey,
    {
      title: string;
      tooltip: string;
      kind: 'amount' | 'margin';
      color: string;
      chartType: 'line' | 'bar';
    }
  > = {
    revenue: {
      title: '收入',
      tooltip:
        '当天 0 点至接口返回时刻的运单收入合计（取运费计算引擎结果 biz_waybill_freight_result，无结果时回退运单应收运费）；主数字单位为万元；迷你图为近 30 天每日收入。',
      kind: 'amount',
      color: '#165dff',
      chartType: 'line'
    },
    cost: {
      title: '成本',
      tooltip:
        '当天 0 点至今的运输成本合计（取任务成本引擎结果 biz_task_cost_result，按台数分摊到运单）；单位为万元；迷你图为近 30 天每日成本。',
      kind: 'amount',
      color: '#ff7d00',
      chartType: 'bar'
    },
    grossProfit: {
      title: '毛利',
      tooltip:
        '毛利 = 收入 − 分摊成本；单位为万元；迷你图为近 30 天每日毛利。未挂接任务（无成本）的运单成本按 0 计，可能拉高毛利。',
      kind: 'amount',
      color: '#00b42a',
      chartType: 'line'
    },
    grossMargin: {
      title: '毛利率',
      tooltip:
        '毛利率 = 毛利 / 收入；日/周环比为「百分点差」（pp）；迷你图为近 30 天每日毛利率。收入为 0 的日期显示为断点。',
      kind: 'margin',
      color: '#722ed1',
      chartType: 'line'
    }
  };

  const summary = ref<ProfitKpiSummary | null>(null);

  const kpiItems = computed<KpiItem[]>(() => {
    const keys: KpiKey[] = ['revenue', 'cost', 'grossProfit', 'grossMargin'];
    return keys.map((key) => {
      const meta = META[key];
      const metric = summary.value ? summary.value[key] : null;
      const points: ProfitSparklinePoint[] = metric
        ? (metric.trend30d || []).map((p) => ({ date: p.date, value: p.value }))
        : [];
      return {
        key,
        title: meta.title,
        tooltip: meta.tooltip,
        kind: meta.kind,
        color: meta.color,
        chartType: meta.chartType,
        todayValue: metric ? metric.todayValue : null,
        weekOverWeekRate: metric ? metric.weekOverWeekRate : null,
        dayOverDayRate: metric ? metric.dayOverDayRate : null,
        trend30d: points,
        chartOption: makeChartOption(
          points,
          meta.color,
          meta.chartType,
          meta.kind
        )
      };
    });
  });

  const formatMainValue = (item: KpiItem) => {
    if (item.todayValue === null || !Number.isFinite(item.todayValue)) {
      return item.kind === 'margin' ? '—' : '0.00 万元';
    }
    if (item.kind === 'margin') {
      return `${(item.todayValue * 100).toFixed(2)}%`;
    }
    const w = item.todayValue / 10000;
    return `${w.toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })} 万元`;
  };

  const compareLine = (label: string, item: KpiItem, rate: number | null) => {
    if (rate === null || rate === undefined) {
      return `${label} —`;
    }
    const sign = rate >= 0 ? '+' : '';
    if (item.kind === 'margin') {
      // 百分点差
      return `${label}${sign}${(rate * 100).toFixed(2)}pp`;
    }
    return `${label}${sign}${(rate * 100).toFixed(2)}%`;
  };

  const load = async () => {
    loading.value = true;
    try {
      summary.value = await getProfitKpiSummary();
    } catch (e: any) {
      EleMessage.error({ message: e?.message || '加载 KPI 失败', plain: true });
    } finally {
      loading.value = false;
    }
  };

  onMounted(() => load());
</script>

<style lang="scss" scoped>
  .kpi-card {
    margin-top: 8px;
    margin-bottom: 16px;

    :deep(.ele-card-body) {
      padding: 16px 22px 12px 22px;
    }

    :deep(.el-divider) {
      margin: 12px 0;
      opacity: 0.6;
    }

    .kpi-header {
      display: flex;
      align-items: center;

      .kpi-header-text {
        flex: 1;
      }

      .kpi-header-tip {
        font-size: 15px;
        cursor: help;
      }
    }

    .kpi-value {
      margin-top: 4px;
    }

    :deep(.kpi-value) {
      font-variant-numeric: tabular-nums;
    }

    .kpi-empty {
      height: 36px;
      line-height: 36px;
      color: var(--el-text-color-placeholder);
      font-size: 12px;
    }

    .kpi-footer {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      color: var(--el-text-color-regular);
    }

    .kpi-trend-text {
      display: flex;
      align-items: center;
      white-space: nowrap;
      overflow: hidden;

      .el-icon {
        font-size: 16px;
        margin-left: 4px;
      }
    }

    .kpi-trend-text + .kpi-trend-text {
      margin-left: 14px;
    }

    .kpi-trend-text--muted {
      color: var(--el-text-color-placeholder);
    }
  }
</style>
