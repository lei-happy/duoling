<template>
  <ele-page>
    <el-alert
      type="info"
      :closable="false"
      :title="
        overview.note ||
        '油补是付给司机的补贴，能源消费是付给供应商的能源费，两笔钱不重复。'
      "
      style="margin-bottom: 12px"
    />
    <el-row :gutter="16">
      <el-col :span="6">
        <ele-card>
          <div class="kpi">
            账面余额<br /><b>{{ overview.ledgerBalance ?? 0 }}</b>
          </div>
        </ele-card>
      </el-col>
      <el-col :span="6">
        <ele-card>
          <div class="kpi">
            本月消费<br /><b>{{ overview.monthConsumption ?? 0 }}</b>
          </div>
        </ele-card>
      </el-col>
      <el-col :span="6">
        <ele-card>
          <div class="kpi">
            本月充值<br /><b>{{ overview.monthRecharge ?? 0 }}</b>
          </div>
        </ele-card>
      </el-col>
      <el-col :span="6">
        <ele-card>
          <div class="kpi">
            预计可用天数<br /><b>{{ overview.usableDays ?? '-' }}</b>
          </div>
        </ele-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
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
      <el-col :span="12">
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

    <ele-card style="margin-top: 16px">
      <div class="card-title">单车明细</div>
      <el-table :data="vehicles" border>
        <el-table-column prop="vehicleId" label="车辆ID" width="100" />
        <el-table-column prop="amount" label="金额" width="120" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="mileage" label="里程" width="100" />
        <el-table-column prop="costPer100km" label="百公里成本" width="120" />
      </el-table>
    </ele-card>
    <ele-card style="margin-top: 16px">
      <div class="card-title">供应商对比</div>
      <el-table :data="suppliers" border>
        <el-table-column prop="supplierName" label="供应商" min-width="140" />
        <el-table-column prop="amount" label="消费金额" width="120" />
        <el-table-column prop="avgPrice" label="均价" width="100" />
        <el-table-column prop="ledgerBalance" label="账户余额" width="120" />
        <el-table-column prop="usableDays" label="可用天数" width="100" />
        <el-table-column label="提示" min-width="140">
          <template #default="{ row }">
            <el-tag v-if="row.idleHint" type="warning">资金沉淀偏高</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
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
        data: suppliers.value.map((s) => s.supplierName || `供应商 ${s.supplierId}`)
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
      EleMessage.error({ message: e.message || '加载分析数据失败，请重试', plain: true });
    }
  });
</script>
<style scoped>
  .kpi {
    line-height: 1.6;
  }
  .kpi b {
    font-size: 22px;
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
</style>
