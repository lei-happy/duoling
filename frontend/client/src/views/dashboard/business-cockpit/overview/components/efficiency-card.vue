<!-- 经营驾驶舱 - 运营效率（状态环形 + 计算异常率 + 锁定单数） -->
<template>
  <ele-card header="运营效率" class="eff-card" v-loading="loading">
    <div v-if="!data" class="empty-state">暂无数据</div>
    <template v-else>
      <div class="eff-section-title">运单状态分布</div>
      <v-chart
        ref="statusChartRef"
        :option="statusOption"
        style="height: 220px"
      />
      <el-divider style="margin: 12px 0" />
      <div class="eff-metrics">
        <div class="eff-row">
          <div class="eff-row-label">
            <span>运费计算异常率</span>
            <ele-tooltip
              content="本期内 calc_status=exception 的运单占比"
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
  import { QuestionCircleOutlined } from '@/components/icons';
  import { useEcharts } from '@/utils/use-echarts';
  import { getOperationEfficiency } from '@/api/dashboard/cockpit';
  import type { OperationEfficiency } from '@/api/dashboard/cockpit/model';
  import { useCockpitFilter } from '../composables/use-cockpit-filter';

  use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent]);

  const { state } = useCockpitFilter();

  const loading = ref(false);
  const data = ref<OperationEfficiency | null>(null);
  const statusChartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([statusChartRef]);

  const statusOption: EChartsCoreOption = reactive({});

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
      data.value = await getOperationEfficiency({
        start: state.start,
        end: state.end
      });
      renderChart();
    } catch (e: any) {
      EleMessage.error({ message: e?.message || '加载运营效率失败', plain: true });
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
  .eff-card {
    margin-bottom: 16px;
  }

  .empty-state {
    height: 320px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
  }

  .eff-section-title {
    padding: 0 0 4px 0;
    color: var(--el-text-color-regular);
  }

  .eff-metrics {
    padding: 4px 4px 0 4px;
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
