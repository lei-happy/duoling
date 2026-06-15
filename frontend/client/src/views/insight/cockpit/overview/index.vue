<!--
  经营驾驶舱 - 经营总览页面

  挂载路径：/insight/cockpit/overview
  菜单：数据洞察 > 经营驾驶舱 > 经营总览

  布局顺序：
    1. 4 KPI 卡：当日自然日大数 + 近 30 日迷你图 + 周同比 / 日同比
    2. 运单运费/单量趋势 + 客户排行（卡片内自选日期范围，柱图按日联动排行）
    3. 客户类型分布 (16) + 运单状态分布 (8)
    4. 起讫点 Top10（双柱状）
    5. 商品车品牌排行（柱状 + 词云）
-->
<template>
  <ele-page>
    <kpi-card />
    <trend-card />
    <el-row :gutter="16" align="stretch" class="cockpit-customer-eff-row">
      <el-col :md="16" :sm="14" :xs="24" class="cockpit-row-col">
        <customer-analysis />
      </el-col>
      <el-col :md="8" :sm="10" :xs="24" class="cockpit-row-col">
        <efficiency-card />
      </el-col>
    </el-row>
    <!-- <route-analysis /> -->
    <vehicle-brand-analysis />
  </ele-page>
</template>

<script lang="ts" setup>
  import KpiCard from './components/kpi-card.vue';
  import TrendCard from './components/trend-card.vue';
  import CustomerAnalysis from './components/customer-analysis.vue';
  import RouteAnalysis from './components/route-analysis.vue';
  import VehicleBrandAnalysis from './components/vehicle-brand-analysis.vue';
  import EfficiencyCard from './components/efficiency-card.vue';
  import { provideCockpitFilter } from './composables/use-cockpit-filter';

  defineOptions({ name: 'BusinessCockpitOverview' });

  provideCockpitFilter();
</script>

<style lang="scss" scoped>
  .cockpit-row-col {
    display: flex;
    flex-direction: column;
  }

  .cockpit-row-col > :deep(*) {
    flex: 1;
    width: 100%;
    min-height: 0;
  }
</style>
