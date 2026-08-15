<template>
  <ele-page>
    <el-alert
      type="info"
      :closable="false"
      class="analysis-alert"
      :title="
        overview.note ||
        '油补是付给司机的补贴，能源消费是付给供应商的能源费，两笔钱不重复。'
      "
    />
    <el-row :gutter="16">
      <el-col :lg="6" :md="12" :sm="12" :xs="24">
        <ele-card>
          <div class="energy-kpi">
            <div class="energy-kpi__label">账面余额</div>
            <div class="energy-kpi__value">
              {{ formatMoney(overview.ledgerBalance) }}
            </div>
          </div>
        </ele-card>
      </el-col>
      <el-col :lg="6" :md="12" :sm="12" :xs="24">
        <ele-card>
          <div class="energy-kpi">
            <div class="energy-kpi__label">本月消费</div>
            <div class="energy-kpi__value">
              {{ formatMoney(overview.monthConsumption) }}
            </div>
          </div>
        </ele-card>
      </el-col>
      <el-col :lg="6" :md="12" :sm="12" :xs="24">
        <ele-card>
          <div class="energy-kpi">
            <div class="energy-kpi__label">本月充值</div>
            <div class="energy-kpi__value">
              {{ formatMoney(overview.monthRecharge) }}
            </div>
          </div>
        </ele-card>
      </el-col>
      <el-col :lg="6" :md="12" :sm="12" :xs="24">
        <ele-card>
          <div class="energy-kpi">
            <div class="energy-kpi__label">预计可用天数</div>
            <div class="energy-kpi__value">{{ overview.usableDays ?? '-' }}</div>
          </div>
        </ele-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="analysis-charts">
      <el-col :lg="12" :md="24" :sm="24" :xs="24">
        <ele-card>
          <div class="card-title">单车能源成本（近 30 天）</div>
          <div class="chart-body">
            <v-chart
              ref="vehicleChartRef"
              :option="vehicleChartOption"
              class="chart-inner"
              autoresize
            />
          </div>
        </ele-card>
      </el-col>
      <el-col :lg="12" :md="24" :sm="24" :xs="24">
        <ele-card>
          <div class="card-title">供应商消费对比</div>
          <div class="chart-body">
            <v-chart
              ref="supplierChartRef"
              :option="supplierChartOption"
              class="chart-inner"
              autoresize
            />
          </div>
        </ele-card>
      </el-col>
    </el-row>

    <ele-card class="analysis-table" :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        row-key="vehicleId"
        :columns="vehicleColumns"
        :datasource="vehicles"
        :pagination="false"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="EnergyAnalysisVehicleTable"
      >
        <template #toolbar>
          <span class="table-title">单车明细</span>
        </template>
      </ele-pro-table>
    </ele-card>
    <ele-card class="analysis-table" :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        row-key="supplierId"
        :columns="supplierColumns"
        :datasource="suppliers"
        :pagination="false"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="EnergyAnalysisSupplierTable"
      >
        <template #toolbar>
          <span class="table-title">供应商对比</span>
        </template>
        <template #idleHint="{ row }">
          <el-tag v-if="row.idleHint" type="warning" size="small">
            资金沉淀偏高
          </el-tag>
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { Columns } from 'ele-admin-plus/es/ele-pro-table/types';
  import { use } from 'echarts/core';
  import type { EChartsCoreOption } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { BarChart } from 'echarts/charts';
  import { GridComponent, TooltipComponent } from 'echarts/components';
  import VChart from 'vue-echarts';
  import { useEcharts } from '@/utils/use-echarts';
  import {
    analysisOverview,
    analysisSupplier,
    analysisVehicleCost
  } from '@/api/energy';
  import { formatMoney } from '../_shared/options';

  defineOptions({ name: 'EnergyAnalysis' });

  use([CanvasRenderer, BarChart, GridComponent, TooltipComponent]);

  const vehicleChartRef = ref<InstanceType<typeof VChart> | null>(null);
  const supplierChartRef = ref<InstanceType<typeof VChart> | null>(null);
  useEcharts([vehicleChartRef, supplierChartRef]);

  const overview = ref<any>({});
  const vehicles = ref<any[]>([]);
  const suppliers = ref<any[]>([]);
  const vehicleChartOption: EChartsCoreOption = reactive({});
  const supplierChartOption: EChartsCoreOption = reactive({});

  const vehicleColumns = ref<Columns>([
    { prop: 'vehicleId', label: '车辆ID', width: 100 },
    {
      prop: 'amount',
      label: '金额',
      width: 120,
      align: 'right',
      formatter: (row) => formatMoney(row.amount)
    },
    { prop: 'quantity', label: '数量', width: 100, align: 'right' },
    { prop: 'mileage', label: '里程', width: 100, align: 'right' },
    {
      prop: 'costPer100km',
      label: '百公里成本',
      width: 120,
      align: 'right',
      formatter: (row) => formatMoney(row.costPer100km)
    }
  ]);

  const supplierColumns = ref<Columns>([
    { prop: 'supplierName', label: '供应商', minWidth: 160 },
    {
      prop: 'amount',
      label: '消费金额',
      width: 120,
      align: 'right',
      formatter: (row) => formatMoney(row.amount)
    },
    {
      prop: 'avgPrice',
      label: '均价',
      width: 100,
      align: 'right',
      formatter: (row) => formatMoney(row.avgPrice)
    },
    {
      prop: 'ledgerBalance',
      label: '账户余额',
      width: 120,
      align: 'right',
      formatter: (row) => formatMoney(row.ledgerBalance)
    },
    { prop: 'usableDays', label: '可用天数', width: 100, align: 'center' },
    { prop: 'idleHint', label: '提示', minWidth: 140, slot: 'idleHint' }
  ]);

  const fillCharts = () => {
    Object.assign(vehicleChartOption, {
      tooltip: { trigger: 'axis' },
      grid: { left: 48, right: 16, top: 24, bottom: 40 },
      xAxis: {
        type: 'category',
        data: vehicles.value.map((v) => `车辆 ${v.vehicleId}`)
      },
      yAxis: { type: 'value', name: '金额' },
      series: [
        {
          type: 'bar',
          name: '能源成本',
          data: vehicles.value.map((v) => Number(v.amount || 0)),
          itemStyle: { color: '#2f8f7d' }
        }
      ]
    });
    Object.assign(supplierChartOption, {
      tooltip: { trigger: 'axis' },
      grid: { left: 48, right: 16, top: 24, bottom: 40 },
      xAxis: {
        type: 'category',
        data: suppliers.value.map(
          (s) => s.supplierName || `供应商 ${s.supplierId}`
        )
      },
      yAxis: { type: 'value', name: '金额' },
      series: [
        {
          type: 'bar',
          name: '消费金额',
          data: suppliers.value.map((s) => Number(s.amount || 0)),
          itemStyle: { color: '#5bb8a8' }
        }
      ]
    });
  };

  onMounted(async () => {
    try {
      overview.value = await analysisOverview();
      vehicles.value = (await analysisVehicleCost({})) || [];
      suppliers.value = (await analysisSupplier({})) || [];
      fillCharts();
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '加载分析数据失败，请稍后重试',
        plain: true
      });
    }
  });
</script>

<style scoped>
  .analysis-alert {
    margin-bottom: 12px;
  }

  .energy-kpi {
    min-height: 72px;
  }

  .energy-kpi__label {
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .energy-kpi__value {
    margin-top: 8px;
    font-size: 22px;
    font-weight: 600;
    line-height: 1.2;
    color: var(--el-text-color-primary);
  }

  .analysis-charts {
    margin-top: 16px;
  }

  .card-title {
    font-weight: 600;
    margin-bottom: 12px;
  }

  .chart-body {
    height: 280px;
  }

  .chart-inner {
    width: 100%;
    height: 100%;
  }

  .analysis-table {
    margin-top: 16px;
  }

  .table-title {
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
</style>
