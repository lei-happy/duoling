<!-- 经营驾驶舱 - 运单状态分布（环形 + 计算异常率 + 锁定单数） -->
<template>
  <ele-card
    header="运单状态分布"
    :header-style="{ paddingTop: 0, paddingBottom: 0 }"
    :body-style="{ padding: 0 }"
    class="eff-card"
  >
    <template #extra>
      <div class="hidden-xs-only eff-card-extra">
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
          @calendar-change="onCalendarChange"
          @change="onDateRangeChange"
        />
      </div>
    </template>
    <div class="eff-body" v-loading="loading">
      <div v-if="!data" class="empty-state">暂无数据</div>
      <template v-else>
        <div class="eff-chart-wrap">
          <v-chart
            ref="statusChartRef"
            :option="statusOption"
            class="eff-chart-inner"
            autoresize
          />
        </div>
        <el-divider style="margin: 12px 0" />
        <div class="eff-metrics">
          <div class="eff-row">
            <div class="eff-row-label">
              <span>运费计算异常率</span>
              <ele-tooltip
                content="本期内未自动计算运费的运单占比"
                placement="top"
                :offset="6"
              >
                <el-icon class="eff-tip">
                  <QuestionCircleOutlined />
                </el-icon>
              </ele-tooltip>
            </div>
            <div class="eff-row-value">
              <ele-text
                size="lg"
                :type="data.calcExceptionRate >= 0.05 ? 'danger' : 'success'"
              >
                {{ (data.calcExceptionRate * 100).toFixed(2) }}%
              </ele-text>
              <ele-text type="placeholder" size="sm" style="margin-left: 6px">
                ({{ data.calcExceptionCount }} / {{ data.totalCount }})
              </ele-text>
            </div>
          </div>
          <el-progress
            :percentage="
              Math.min(100, Math.round(data.calcExceptionRate * 100))
            "
            :color="data.calcExceptionRate >= 0.05 ? '#f5222d' : '#52c41a'"
            :show-text="false"
            :stroke-width="8"
            style="margin-bottom: 12px"
          />
          <div class="eff-row">
            <div class="eff-row-label">已锁定运单</div>
            <div class="eff-row-value">
              <ele-text size="lg">{{ data.lockedCount }}</ele-text>
              <ele-text type="placeholder" size="sm" style="margin-left: 6px">
                单（不参与重算）
              </ele-text>
            </div>
          </div>
        </div>
      </template>
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
  import { PieChart } from 'echarts/charts';
  import { TooltipComponent, LegendComponent } from 'echarts/components';
  import VChart from 'vue-echarts';
  import { QuestionCircleOutlined } from '@/components/icons';
  import { useEcharts } from '@/utils/use-echarts';
  import { getOperationEfficiency } from '@/api/dashboard/cockpit';
  import type { OperationEfficiency } from '@/api/dashboard/cockpit/model';

  use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent]);

  const API_DT = 'YYYY-MM-DD HH:mm:ss';
  const MAX_RANGE_DAYS = 60;
  const DEFAULT_RANGE_DAYS = 15;

  const dateRange = ref<[string, string]>(defaultDateRange());
  const calendarAnchor = ref<dayjs.Dayjs | null>(null);

  const loading = ref(false);
  const data = ref<OperationEfficiency | null>(null);
  const statusChartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([statusChartRef]);

  const statusOption: EChartsCoreOption = reactive({});

  function defaultDateRange(): [string, string] {
    const end = dayjs().startOf('day');
    const start = end.subtract(DEFAULT_RANGE_DAYS - 1, 'day');
    return [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')];
  }

  function rangeSpanDays(range: [string, string]): number {
    return dayjs(range[1]).diff(dayjs(range[0]), 'day') + 1;
  }

  function toApiWindow(range: [string, string]): { start: string; end: string } {
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

  const STATUS_COLORS = [
    '#bfbfbf', // 待确认
    '#5b8ff9', // 已确认
    '#5d7092', // 已调度
    '#f6bd16', // 运输中
    '#5ad8a6', // 已送达
    '#52c41a', // 已完成
    '#e8684a' // 已取消
  ];

  const renderChart = () => {
    if (!data.value) return;
    const items = data.value.statusDist;
    Object.assign(statusOption, {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        bottom: 0,
        type: 'scroll',
        textStyle: { fontSize: 11 },
        data: items.map((i) => i.label)
      },
      color: items.map(
        (i) => STATUS_COLORS[i.status] || '#cccccc'
      ),
      series: [
        {
          type: 'pie',
          radius: ['38%', '62%'],
          center: ['50%', '42%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderRadius: 4,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}\n{d}%',
            fontSize: 11
          },
          data: items.map((i) => ({ name: i.label, value: i.count }))
        }
      ]
    });
  };

  const load = async () => {
    loading.value = true;
    try {
      const win = toApiWindow(dateRange.value);
      data.value = await getOperationEfficiency({
        start: win.start,
        end: win.end
      });
      renderChart();
    } catch (e: any) {
      EleMessage.error({ message: e?.message || '加载运营效率失败', plain: true });
    } finally {
      loading.value = false;
    }
  };

  void load();
</script>

<style lang="scss" scoped>
  .eff-card {
    margin-bottom: 16px;

    :deep(.ele-card-header) {
      min-height: 52px;
    }

    :deep(.ele-card-title) {
      flex: 1;
      min-width: 0;
    }
  }

  .eff-card-extra {
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }

  .eff-card-extra :deep(.el-date-editor.el-date-editor--daterange) {
    width: 220px;
  }

  /* 与客户类型卡片 customer-body + 图表列纵向占位一致 */
  .eff-body {
    box-sizing: border-box;
    padding: 16px 0 8px 0;
    min-height: 364px;
    display: flex;
    flex-direction: column;
  }

  @media (min-width: 768px) {
    .eff-body {
      min-height: 404px;
    }
  }

  .eff-chart-wrap {
    flex: 1;
    min-height: 0;
    padding: 4px 8px 4px 12px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
  }

  .eff-chart-inner {
    flex: 1;
    width: 100%;
    min-height: 200px;
    height: 100%;
  }

  .empty-state {
    flex: 1;
    min-height: 280px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
  }

  .eff-metrics {
    flex-shrink: 0;
    padding: 4px 12px 0 12px;
  }

  .eff-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;

    .eff-row-label {
      display: flex;
      align-items: center;
      color: var(--el-text-color-regular);
      gap: 4px;
      font-size: 13px;

      .eff-tip {
        font-size: 14px;
        cursor: help;
        color: var(--el-text-color-placeholder);
      }
    }

    .eff-row-value {
      display: flex;
      align-items: baseline;
    }
  }
</style>
