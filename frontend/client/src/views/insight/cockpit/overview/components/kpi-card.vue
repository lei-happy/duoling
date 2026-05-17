<!-- 经营驾驶舱 - 核心 KPI 卡片（当日值 + 近 30 日趋势 + 日同比 / 周同比） -->
<template>
  <el-row :gutter="16">
    <el-col :md="6" :sm="12" :xs="24" v-for="(item, idx) in kpiItems" :key="item.key">
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
          <ele-tooltip
            class="kpi-trend-tooltip"
            :content="kpiCompareTooltipDay"
            placement="top"
            :offset="6"
          >
            <div
              class="kpi-trend-text"
              :class="{
                'kpi-trend-text--muted':
                  item.dayOverDayRate === null ||
                  item.dayOverDayRate === undefined
              }"
            >
              <div>{{ trendCompareLine('日同比', item.dayOverDayRate) }}</div>
              <ele-text
                v-if="item.dayOverDayRate !== null && item.dayOverDayRate !== undefined"
                :type="item.dayOverDayRate >= 0 ? 'danger' : 'success'"
                :icon="
                  item.dayOverDayRate >= 0 ? CaretUpFilled : CaretDownFilled
                "
              />
            </div>
          </ele-tooltip>
          <ele-tooltip
            class="kpi-trend-tooltip"
            :content="kpiCompareTooltipWeek"
            placement="top"
            :offset="6"
          >
            <div
              class="kpi-trend-text"
              :class="{
                'kpi-trend-text--muted':
                  item.weekOverWeekRate === null ||
                  item.weekOverWeekRate === undefined
              }"
            >
              <div>{{ trendCompareLine('周同比', item.weekOverWeekRate) }}</div>
              <ele-text
                v-if="item.weekOverWeekRate !== null && item.weekOverWeekRate !== undefined"
                :type="item.weekOverWeekRate >= 0 ? 'danger' : 'success'"
                :icon="
                  item.weekOverWeekRate >= 0 ? CaretUpFilled : CaretDownFilled
                "
              />
            </div>
          </ele-tooltip>
        </div>
      </ele-card>
    </el-col>
  </el-row>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref } from 'vue';
  import dayjs from 'dayjs';
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
  import { getKpiSummary } from '@/api/dashboard/cockpit';
  import type { KpiMetric, KpiSummary } from '@/api/dashboard/cockpit/model';

  use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent]);

  type KpiKey = 'revenue' | 'waybillCount' | 'vehicleQuantity' | 'customerCount';

  interface KpiItem {
    key: KpiKey;
    title: string;
    tooltip: string;
    /** 主数值展示：万元（收入）或整数 */
    display: 'wan' | 'int';
    /** 主数字后的单位（运单数「单」、商品车「台」、客户「家」） */
    mainUnit?: string;
    color: string;
    chartType: 'line' | 'bar';
    todayValue: number;
    weekOverWeekRate: number | null;
    dayOverDayRate: number | null;
    trend30d: Array<{ date: string; value: number }>;
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
    points: Array<{ date: string; value: number }>,
    color: string,
    type: 'line' | 'bar',
    tooltipValueInWan: boolean
  ): EChartsCoreOption => {
    const dot = (c: string) =>
      `<i style="background: ${c};width: 10px;height: 10px;margin-right: 5px;border-radius: 50%;display: inline-block;"></i>`;

    const formatTipVal = (val: number) => {
      if (!Number.isFinite(val)) return '—';
      if (tooltipValueInWan) {
        return `${(val / 10000).toLocaleString('zh-CN', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        })} 万元`;
      }
      return Math.round(val).toLocaleString('zh-CN');
    };

    const axisTooltipFormatter = (params: unknown) => {
      const p = Array.isArray(params) ? params[0] : params;
      if (!p || typeof p !== 'object') return '';
      const px = p as { axisValue?: string; value?: number; dataIndex?: number };
      const date = px.axisValue ?? points[px.dataIndex ?? 0]?.date ?? '';
      const val = typeof px.value === 'number' ? px.value : 0;
      return `${dot(color)}${date}: ${formatTipVal(val)}`;
    };

    if (type === 'bar') {
      return {
        tooltip: {
          trigger: 'axis',
          formatter: axisTooltipFormatter
        },
        grid: { top: 0, bottom: 0, left: 0, right: 0 },
        xAxis: [
          {
            show: false,
            type: 'category',
            data: points.map((d) => d.date)
          }
        ],
        yAxis: [{ show: false, type: 'value', splitLine: { show: false } }],
        series: [
          {
            type: 'bar',
            data: points.map((d) => d.value),
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
                  { offset: 0.45, color: color },
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
      tooltip: {
        trigger: 'axis',
        formatter: axisTooltipFormatter
      },
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
          data: points.map((d) => d.value)
        }
      ]
    };
  };

  /** KPI 元数据 */
  const META: Record<
    KpiKey,
    {
      title: string;
      tooltip: string;
      display: 'wan' | 'int';
      mainUnit?: string;
      color: string;
      chartType: 'line' | 'bar';
    }
  > = {
    revenue: {
      title: '运单收入',
      tooltip:
        '统计当天 0 点至接口返回时刻的应收运费合计，主数字单位为万元；迷你图为近 30 天每日运费（元）。',
      display: 'wan',
      color: '#165dff',
      chartType: 'line'
    },
    waybillCount: {
      title: '运单数',
      tooltip:
        '统计当天 0 点至接口返回时刻的运单条数，单位为「单」；迷你图为近 30 天每日运单量。',
      display: 'int',
      mainUnit: '单',
      color: '#14c9c9',
      chartType: 'bar'
    },
    vehicleQuantity: {
      title: '商品车数量',
      tooltip:
        '统计当天 0 点至接口返回时刻的商品车台数合计，单位为「台」；迷你图为近 30 天每日台数。',
      display: 'int',
      mainUnit: '台',
      color: '#722ed1',
      chartType: 'line'
    },
    customerCount: {
      title: '服务客户数',
      tooltip:
        '统计当天 0 点至接口返回时刻、有运单的去重客户数，单位为「家」；迷你图为近 30 天每日去重客户数。',
      display: 'int',
      mainUnit: '家',
      color: '#ff7d00',
      chartType: 'bar'
    }
  };

  const summary = ref<KpiSummary | null>(null);

  const emptyMetric = (): KpiMetric => ({
    todayValue: 0,
    weekOverWeekRate: null,
    dayOverDayRate: null,
    trend30d: []
  });

  const kpiItems = computed<KpiItem[]>(() => {
    const keys: KpiKey[] = [
      'revenue',
      'waybillCount',
      'vehicleQuantity',
      'customerCount'
    ];
    return keys.map((key) => {
      const meta = META[key];
      const metric: KpiMetric = summary.value
        ? summary.value[key]
        : emptyMetric();
      const points = (metric.trend30d || []).map((p) => ({
        date: p.date,
        value: p.value
      }));
      return {
        key,
        title: meta.title,
        tooltip: meta.tooltip,
        display: meta.display,
        mainUnit: meta.mainUnit,
        color: meta.color,
        chartType: meta.chartType,
        todayValue: metric.todayValue,
        weekOverWeekRate: metric.weekOverWeekRate,
        dayOverDayRate: metric.dayOverDayRate,
        trend30d: points,
        chartOption: makeChartOption(
          points,
          meta.color,
          meta.chartType,
          key === 'revenue'
        )
      };
    });
  });

  const formatNumber = (n: number) => {
    if (!Number.isFinite(n)) return '0';
    return n.toLocaleString('zh-CN');
  };

  const formatMainValue = (item: KpiItem) => {
    if (item.display === 'wan') {
      const w = item.todayValue / 10000;
      return `${w.toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })} 万元`;
    }
    const num = formatNumber(Math.round(item.todayValue));
    return item.mainUnit ? `${num} ${item.mainUnit}` : num;
  };

  /** 最近一次 KPI 接口成功返回时的本地时分，用于 tooltip 与口径说明 */
  const dataRequestTime = ref('');

  const kpiCompareTooltipWeek = computed(() => {
    const t = dataRequestTime.value;
    if (!t) {
      return '本期：本周一 0:00 至统计时分的累计；对比：上周一 0:00 起相同时长。增幅 = (本期−对比) /对比。';
    }
    return `本期：本周一 0:00 至今天 ${t} 的累计；对比：上周一 0:00 起相同时长内的累计。增幅 = (本期−对比) /对比。`;
  });

  const kpiCompareTooltipDay = computed(() => {
    const t = dataRequestTime.value;
    if (!t) {
      return '本期：今天 0:00 至统计时分的累计；对比：昨天 0:00 至昨天相同时分。增幅 = (本期−对比) /对比。';
    }
    return `本期：今天 0:00 至 ${t} 的累计；对比：昨天 0:00 至昨天 ${t} 的累计。增幅 = (本期−对比) /对比。`;
  });

  const formatPercent = (rate: number) => {
    const sign = rate >= 0 ? '+' : '';
    return `${sign}${(rate * 100).toFixed(2)}%`;
  };

  /** 与 statistics-card 一致：「周同比+12.34%」文案 + 独立 icon 的 ele-text */
  const trendCompareLine = (label: string, rate: number | null | undefined) => {
    if (rate === null || rate === undefined) {
      return `${label} —`;
    }
    return `${label}${formatPercent(rate)}`;
  };

  const load = async () => {
    loading.value = true;
    try {
      summary.value = await getKpiSummary();
      dataRequestTime.value = dayjs().format('HH:mm');
    } catch (e: any) {
      dataRequestTime.value = '';
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

    .kpi-trend-tooltip {
      display: inline-flex;
      max-width: 100%;
    }

    .kpi-trend-tooltip + .kpi-trend-tooltip {
      margin-left: 14px;
    }

    .kpi-trend-text {
      display: flex;
      align-items: center;
      white-space: nowrap;
      word-break: break-all;
      overflow: hidden;
      cursor: help;

      .el-icon {
        font-size: 16px;
        margin-left: 4px;
      }
    }

    .kpi-trend-text--muted {
      color: var(--el-text-color-placeholder);
    }
  }
</style>
