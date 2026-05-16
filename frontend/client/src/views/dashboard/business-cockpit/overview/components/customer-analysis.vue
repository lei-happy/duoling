<!-- 经营驾驶舱 - 客户类型分布 + 按类型/运费的客户排行 -->
<template>
  <ele-card
    header="客户类型分布"
    :header-style="{ paddingTop: 0, paddingBottom: 0 }"
    :body-style="{ padding: 0 }"
    class="customer-card"
  >
    <template #extra>
      <div class="hidden-xs-only customer-card-extra">
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
          class="customer-date-range"
          @calendar-change="onCalendarChange"
          @change="onDateRangeChange"
        />
      </div>
    </template>
    <div class="customer-body" v-loading="loading">
      <el-row :gutter="16" class="customer-row">
        <el-col :md="14" :sm="13" :xs="24" class="customer-chart-col">
          <div class="customer-chart-wrap">
            <div v-if="dist.length === 0" class="empty-state">暂无客户数据</div>
            <v-chart
              v-else
              ref="chartRef"
              :option="chartOption"
              class="customer-chart-inner"
              autoresize
              @click="onPieClick"
            />
          </div>
        </el-col>
        <el-col :md="10" :sm="11" :xs="24" class="customer-rank-col">
          <div class="customer-rank-meta">
            <ele-text type="placeholder" class="customer-rank-sub rank-meta-row">
              <span>{{ rankMetaLead }}</span>
              <span class="rank-meta-sep"> · </span>
              <el-tag
                v-if="selectedCustomerType !== null"
                size="small"
                effect="dark"
                :color="selectedTypeColor"
                class="customer-type-hint-tag"
                :disable-transitions="true"
              >
                {{ selectedTypeLabel }}
              </el-tag>
              <span v-else>全部类型</span>
            </ele-text>
          </div>
          <div class="rank-list">
            <div
              v-for="(item, index) in customerRank"
              :key="`${item.customerId ?? 'x'}-${index}`"
              class="rank-item"
            >
              <el-tag
                size="small"
                class="rank-num"
                :disable-transitions="true"
                :type="index < 3 ? void 0 : 'info'"
                :effect="index < 3 ? 'dark' : 'light'"
                :color="index < 3 ? '#314659' : void 0"
              >
                {{ index + 1 }}
              </el-tag>
              <div class="rank-item-body">
                <ele-ellipsis class="rank-name">
                  {{ item.customerName }}
                </ele-ellipsis>
                <div class="rank-tags">
                  <el-tag type="primary" effect="light" size="small">
                    ¥{{ formatNumber(Math.round(item.revenue)) }}
                  </el-tag>
                  <el-tag type="success" effect="light" size="small">
                    {{ item.waybillCount }} 单
                  </el-tag>
                </div>
              </div>
            </div>
            <div v-if="customerRank.length === 0" class="rank-empty">
              暂无客户数据
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import dayjs from 'dayjs';
  import { EleMessage } from 'ele-admin-plus';
  import { use } from 'echarts/core';
  import type { EChartsCoreOption } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { PieChart } from 'echarts/charts';
  import { TooltipComponent, LegendComponent } from 'echarts/components';
  import VChart from 'vue-echarts';
  import { useEcharts } from '@/utils/use-echarts';
  import { getCustomerRank, getCustomerTypeDist } from '@/api/dashboard/cockpit';
  import type {
    CustomerRankItem,
    CustomerTypeDistItem
  } from '@/api/dashboard/cockpit/model';

  use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent]);

  const API_DT = 'YYYY-MM-DD HH:mm:ss';
  const MAX_RANGE_DAYS = 60;
  const DEFAULT_RANGE_DAYS = 15;
  const RANK_LIMIT = 5000;

  const dateRange = ref<[string, string]>(defaultDateRange());
  const calendarAnchor = ref<dayjs.Dayjs | null>(null);

  const dist = ref<CustomerTypeDistItem[]>([]);
  const customerRank = ref<CustomerRankItem[]>([]);
  /** null：全部类型按运费排行；有值：仅该客户类型内排行 */
  const selectedCustomerType = ref<number | null>(null);

  const loading = ref(false);
  const chartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([chartRef]);

  const chartOption: EChartsCoreOption = reactive({});

  const TYPE_COLORS: Record<number, string> = {
    0: '#5b8ff9',
    1: '#5ad8a6',
    2: '#5d7092',
    3: '#f6bd16',
    4: '#e8684a',
    [-1]: '#cccccc'
  };

  const colorFor = (t: number) => TYPE_COLORS[t] || '#cccccc';

  function defaultDateRange(): [string, string] {
    const end = dayjs().startOf('day');
    const start = end.subtract(DEFAULT_RANGE_DAYS - 1, 'day');
    return [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')];
  }

  const formatNumber = (n: number) => {
    if (!Number.isFinite(n)) return '0';
    return n.toLocaleString('zh-CN');
  };

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

  const rankMetaLead = computed(() => {
    const r = dateRange.value;
    const range = r?.[0] && r?.[1] ? `${r[0]} — ${r[1]}` : '';
    return `${range} · 按运费`;
  });

  const selectedTypeLabel = computed(() => {
    if (selectedCustomerType.value === null) return '';
    return (
      dist.value.find((i) => i.customerType === selectedCustomerType.value)
        ?.label ?? '该类型'
    );
  });

  const selectedTypeColor = computed(() => {
    if (selectedCustomerType.value === null) return '';
    return colorFor(selectedCustomerType.value);
  });

  const rankParams = () => {
    const win = toApiWindow(dateRange.value);
    return {
      start: win.start,
      end: win.end,
      limit: RANK_LIMIT,
      sort_by: 'revenue' as const,
      ...(selectedCustomerType.value !== null
        ? { customer_type: selectedCustomerType.value }
        : {})
    };
  };

  const renderChart = () => {
    const items = dist.value;
    const totalOrders = items.reduce((s, i) => s + (i.waybillCount || 0), 0);
    const sel = selectedCustomerType.value;

    Object.assign(chartOption, {
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          const wb = Number(params?.data?.waybillCount ?? 0);
          const rev = Number(params?.value ?? 0);
          const pctRev = params?.percent ?? '0';
          const pctWb =
            totalOrders > 0 ? ((wb / totalOrders) * 100).toFixed(2) : '0.00';
          const name = params?.name ?? '';
          return `${name}<br/>单数：${wb}（${pctWb}%）<br/>运费：¥${formatNumber(
            Math.round(rev)
          )}（${pctRev}%）`;
        }
      },
      legend: {
        bottom: 4,
        type: 'scroll',
        data: items.map((i) => i.label)
      },
      color: items.map((i) => colorFor(i.customerType)),
      series: [
        {
          name: '客户类型分布',
          type: 'pie',
          radius: ['40%', '68%'],
          center: ['48%', '46%'],
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
          data: items.map((i) => {
            const on =
              sel === null ? false : sel === i.customerType;
            return {
              name: i.label,
              value: Math.round(i.revenue),
              customerType: i.customerType,
              waybillCount: i.waybillCount,
              itemStyle: {
                borderColor: on ? '#0e42d2' : '#fff',
                borderWidth: on ? 3 : 2,
                shadowBlur: on ? 10 : 0,
                shadowColor: 'rgba(22,93,255,0.22)'
              }
            };
          })
        }
      ]
    });
  };

  async function loadRankOnly() {
    customerRank.value = await getCustomerRank(rankParams());
  }

  async function loadAll() {
    loading.value = true;
    try {
      const win = toApiWindow(dateRange.value);
      const [d, r] = await Promise.all([
        getCustomerTypeDist({ start: win.start, end: win.end }),
        getCustomerRank(rankParams())
      ]);
      dist.value = d;
      customerRank.value = r;
      renderChart();
    } catch (e: unknown) {
      const err = e as { message?: string };
      EleMessage.error({
        message: err?.message || '加载客户分析失败',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  }

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
    selectedCustomerType.value = null;
    void loadAll();
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

  const onPieClick = (params: Record<string, unknown>) => {
    if (params.componentType !== 'series' || params.seriesType !== 'pie') {
      return;
    }
    const data = params.data as
      | { customerType?: number }
      | undefined;
    if (data?.customerType === undefined) return;
    const t = data.customerType;
    if (selectedCustomerType.value === t) {
      selectedCustomerType.value = null;
    } else {
      selectedCustomerType.value = t;
    }
    loading.value = true;
    loadRankOnly()
      .then(() => {
        renderChart();
      })
      .catch((e: unknown) => {
        const err = e as { message?: string };
        EleMessage.error({
          message: err?.message || '加载排行失败',
          plain: true
        });
      })
      .finally(() => {
        loading.value = false;
      });
  };

  void loadAll();
</script>

<style lang="scss" scoped>
  .customer-card {
    margin-bottom: 16px;
    flex: 1;
    width: 100%;
    min-height: 0;
    display: flex;
    flex-direction: column;

    /* 标题区域高度与标准卡片（如「运营效率」）保持一致：52px */
    :deep(.ele-card-header) {
      min-height: 52px;
    }

    :deep(.ele-card-title) {
      flex: 1;
      min-width: 0;
    }

    :deep(.el-card__body),
    :deep(.ele-card__body) {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }
  }

  .customer-card-extra {
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }

  /* 与趋势卡 #extra 完全一致：default + 220px（仅显示 YYYY-MM-DD）
     需要用 :deep 提升优先级，覆盖 el-date-editor--daterange 默认 352px */
  .customer-card-extra :deep(.el-date-editor.el-date-editor--daterange) {
    width: 250px;
  }

  .customer-body {
    padding: 16px 0 8px 0;
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .customer-row {
    align-items: stretch;
    flex: 1;
    min-height: 0;
  }

  .customer-chart-col,
  .customer-rank-col {
    display: flex;
    flex-direction: column;
    min-height: 340px;
  }

  @media (min-width: 768px) {
    .customer-chart-col,
    .customer-rank-col {
      height: 380px;
      min-height: 380px;
    }
  }

  .customer-chart-wrap {
    flex: 1;
    min-height: 0;
    padding: 4px 8px 4px 12px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
  }

  .customer-chart-inner {
    flex: 1;
    width: 100%;
    min-height: 320px;
    height: 100%;
  }

  .empty-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
    font-size: 13px;
  }

  .customer-rank-meta {
    flex-shrink: 0;
    padding: 2px 12px 8px 20px;
    line-height: 1.3;
  }

  .customer-rank-sub {
    font-size: 12px;
  }

  .rank-meta-row {
    display: inline-flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0;
    line-height: 1.5;
  }

  .rank-meta-sep {
    white-space: pre;
  }

  .customer-type-hint-tag {
    font-weight: 600;
    border: none;
    vertical-align: middle;
  }

  .rank-list {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 0 6px 4px 12px;
    box-sizing: border-box;
  }

  .rank-item {
    display: flex;
    align-items: flex-start;
    padding: 8px 10px 8px 12px;
    margin-top: 0;
    box-sizing: border-box;
    border-radius: 4px;
  }

  .rank-item:nth-child(odd) {
    background-color: var(--el-fill-color-extra-light, rgba(0, 0, 0, 0.03));
  }

  .rank-item:nth-child(even) {
    background-color: transparent;
  }

  .rank-num {
    flex-shrink: 0;
    border: none !important;
    border-radius: 50% !important;
    width: 22px;
    height: 22px;
    padding: 0 !important;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .rank-item-body {
    flex: 1;
    min-width: 0;
    padding-left: 10px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .rank-name {
    font-size: 13px;
    line-height: 1.35;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .rank-tags {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
  }

  .rank-empty {
    padding: 24px 20px;
    color: var(--el-text-color-placeholder);
    font-size: 13px;
  }
</style>
