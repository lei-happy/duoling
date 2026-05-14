<!-- 经营驾驶舱 - 商品车品牌排行（左：横向柱状 Top10；右：品牌词云 Top20） -->
<template>
  <ele-card header="商品车品牌排行" class="brand-card" v-loading="loading">
    <el-row :gutter="16">
      <el-col :md="16" :sm="14" :xs="24">
        <div class="brand-section-title">Top10 品牌（按发运台数）</div>
        <v-chart
          ref="rankChartRef"
          :option="rankOption"
          style="height: 360px"
        />
      </el-col>
      <el-col :md="8" :sm="10" :xs="24">
        <div class="brand-section-title">品牌词云</div>
        <v-chart
          ref="cloudChartRef"
          :option="cloudOption"
          style="height: 360px"
        />
      </el-col>
    </el-row>
  </ele-card>
</template>

<script lang="ts" setup>
  import { reactive, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { use } from 'echarts/core';
  import type { EChartsCoreOption } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { BarChart } from 'echarts/charts';
  import { GridComponent, TooltipComponent } from 'echarts/components';
  import VChart from 'vue-echarts';
  import 'echarts-wordcloud';
  import { useEcharts } from '@/utils/use-echarts';
  import { getVehicleBrandRank } from '@/api/dashboard/cockpit';
  import type { VehicleBrandRankItem } from '@/api/dashboard/cockpit/model';
  import { useCockpitFilter } from '../composables/use-cockpit-filter';

  use([CanvasRenderer, BarChart, GridComponent, TooltipComponent]);

  const { state } = useCockpitFilter();

  const loading = ref(false);
  const rankChartRef = ref<InstanceType<typeof VChart> | null>(null);
  const cloudChartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([rankChartRef, cloudChartRef]);

  const rankOption: EChartsCoreOption = reactive({});
  const cloudOption: EChartsCoreOption = reactive({});

  const CLOUD_COLORS = [
    '#5b8ff9',
    '#5ad8a6',
    '#5d7092',
    '#f6bd16',
    '#e8684a',
    '#6dc8ec',
    '#945fb9',
    '#ff9d4d',
    '#269a99',
    '#ff99c3'
  ];

  const buildRankOption = (
    items: VehicleBrandRankItem[]
  ): EChartsCoreOption => {
    const top = items.slice(0, 10);
    const sorted = [...top].reverse();
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params: any) => {
          const p = Array.isArray(params) ? params[0] : params;
          const it = sorted[p.dataIndex];
          if (!it) return p.name;
          return `${it.brandName}<br/>台数：${it.vehicleQuantity}<br/>运单数：${it.waybillCount}`;
        }
      },
      grid: { left: 12, right: 36, top: 16, bottom: 12, containLabel: true },
      xAxis: { type: 'value', axisLabel: { fontSize: 11 } },
      yAxis: {
        type: 'category',
        data: sorted.map((it) => it.brandName),
        axisLabel: { fontSize: 12 }
      },
      series: [
        {
          type: 'bar',
          data: sorted.map((it) => it.vehicleQuantity),
          itemStyle: {
            borderRadius: [0, 4, 4, 0],
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [
                { offset: 0, color: '#b0d0ff' },
                { offset: 1, color: '#5b8ff9' }
              ]
            }
          },
          label: {
            show: true,
            position: 'right',
            formatter: '{c} 台',
            fontSize: 11
          }
        }
      ]
    };
  };

  const buildCloudOption = (
    items: VehicleBrandRankItem[]
  ): EChartsCoreOption => {
    return {
      tooltip: {
        show: true,
        confine: true,
        borderWidth: 1,
        formatter: (params: any) => `${params.name}：${params.value} 台`
      },
      series: [
        {
          type: 'wordCloud',
          width: '100%',
          height: '100%',
          sizeRange: [14, 40],
          rotationRange: [0, 0],
          gridSize: 8,
          shape: 'circle',
          textStyle: {
            color: () =>
              CLOUD_COLORS[Math.floor(Math.random() * CLOUD_COLORS.length)]
          },
          emphasis: {
            textStyle: {
              textShadowBlur: 4,
              textShadowColor: 'rgba(0,0,0,0.2)'
            }
          },
          data: items.map((it) => ({
            name: it.brandName,
            value: it.vehicleQuantity
          }))
        }
      ]
    };
  };

  const load = async () => {
    loading.value = true;
    try {
      const data = await getVehicleBrandRank({
        start: state.start,
        end: state.end,
        limit: 20
      });
      Object.assign(rankOption, buildRankOption(data));
      Object.assign(cloudOption, buildCloudOption(data));
    } catch (e: any) {
      EleMessage.error({ message: e?.message || '加载品牌排行失败', plain: true });
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
  .brand-card {
    margin-bottom: 16px;
  }

  .brand-section-title {
    padding: 6px 0;
    color: var(--el-text-color-regular);
  }
</style>
