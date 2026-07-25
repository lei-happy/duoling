<!-- 经营驾驶舱 - 计划状态分布（环形 + 运费计算状态堆叠条） -->
<template>
  <ele-card
    header="计划状态分布"
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
      <div v-else class="eff-content">
        <div class="eff-chart-wrap">
          <v-chart
            ref="statusChartRef"
            :option="statusOption"
            class="eff-chart-inner"
            autoresize
          />
        </div>
        <div class="eff-footer">
          <div class="eff-divider" role="separator"></div>
          <div class="eff-metrics">
            <div class="eff-calc-block">
              <div class="eff-calc-strip-head">
                <div class="eff-calc-head-left">
                  <span class="eff-calc-head-title">运费计算状态</span>
                  <ele-tooltip
                    content="统计所选时间内，每张计划的「运费有没有被系统自动算出来、算得是否正常」。"
                    placement="top"
                    :offset="6"
                  >
                    <el-icon class="eff-tip">
                      <QuestionCircleOutlined />
                    </el-icon>
                  </ele-tooltip>
                </div>
                <div v-if="data.totalCount > 0" class="eff-calc-head-right">
                  <span class="eff-calc-head-meta">
                    计算异常
                    <span
                      class="eff-calc-ex-pct"
                      :style="{ color: colorForCalcStatus('exception') }"
                    >
                      {{ calcExceptionPctText }}%
                    </span>
                  </span>
                  <span class="eff-calc-head-meta eff-calc-head-total">
                    · 共 {{ data.totalCount }} 单
                  </span>
                </div>
              </div>
              <div
                v-if="data.totalCount > 0 && calcBarSegments.length"
                class="eff-calc-track"
                role="img"
                :aria-label="calcBarAriaLabel"
              >
                <div
                  v-for="seg in calcBarSegments"
                  :key="seg.calcStatus"
                  class="eff-calc-seg"
                  :style="{
                    flex: `0 0 ${seg.pct.toFixed(4)}%`,
                    minWidth: seg.count ? '3px' : '0',
                    backgroundColor: seg.color
                  }"
                  :title="`${seg.label} ${seg.count} 单（${seg.pct.toFixed(1)}%）`"
                ></div>
              </div>
              <div v-else-if="data.totalCount > 0" class="eff-calc-empty">
                暂无计算状态分布
              </div>
              <div v-else class="eff-calc-empty">本期无计划</div>
              <div v-if="calcBarSegments.length" class="eff-calc-legend">
                <span
                  v-for="seg in calcBarSegments"
                  :key="'lg-' + seg.calcStatus"
                  class="eff-calc-legend-item"
                >
                  <i
                    class="eff-calc-legend-dot"
                    :style="{ backgroundColor: seg.color }"
                  ></i>
                  <span>{{ seg.label }}</span>
                  <span class="eff-calc-legend-num">{{ seg.count }}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, nextTick, reactive, ref } from 'vue';
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

  const STATUS_COLORS = [
    '#c9cdd4', // 待确认
    '#165dff', // 待调度
    '#14c9c9', // 调度中
    '#fadc19', // 运输中
    '#722ed1', // 待签收
    '#34c724', // 已签收
    '#f5319d' // 已关闭
  ];

  /** 与堆叠条一致：按 calc_status 着色 */
  const CALC_STATUS_COLORS: Record<string, string> = {
    pending: '#c9cdd4',
    calculating: '#165dff',
    calculated: '#34c724',
    exception: '#f5319d',
    locked: '#722ed1'
  };

  const colorForCalcStatus = (key: string) =>
    CALC_STATUS_COLORS[key] ?? '#8c8c8c';

  const calcBarSegments = computed(() => {
    const d = data.value;
    const rows = d?.calcStatusDist;
    const total = d?.totalCount ?? 0;
    if (!rows?.length || total <= 0) return [];
    const segs = rows.map((row) => {
      const pct = (row.count / total) * 100;
      return {
        calcStatus: row.calcStatus,
        label: row.label,
        count: row.count,
        color: colorForCalcStatus(row.calcStatus),
        pct
      };
    });
    let sum = segs.reduce((s, x) => s + x.pct, 0);
    if (segs.length && Math.abs(sum - 100) > 0.02) {
      segs[segs.length - 1] = {
        ...segs[segs.length - 1],
        pct: segs[segs.length - 1].pct + (100 - sum)
      };
    }
    return segs;
  });

  const calcExceptionPctText = computed(() => {
    const d = data.value;
    if (!d?.totalCount) return '0.00';
    return (d.calcExceptionRate * 100).toFixed(2);
  });

  const calcBarAriaLabel = computed(() =>
    calcBarSegments.value.map((s) => `${s.label}${s.count}单`).join('，')
  );

  const renderChart = () => {
    if (!data.value) return;
    const items = data.value.statusDist;
    const showLegend = items.length > 3;
    Object.assign(statusOption, {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        show: showLegend,
        bottom: 4,
        left: 'center',
        type: 'scroll',
        itemWidth: 10,
        itemHeight: 10,
        itemGap: 8,
        textStyle: { fontSize: 11 },
        data: items.map((i) => i.label)
      },
      color: items.map((i) => STATUS_COLORS[i.status] || '#cccccc'),
      series: [
        {
          type: 'pie',
          radius: showLegend ? ['40%', '66%'] : ['42%', '68%'],
          center: showLegend ? ['50%', '46%'] : ['50%', '48%'],
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
      await nextTick();
      statusChartRef.value?.resize?.();
    } catch (e: any) {
      EleMessage.error({
        message: e?.message || '加载运营效率失败',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  void load();
</script>

<style lang="scss" scoped>
  .eff-card {
    margin-bottom: 16px;
    height: 100%;
    display: flex;
    flex-direction: column;

    :deep(.el-card__body),
    :deep(.ele-card__body) {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }

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

  .eff-body {
    box-sizing: border-box;
    padding: 16px 12px 8px;
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  /* 与左侧 customer-row 同高：420px 内容区，内部 chart 弹性 + footer 贴底 */
  .eff-content {
    flex: 1;
    min-height: 360px;
    display: flex;
    flex-direction: column;
  }

  @media (min-width: 768px) {
    .eff-content {
      flex: none;
      height: 420px;
      min-height: 420px;
    }
  }

  .eff-chart-wrap {
    flex: 1;
    min-height: 0;
    padding: 4px 0 0;
    box-sizing: border-box;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .eff-chart-inner {
    flex: 1;
    min-height: 0;
    width: 100%;
    height: 100%;
  }

  .eff-footer {
    flex-shrink: 0;
    padding-top: 2px;
  }

  .eff-divider {
    height: 1px;
    margin: 0 0 6px;
    background-color: var(--el-border-color-lighter);
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
    padding: 0 0 2px;
  }

  .eff-calc-block {
    margin-bottom: 0;
  }

  .eff-calc-strip-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 6px;
    flex-wrap: wrap;
  }

  .eff-calc-head-left {
    display: flex;
    align-items: center;
    gap: 4px;
    min-width: 0;

    .eff-tip {
      font-size: 14px;
      cursor: help;
      color: var(--el-text-color-placeholder);
    }
  }

  .eff-calc-head-title {
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .eff-calc-head-right {
    display: flex;
    align-items: baseline;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 0;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eff-calc-head-meta {
    color: var(--el-text-color-secondary);
  }

  .eff-calc-ex-pct {
    font-weight: 600;
    margin-left: 2px;
  }

  .eff-calc-head-total {
    margin-left: 2px;
  }

  .eff-calc-track {
    display: flex;
    width: 100%;
    height: 10px;
    border-radius: 999px;
    overflow: hidden;
    background-color: var(--el-fill-color-dark, #e4e7ed);
  }

  .eff-calc-seg {
    height: 100%;
    flex-shrink: 0;
    box-sizing: border-box;
    transition: opacity 0.15s ease;
  }

  .eff-calc-seg:hover {
    opacity: 0.88;
  }

  .eff-calc-empty {
    font-size: 12px;
    color: var(--el-text-color-placeholder);
    padding: 6px 0 4px;
  }

  .eff-calc-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 14px;
    margin-top: 6px;
    font-size: 12px;
    color: var(--el-text-color-regular);
  }

  .eff-calc-legend-item {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }

  .eff-calc-legend-dot {
    width: 8px;
    height: 8px;
    border-radius: 2px;
    flex-shrink: 0;
  }

  .eff-calc-legend-num {
    color: var(--el-text-color-secondary);
    font-variant-numeric: tabular-nums;
  }
</style>
