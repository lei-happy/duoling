<!-- 利润总览 - 成本构成（按费用类型分摊后的净额饼图） -->
<template>
  <ele-card class="cost-card" header="成本构成（按费用类型）">
    <div class="cost-body" v-loading="loading">
      <v-chart
        ref="chartRef"
        :option="chartOption"
        class="cost-chart"
        autoresize
      />
      <div v-if="items.length === 0 && !loading" class="cost-empty">
        暂无成本明细数据
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
  import { PieChart } from 'echarts/charts';
  import { TooltipComponent, LegendComponent } from 'echarts/components';
  import VChart from 'vue-echarts';
  import { useEcharts } from '@/utils/use-echarts';
  import { getCostStructure } from '@/api/dashboard/profit';
  import type { CostStructureItem } from '@/api/dashboard/profit/model';
  import { useProfitFilter } from '../composables/use-profit-filter';

  use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent]);

  const { state } = useProfitFilter();

  const loading = ref(false);
  const items = ref<CostStructureItem[]>([]);
  const chartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([chartRef]);

  const chartOption: EChartsCoreOption = reactive({});

  const PALETTE = [
    '#165dff',
    '#ff7d00',
    '#00b42a',
    '#722ed1',
    '#14c9c9',
    '#f7ba1e',
    '#f53f3f',
    '#3491fa',
    '#7bc616',
    '#ff9a2e'
  ];

  const renderChart = () => {
    // 仅展示正向（加项占比）切片，扣减项以负数出现时过滤
    const positive = items.value.filter((i) => i.amount > 0);
    Object.assign(chartOption, {
      tooltip: {
        trigger: 'item',
        formatter: (p: any) =>
          `${p.marker}${p.name}: ¥${(Number(p.value) / 10000).toFixed(2)} 万 (${p.percent}%)`
      },
      legend: { type: 'scroll', bottom: 0, left: 'center' },
      color: PALETTE,
      series: [
        {
          name: '成本构成',
          type: 'pie',
          radius: ['42%', '68%'],
          center: ['50%', '46%'],
          avoidLabelOverlap: true,
          itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
          label: { formatter: '{b}\n{d}%' },
          data: positive.map((i) => ({ name: i.feeName, value: i.amount }))
        }
      ]
    });
  };

  const load = async () => {
    loading.value = true;
    try {
      items.value = await getCostStructure({
        start: state.start,
        end: state.end
      });
      renderChart();
    } catch (e: unknown) {
      const err = e as { message?: string };
      EleMessage.error({
        message: err?.message || '加载成本构成失败',
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
  .cost-card {
    margin-bottom: 16px;
  }

  .cost-body {
    position: relative;
  }

  .cost-chart {
    width: 100%;
    height: 340px;
  }

  .cost-empty {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
    font-size: 13px;
  }
</style>
