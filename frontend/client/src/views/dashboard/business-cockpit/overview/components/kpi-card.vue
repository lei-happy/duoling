<!-- 经营驾驶舱 - 核心 KPI 卡片（收入 / 单量 / 台数 / 客户数） -->
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
          {{ formatValue(item) }}
        </ele-text>
        <v-chart
          v-if="item.sparkline.length > 0"
          :ref="(el: any) => assignChartRef(idx, el)"
          :option="item.chartOption"
          style="height: 36px"
        />
        <div v-else class="kpi-empty">暂无趋势数据</div>
        <el-divider />
        <div class="kpi-footer">
          <div class="kpi-trend">
            <span>环比</span>
            <template v-if="item.growthRate === null || item.growthRate === undefined">
              <ele-text type="placeholder">&nbsp;—</ele-text>
            </template>
            <template v-else>
              <ele-text :type="item.growthRate >= 0 ? 'danger' : 'success'">
                &nbsp;{{ formatPercent(item.growthRate) }}
              </ele-text>
              <ele-text
                :type="item.growthRate >= 0 ? 'danger' : 'success'"
                :icon="item.growthRate >= 0 ? CaretUpFilled : CaretDownFilled"
              />
            </template>
          </div>
          <div class="kpi-prev">对照期 {{ formatCompact(item.previous, item) }}</div>
        </div>
      </ele-card>
    </el-col>
  </el-row>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
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
  import { useCockpitFilter } from '../composables/use-cockpit-filter';

  use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent]);

  type KpiKey = 'revenue' | 'waybillCount' | 'vehicleQuantity' | 'customerCount';

  interface KpiItem {
    key: KpiKey;
    title: string;
    tooltip: string;
    /** 单位/格式：'money' 显示 ¥+千分位；'int' 整数千分位 */
    format: 'money' | 'int';
    color: string;
    chartType: 'line' | 'bar';
    value: number;
    previous: number;
    growthRate: number | null;
    sparkline: Array<{ date: string; value: number }>;
    chartOption: EChartsCoreOption;
  }

  const { state } = useCockpitFilter();

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
    type: 'line' | 'bar'
  ): EChartsCoreOption => {
    if (type === 'bar') {
      return {
        tooltip: {
          trigger: 'axis',
          formatter: `<i style="background: ${color};width: 10px;height: 10px;margin-right: 5px;border-radius: 50%;display: inline-block;"></i>{b0}: {c0}`
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
              color
            }
          }
        ]
      };
    }
    return {
      tooltip: {
        trigger: 'axis',
        formatter: `<i style="background: ${color};width: 10px;height: 10px;margin-right: 5px;border-radius: 50%;display: inline-block;"></i>{b0}: {c0}`
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
          lineStyle: { width: 1.5, color },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: color + '99' },
                { offset: 1, color: color + '11' }
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
      format: 'money' | 'int';
      color: string;
      chartType: 'line' | 'bar';
    }
  > = {
    revenue: {
      title: '运费总收入',
      tooltip: '本期内所有运单的应收运费合计',
      format: 'money',
      color: '#5b8ff9',
      chartType: 'line'
    },
    waybillCount: {
      title: '总运单数',
      tooltip: '本期内创建的运单总数（已剔除作废单）',
      format: 'int',
      color: '#975fe5',
      chartType: 'bar'
    },
    vehicleQuantity: {
      title: '总发运台数',
      tooltip: '本期内所有运单合计发运的商品车台数',
      format: 'int',
      color: '#61ddaa',
      chartType: 'line'
    },
    customerCount: {
      title: '服务客户数',
      tooltip: '本期内有运单产生的去重客户数量',
      format: 'int',
      color: '#ff9c6e',
      chartType: 'bar'
    }
  };

  const summary = ref<KpiSummary | null>(null);

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
        : { value: 0, previous: 0, growthRate: null, sparkline: [] };
      const points = (metric.sparkline || []).map((p) => ({
        date: p.date,
        value: p.value
      }));
      return {
        key,
        title: meta.title,
        tooltip: meta.tooltip,
        format: meta.format,
        color: meta.color,
        chartType: meta.chartType,
        value: metric.value,
        previous: metric.previous,
        growthRate: metric.growthRate,
        sparkline: points,
        chartOption: makeChartOption(points, meta.color, meta.chartType)
      };
    });
  });

  const formatNumber = (n: number) => {
    if (!Number.isFinite(n)) return '0';
    return n.toLocaleString('zh-CN');
  };

  const formatValue = (item: KpiItem) => {
    if (item.format === 'money') {
      return `¥ ${formatNumber(Math.round(item.value))}`;
    }
    return formatNumber(Math.round(item.value));
  };

  const formatCompact = (n: number, item: KpiItem) => {
    if (item.format === 'money') {
      return `¥ ${formatNumber(Math.round(n))}`;
    }
    return formatNumber(Math.round(n));
  };

  const formatPercent = (rate: number) => {
    const sign = rate >= 0 ? '+' : '';
    return `${sign}${(rate * 100).toFixed(2)}%`;
  };

  const load = async () => {
    loading.value = true;
    try {
      const data = await getKpiSummary({
        start: state.start,
        end: state.end
      });
      summary.value = data;
    } catch (e: any) {
      EleMessage.error({ message: e?.message || '加载 KPI 失败', plain: true });
    } finally {
      loading.value = false;
    }
  };

  watch(
    () => [state.start, state.end] as const,
    () => load(),
    { immediate: true }
  );
</script>

<style lang="scss" scoped>
  .kpi-card {
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

    .kpi-empty {
      height: 36px;
      line-height: 36px;
      color: var(--el-text-color-placeholder);
      font-size: 12px;
    }

    .kpi-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--el-text-color-regular);
    }

    .kpi-trend {
      display: flex;
      align-items: center;
      white-space: nowrap;

      .el-icon {
        font-size: 16px;
        margin-left: 4px;
      }
    }

    .kpi-prev {
      color: var(--el-text-color-placeholder);
      font-size: 12px;
    }
  }
</style>
