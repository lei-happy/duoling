<!-- 经营驾驶舱 - 热门起讫点（左：出发地 Top10，右：目的地 Top10） -->
<template>
  <ele-card header="热门起讫点" class="route-card" v-loading="loading">
    <el-row :gutter="16">
      <el-col :md="12" :sm="24" :xs="24">
        <div class="route-section-title">出发地 Top10</div>
        <v-chart
          ref="originChartRef"
          :option="originOption"
          style="height: 360px"
        />
      </el-col>
      <el-col :md="12" :sm="24" :xs="24">
        <div class="route-section-title">目的地 Top10</div>
        <v-chart
          ref="destChartRef"
          :option="destOption"
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
  import { useEcharts } from '@/utils/use-echarts';
  import { getRegionRank } from '@/api/dashboard/cockpit';
  import type { RegionRankItem } from '@/api/dashboard/cockpit/model';
  import { useCockpitFilter } from '../composables/use-cockpit-filter';

  use([CanvasRenderer, BarChart, GridComponent, TooltipComponent]);

  const { state } = useCockpitFilter();

  const loading = ref(false);
  const originChartRef = ref<InstanceType<typeof VChart> | null>(null);
  const destChartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([originChartRef, destChartRef]);

  const originOption: EChartsCoreOption = reactive({});
  const destOption: EChartsCoreOption = reactive({});

  const buildOption = (
    rows: RegionRankItem[],
    color: string
  ): EChartsCoreOption => {
    // 升序排列以便横向柱状图最大值在顶部
    const sorted = [...rows].reverse();
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params: any) => {
          const p = Array.isArray(params) ? params[0] : params;
          const item = sorted[p.dataIndex];
          if (!item) return p.name;
          return `${item.regionName}<br/>
            单量：${item.waybillCount}<br/>
            台数：${item.vehicleQuantity}<br/>
            收入：¥${Math.round(item.revenue).toLocaleString('zh-CN')}`;
        }
      },
      grid: { left: 12, right: 24, top: 16, bottom: 12, containLabel: true },
      xAxis: { type: 'value', axisLabel: { fontSize: 11 } },
      yAxis: {
        type: 'category',
        data: sorted.map((r) => r.regionName),
        axisLabel: { fontSize: 12 }
      },
      series: [
        {
          type: 'bar',
          data: sorted.map((r) => r.waybillCount),
          itemStyle: {
            borderRadius: [0, 4, 4, 0],
            color
          },
          label: {
            show: true,
            position: 'right',
            formatter: '{c} 单',
            fontSize: 11
          }
        }
      ]
    };
  };

  const load = async () => {
    loading.value = true;
    try {
      const [origin, dest] = await Promise.all([
        getRegionRank({
          start: state.start,
          end: state.end,
          type: 'origin',
          limit: 10
        }),
        getRegionRank({
          start: state.start,
          end: state.end,
          type: 'destination',
          limit: 10
        })
      ]);
      Object.assign(originOption, buildOption(origin, '#5b8ff9'));
      Object.assign(destOption, buildOption(dest, '#5ad8a6'));
    } catch (e: any) {
      EleMessage.error({ message: e?.message || '加载起讫点数据失败', plain: true });
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
  .route-card {
    margin-bottom: 16px;
  }

  .route-section-title {
    padding: 6px 0;
    color: var(--el-text-color-regular);
  }
</style>
