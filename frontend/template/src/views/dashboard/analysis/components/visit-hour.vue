<template>
  <ele-card
    header="最近1小时访问情况"
    :body-style="{ padding: '16px 6px 0 0' }"
  >
    <v-chart
      ref="visitHourChartRef"
      :option="visitHourChartOption"
      style="height: 362px"
    />
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { use } from 'echarts/core';
  import type { EChartsCoreOption } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { LineChart } from 'echarts/charts';
  import {
    GridComponent,
    TooltipComponent,
    LegendComponent
  } from 'echarts/components';
  import VChart from 'vue-echarts';
  import { getVisitHourList } from '@/api/dashboard/analysis';
  import { useEcharts } from '@/utils/use-echarts';

  use([
    CanvasRenderer,
    LineChart,
    GridComponent,
    TooltipComponent,
    LegendComponent
  ]);

  const visitHourChartRef = ref<InstanceType<typeof VChart> | null>(null);

  useEcharts([visitHourChartRef]);

  /** 最近 1 小时访问情况折线图配置 */
  const visitHourChartOption: EChartsCoreOption = reactive({});

  /** 获取最近 1 小时访问情况数据 */
  const getVisitHourData = () => {
    getVisitHourList()
      .then((data) => {
        Object.assign(visitHourChartOption, {
          tooltip: { trigger: 'axis' },
          legend: {
            data: ['浏览量', '访问量'],
            right: 20
          },
          xAxis: [
            {
              type: 'category',
              boundaryGap: false,
              data: data.map((d) => d.time)
            }
          ],
          yAxis: [{ type: 'value' }],
          series: [
            {
              name: '浏览量',
              type: 'line',
              smooth: true,
              symbol: 'none',
              areaStyle: {
                color: {
                  type: 'linear',
                  x: 0,
                  y: 0,
                  x2: 0,
                  y2: 1,
                  colorStops: [
                    { offset: 0, color: 'rgba(91, 143, 249, 0.6)' },
                    { offset: 1, color: 'rgba(91, 143, 249, 0.2)' }
                  ]
                }
              },
              data: data.map((d) => d.views)
            },
            {
              name: '访问量',
              type: 'line',
              smooth: true,
              symbol: 'none',
              areaStyle: {
                color: {
                  type: 'linear',
                  x: 0,
                  y: 0,
                  x2: 0,
                  y2: 1,
                  colorStops: [
                    { offset: 0, color: 'rgba(97, 221, 170, 0.6)' },
                    { offset: 1, color: 'rgba(97, 221, 170, 0.2)' }
                  ]
                }
              },
              data: data.map((d) => d.visits)
            }
          ]
        });
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  getVisitHourData();
</script>
