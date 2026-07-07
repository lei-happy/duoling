<!-- 利润总览 - 承运结构（自有 / 承运商 / 社会运力 的收入、成本、毛利对比） -->
<template>
  <ele-card class="carrier-card" header="承运结构（收入 / 成本 / 毛利）">
    <div class="carrier-body" v-loading="loading">
      <v-chart
        ref="chartRef"
        :option="chartOption"
        class="carrier-chart"
        autoresize
      />
      <div class="carrier-table">
        <div v-for="row in rows" :key="row.carrierType" class="carrier-row">
          <span class="carrier-name">{{ row.label }}</span>
          <span class="carrier-metric">
            收入 <b>¥{{ formatWan(row.revenue) }}</b>
          </span>
          <span class="carrier-metric">
            毛利
            <b :class="row.grossProfit >= 0 ? 'pos' : 'neg'"
              >¥{{ formatWan(row.grossProfit) }}</b
            >
          </span>
          <span class="carrier-metric">
            毛利率
            <b>{{
              row.grossMargin === null
                ? '—'
                : `${(row.grossMargin * 100).toFixed(1)}%`
            }}</b>
          </span>
        </div>
        <div v-if="rows.length === 0 && !loading" class="carrier-empty">
          暂无承运结构数据
        </div>
      </div>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { reactive, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { use } from 'echarts/core';
  import type { EChartsCoreOption } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { BarChart } from 'echarts/charts';
  import {
    GridComponent,
    TooltipComponent,
    LegendComponent
  } from 'echarts/components';
  import VChart from 'vue-echarts';
  import { useEcharts } from '@/utils/use-echarts';
  import { getCarrierStructure } from '@/api/dashboard/profit';
  import type { CarrierStructureItem } from '@/api/dashboard/profit/model';
  import { useProfitFilter } from '../composables/use-profit-filter';

  use([
    CanvasRenderer,
    BarChart,
    GridComponent,
    TooltipComponent,
    LegendComponent
  ]);

  const { state } = useProfitFilter();

  const loading = ref(false);
  const rows = ref<CarrierStructureItem[]>([]);
  const chartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([chartRef]);

  const chartOption: EChartsCoreOption = reactive({});

  const formatWan = (n: number) =>
    (n / 10000).toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });

  const renderChart = () => {
    const labels = rows.value.map((r) => r.label);
    Object.assign(chartOption, {
      grid: { left: 8, right: 12, top: 40, bottom: 0, containLabel: true },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        valueFormatter: (val: unknown) =>
          typeof val === 'number' ? `¥ ${(val / 10000).toFixed(2)} 万` : ''
      },
      legend: { top: 2, left: 'center', data: ['收入', '成本', '毛利'] },
      color: ['#165dff', '#ff7d00', '#00b42a'],
      xAxis: { type: 'category', data: labels },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: (val: number) =>
            Math.abs(val) >= 10000 ? `${(val / 10000).toFixed(1)}万` : `${val}`
        }
      },
      series: [
        {
          name: '收入',
          type: 'bar',
          barMaxWidth: 28,
          itemStyle: { borderRadius: [4, 4, 0, 0] },
          data: rows.value.map((r) => r.revenue)
        },
        {
          name: '成本',
          type: 'bar',
          barMaxWidth: 28,
          itemStyle: { borderRadius: [4, 4, 0, 0] },
          data: rows.value.map((r) => r.cost)
        },
        {
          name: '毛利',
          type: 'bar',
          barMaxWidth: 28,
          itemStyle: { borderRadius: [4, 4, 0, 0] },
          data: rows.value.map((r) => r.grossProfit)
        }
      ]
    });
  };

  const load = async () => {
    loading.value = true;
    try {
      rows.value = await getCarrierStructure({
        start: state.start,
        end: state.end
      });
      renderChart();
    } catch (e: unknown) {
      const err = e as { message?: string };
      EleMessage.error({
        message: err?.message || '加载承运结构失败',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  watch(() => [state.start, state.end], load);
  void load();
</script>

<style lang="scss" scoped>
  .carrier-card {
    margin-bottom: 16px;
  }

  .carrier-chart {
    width: 100%;
    height: 280px;
  }

  .carrier-table {
    margin-top: 8px;
  }

  .carrier-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px 16px;
    padding: 8px 4px;
    border-top: 1px solid var(--el-border-color-lighter);
    font-size: 13px;
  }

  .carrier-name {
    min-width: 72px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .carrier-metric {
    color: var(--el-text-color-regular);

    b {
      color: var(--el-text-color-primary);
      font-variant-numeric: tabular-nums;
    }

    b.pos {
      color: var(--el-color-danger);
    }

    b.neg {
      color: var(--el-color-success);
    }
  }

  .carrier-empty {
    padding: 24px;
    text-align: center;
    color: var(--el-text-color-placeholder);
    font-size: 13px;
  }
</style>
