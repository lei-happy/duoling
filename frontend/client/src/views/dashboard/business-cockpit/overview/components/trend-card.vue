<!-- 经营驾驶舱 - 收入与单量趋势 + TopN 客户运费贡献排行 -->
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
          { name: 'revenue', label: '运费收入趋势' },
          { name: 'waybill', label: '运单量趋势' }
        ]"
        @tabChange="renderChart"
      />
    </template>
    <template #extra>
      <div class="hidden-xs-only" style="display: flex; align-items: center">
        <el-radio-group v-model="granularity" @change="load">
          <el-radio-button value="day" label="日" />
          <el-radio-button value="week" label="周" />
          <el-radio-button value="month" label="月" />
        </el-radio-group>
      </div>
    </template>
    <div class="trend-body" v-loading="loading">
      <el-row :gutter="16">
        <el-col :md="17" :sm="15" :xs="24">
          <div class="trend-section-title">
            {{ metric === 'revenue' ? '运费收入与运单数' : '运单量与发运台数' }}
          </div>
          <v-chart
            ref="trendChartRef"
            :option="trendOption"
            style="height: 320px"
          />
        </el-col>
        <el-col :md="7" :sm="9" :xs="24">
          <div class="trend-section-title">TopN 客户运费贡献</div>
          <div class="rank-list">
            <div
              v-for="(item, index) in customerRank"
              :key="index"
              class="rank-item"
            >
              <el-tag
                size="small"
                :disable-transitions="true"
                :type="index < 3 ? void 0 : 'info'"
                :effect="index < 3 ? 'dark' : 'light'"
                :color="index < 3 ? '#314659' : void 0"
                style="border: none; border-radius: 50%; width: 20px"
              >
                {{ index + 1 }}
              </el-tag>
              <ele-ellipsis class="rank-item-text">
                {{ item.customerName }}
              </ele-ellipsis>
              <ele-text type="placeholder">
                ¥{{ formatNumber(Math.round(item.revenue)) }}
              </ele-text>
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
  import { reactive, ref, watch } from 'vue';
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
  import {
    getCustomerRank,
    getRevenueTrend
  } from '@/api/dashboard/cockpit';
  import type {
    CustomerRankItem,
    RevenueTrendPoint
  } from '@/api/dashboard/cockpit/model';
  import { useCockpitFilter } from '../composables/use-cockpit-filter';

  use([
    CanvasRenderer,
    LineChart,
    BarChart,
    GridComponent,
    TooltipComponent,
    LegendComponent
  ]);

  const { state } = useCockpitFilter();

  const metric = ref<'revenue' | 'waybill'>('revenue');
  const granularity = ref<'day' | 'week' | 'month'>('day');
  const loading = ref(false);
  const trendData = ref<RevenueTrendPoint[]>([]);
  const customerRank = ref<CustomerRankItem[]>([]);

  const trendChartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([trendChartRef]);

  const trendOption: EChartsCoreOption = reactive({});

  const formatNumber = (n: number) => {
    if (!Number.isFinite(n)) return '0';
    return n.toLocaleString('zh-CN');
  };

  const renderChart = () => {
    const points = trendData.value;
    const xData = points.map((p) => p.date);
    if (metric.value === 'revenue') {
      Object.assign(trendOption, {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          valueFormatter: (val: any) => {
            if (typeof val === 'number') {
              return `¥ ${formatNumber(Math.round(val))}`;
            }
            return val;
          }
        },
        legend: { data: ['运费收入', '运单数'], right: 20 },
        xAxis: [{ type: 'category', data: xData, boundaryGap: true }],
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
            name: '运费收入',
            type: 'bar',
            yAxisIndex: 0,
            data: points.map((p) => p.revenue),
            itemStyle: {
              borderRadius: [6, 6, 0, 0],
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: '#b0d0ff' },
                  { offset: 0.4, color: '#80a9fa' },
                  { offset: 1, color: '#5b8ff9' }
                ]
              }
            }
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
            data: points.map((p) => p.waybillCount)
          }
        ]
      });
    } else {
      Object.assign(trendOption, {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: ['运单数', '发运台数'], right: 20 },
        xAxis: [{ type: 'category', data: xData, boundaryGap: true }],
        yAxis: [
          { type: 'value', name: '运单数' },
          { type: 'value', name: '发运台数', alignTicks: true }
        ],
        series: [
          {
            name: '运单数',
            type: 'bar',
            yAxisIndex: 0,
            data: points.map((p) => p.waybillCount),
            itemStyle: {
              borderRadius: [6, 6, 0, 0],
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: '#c2f0e0' },
                  { offset: 0.4, color: '#7cd7b5' },
                  { offset: 1, color: '#61ddaa' }
                ]
              }
            }
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
            data: points.map((p) => p.vehicleQuantity)
          }
        ]
      });
    }
  };

  const load = async () => {
    loading.value = true;
    try {
      const [trend, rank] = await Promise.all([
        getRevenueTrend({
          start: state.start,
          end: state.end,
          granularity: granularity.value
        }),
        getCustomerRank({
          start: state.start,
          end: state.end,
          limit: 10
        })
      ]);
      trendData.value = trend;
      customerRank.value = rank;
      renderChart();
    } catch (e: any) {
      EleMessage.error({ message: e?.message || '加载趋势数据失败', plain: true });
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
  .trend-card {
    margin-bottom: 16px;
  }

  .trend-body {
    padding: 16px 0 10px 0;
  }

  .trend-section-title {
    padding: 6px 20px;
    color: var(--el-text-color-regular);
  }

  .rank-list {
    padding-bottom: 8px;
  }

  .rank-item {
    display: flex;
    align-items: center;
    padding: 0 20px;
    margin-top: 18px;
    box-sizing: border-box;

    .rank-item-text {
      flex: 1;
      padding-left: 12px;
    }
  }

  .rank-empty {
    padding: 24px 20px;
    color: var(--el-text-color-placeholder);
    font-size: 13px;
  }
</style>
