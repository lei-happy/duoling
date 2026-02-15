<template>
  <ele-card header="浏览器分布" :body-style="{ padding: 0 }">
    <v-chart
      ref="browserChartRef"
      :option="browserChartOption"
      style="height: 236px"
      @click="handleBrowserChartClick"
    />
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { use } from 'echarts/core';
  import type { EChartsCoreOption } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { PieChart } from 'echarts/charts';
  import { TooltipComponent, LegendComponent } from 'echarts/components';
  import VChart from 'vue-echarts';
  import { getBrowserCountList } from '@/api/dashboard/monitor';
  import { useEcharts } from '@/utils/use-echarts';

  use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent]);

  const browserChartRef = ref<InstanceType<typeof VChart> | null>(null);

  useEcharts([browserChartRef]);

  /** 浏览器分布饼图配置 */
  const browserChartOption: EChartsCoreOption = reactive({});

  /** 获取用户浏览器分布数据 */
  const getBrowserCountData = () => {
    getBrowserCountList()
      .then((data) => {
        Object.assign(browserChartOption, {
          tooltip: {
            trigger: 'item',
            confine: true,
            borderWidth: 1
          },
          legend: {
            bottom: 5,
            itemWidth: 10,
            itemHeight: 10,
            icon: 'circle',
            data: data.map((d) => d.name)
          },
          series: [
            {
              type: 'pie',
              radius: ['45%', '70%'],
              center: ['50%', '43%'],
              label: { show: false },
              data: data,
              itemStyle: { borderRadius: 6 }
            }
          ]
        });
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  /** 图表点击事件 */
  const handleBrowserChartClick = (params: any) => {
    EleMessage.info({
      message: `点击了: ${params.name} , 用户量: ${params.value}`,
      plain: true
    });
  };

  getBrowserCountData();
</script>
