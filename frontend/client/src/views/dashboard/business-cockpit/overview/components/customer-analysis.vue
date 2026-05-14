<!-- 经营驾驶舱 - 客户类型分布 -->
<template>
  <ele-card header="客户类型分布" class="customer-card" v-loading="loading">
    <div v-if="dist.length === 0" class="empty-state">暂无客户数据</div>
    <v-chart
      v-else
      ref="chartRef"
      :option="chartOption"
      style="height: 320px"
    />
    <el-divider style="margin: 12px 0" />
    <div class="dist-summary">
      <div
        v-for="item in dist"
        :key="item.customerType"
        class="dist-item"
      >
        <span class="dist-dot" :style="{ background: colorFor(item.customerType) }" />
        <span class="dist-name">{{ item.label }}</span>
        <span class="dist-value">
          {{ item.waybillCount }}单 · ¥{{ formatNumber(Math.round(item.revenue)) }}
        </span>
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
  import { getCustomerTypeDist } from '@/api/dashboard/cockpit';
  import type { CustomerTypeDistItem } from '@/api/dashboard/cockpit/model';
  import { useCockpitFilter } from '../composables/use-cockpit-filter';

  use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent]);

  const { state } = useCockpitFilter();

  const dist = ref<CustomerTypeDistItem[]>([]);
  const loading = ref(false);
  const chartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([chartRef]);

  const chartOption: EChartsCoreOption = reactive({});

  const TYPE_COLORS: Record<number, string> = {
    0: '#5b8ff9', // 主机厂
    1: '#5ad8a6', // 贸易商
    2: '#5d7092', // 经销商
    3: '#f6bd16', // 个人
    4: '#e8684a', // 其他
    [-1]: '#cccccc' // 未知
  };

  const colorFor = (t: number) => TYPE_COLORS[t] || '#cccccc';

  const formatNumber = (n: number) => {
    if (!Number.isFinite(n)) return '0';
    return n.toLocaleString('zh-CN');
  };

  const renderChart = () => {
    const items = dist.value;
    Object.assign(chartOption, {
      tooltip: {
        trigger: 'item',
        formatter: (params: any) =>
          `${params.name}<br/>运费：¥${formatNumber(
            Math.round(params.value)
          )} (${params.percent}%)`
      },
      legend: {
        bottom: 0,
        type: 'scroll',
        data: items.map((i) => i.label)
      },
      color: items.map((i) => colorFor(i.customerType)),
      series: [
        {
          name: '客户类型分布',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderRadius: 4,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {d}%'
          },
          data: items.map((i) => ({
            name: i.label,
            value: Math.round(i.revenue)
          }))
        }
      ]
    });
  };

  const load = async () => {
    loading.value = true;
    try {
      dist.value = await getCustomerTypeDist({
        start: state.start,
        end: state.end
      });
      renderChart();
    } catch (e: any) {
      EleMessage.error({ message: e?.message || '加载客户分布失败', plain: true });
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
  .customer-card {
    margin-bottom: 16px;
  }

  .empty-state {
    height: 320px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
  }

  .dist-summary {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 24px;
  }

  .dist-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: var(--el-text-color-regular);

    .dist-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      display: inline-block;
    }

    .dist-name {
      min-width: 48px;
    }

    .dist-value {
      color: var(--el-text-color-placeholder);
    }
  }
</style>
