<!--
  经营驾驶舱 - 经营总览页面

  挂载路径：/insight/cockpit/overview
  菜单：数据洞察 > 经营驾驶舱 > 经营总览

  布局顺序：
    1. 顶部时间筛选条
    2. 4 KPI 卡（运费 / 单量 / 台数 / 客户数）
    3. 收入与单量趋势 + Top10 客户排行
    4. 客户类型分布 (16) + 运营效率 (8)
    5. 起讫点 Top10（双柱状）
    6. 商品车品牌排行（柱状 + 词云）
-->
<template>
  <ele-page>
    <filter-bar />
    <kpi-card />
    <trend-card />
    <el-row :gutter="16">
      <el-col :md="16" :sm="14" :xs="24">
        <customer-analysis />
      </el-col>
      <el-col :md="8" :sm="10" :xs="24">
        <efficiency-card />
      </el-col>
    </el-row>
    <route-analysis />
    <vehicle-brand-analysis />
  </ele-page>
</template>

<script lang="ts" setup>
  import FilterBar from './components/filter-bar.vue';
  import KpiCard from './components/kpi-card.vue';
  import TrendCard from './components/trend-card.vue';
  import CustomerAnalysis from './components/customer-analysis.vue';
  import RouteAnalysis from './components/route-analysis.vue';
  import VehicleBrandAnalysis from './components/vehicle-brand-analysis.vue';
  import EfficiencyCard from './components/efficiency-card.vue';
  import { provideCockpitFilter } from './composables/use-cockpit-filter';

  defineOptions({ name: 'BusinessCockpitOverview' });

  // 顶层提供全局时间筛选状态（默认本月）
  provideCockpitFilter('3');
</script>
