<!-- 经营驾驶舱 - 商品车品牌排行（左：横向柱状 Top10；右：品牌词云 Top20） -->
<template>
  <ele-card
    header="商品车品牌排行[Top10]"
    :header-style="{ paddingTop: 0, paddingBottom: 0 }"
    :body-style="{ padding: 0 }"
    class="brand-card"
  >
    <template #extra>
      <div class="hidden-xs-only brand-card-extra">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          size="default"
          unlink-panels
          range-separator="-"
          value-format="YYYY-MM-DD"
          start-placeholder="开始"
          end-placeholder="结束"
          :disabled-date="disabledDate"
          :clearable="false"
          class="brand-date-range"
          @calendar-change="onCalendarChange"
          @change="onDateRangeChange"
        />
      </div>
    </template>
    <div class="brand-body" v-loading="loading">
      <el-row :gutter="16">
        <el-col :md="16" :sm="14" :xs="24">
          <v-chart
            ref="rankChartRef"
            :option="rankOption"
            style="height: 360px"
          />
        </el-col>
        <el-col :md="8" :sm="10" :xs="24">
          <v-chart
            ref="cloudChartRef"
            :option="cloudOption"
            style="height: 360px"
          />
        </el-col>
      </el-row>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { reactive, ref } from 'vue';
  import dayjs from 'dayjs';
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

  use([CanvasRenderer, BarChart, GridComponent, TooltipComponent]);

  const API_DT = 'YYYY-MM-DD HH:mm:ss';
  const MAX_RANGE_DAYS = 60;
  const DEFAULT_RANGE_DAYS = 15;

  function defaultDateRange(): [string, string] {
    const end = dayjs().startOf('day');
    const start = end.subtract(DEFAULT_RANGE_DAYS - 1, 'day');
    return [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')];
  }

  const dateRange = ref<[string, string]>(defaultDateRange());
  const calendarAnchor = ref<dayjs.Dayjs | null>(null);

  const loading = ref(false);
  const rankChartRef = ref<InstanceType<typeof VChart> | null>(null);
  const cloudChartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([rankChartRef, cloudChartRef]);

  const rankOption: EChartsCoreOption = reactive({});
  const cloudOption: EChartsCoreOption = reactive({});

  function rangeSpanDays(range: [string, string]): number {
    return dayjs(range[1]).diff(dayjs(range[0]), 'day') + 1;
  }

  function toApiWindow(range: [string, string]): {
    start: string;
    end: string;
  } {
    return {
      start: dayjs(range[0]).startOf('day').format(API_DT),
      end: dayjs(range[1]).add(1, 'day').startOf('day').format(API_DT)
    };
  }

  const disabledDate = (time: Date) => {
    const cur = dayjs(time).startOf('day');
    const today = dayjs().startOf('day');
    if (cur.isAfter(today)) return true;
    const anchor = calendarAnchor.value;
    if (!anchor) return false;
    const min = anchor.subtract(MAX_RANGE_DAYS - 1, 'day');
    const max = anchor.add(MAX_RANGE_DAYS - 1, 'day');
    return cur.isBefore(min, 'day') || cur.isAfter(max, 'day');
  };

  const onDateRangeChange = () => {
    calendarAnchor.value = null;
    const r = dateRange.value;
    if (!r?.[0] || !r?.[1]) return;
    if (rangeSpanDays(r) > MAX_RANGE_DAYS) {
      EleMessage.warning({
        message: `时间范围最长 ${MAX_RANGE_DAYS} 天，请重新选择`,
        plain: true
      });
      dateRange.value = defaultDateRange();
    }
    void load();
  };

  const onCalendarChange = (dates: [Date, Date | null]) => {
    const start = dates?.[0];
    const end = dates?.[1];
    if (start && !end) {
      calendarAnchor.value = dayjs(start).startOf('day');
    } else {
      calendarAnchor.value = null;
    }
  };

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
          return `${it.brandName}<br/>台数：${it.vehicleQuantity}<br/>计划数：${it.waybillCount}`;
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
            color: '#5b8ff9'
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
      const win = toApiWindow(dateRange.value);
      const data = await getVehicleBrandRank({
        start: win.start,
        end: win.end,
        limit: 20
      });
      Object.assign(rankOption, buildRankOption(data));
      Object.assign(cloudOption, buildCloudOption(data));
    } catch (e: any) {
      EleMessage.error({
        message: e?.message || '加载品牌排行失败',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  void load();
</script>

<style lang="scss" scoped>
  .brand-card {
    margin-bottom: 16px;

    :deep(.ele-card-header) {
      min-height: 52px;
    }

    :deep(.ele-card-title) {
      flex: 1;
      min-width: 0;
    }
  }

  .brand-card-extra {
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }

  /* 与趋势卡 / 客户类型分布 #extra 日期选择器同规格 */
  .brand-card-extra :deep(.el-date-editor.el-date-editor--daterange) {
    width: 250px;
  }

  .brand-body {
    padding: 16px;
    box-sizing: border-box;
  }
</style>
