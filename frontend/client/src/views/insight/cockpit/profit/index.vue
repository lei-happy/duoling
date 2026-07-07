<!--
  经营驾驶舱 - 利润总览页面（老板视角收入成本 BI）

  挂载路径：/insight/cockpit/profit
  菜单：数据洞察 > 经营驾驶舱 > 利润总览

  布局顺序：
    1. 4 KPI 卡：收入 / 成本 / 毛利 / 毛利率（当日大数 + 近 30 日迷你图 + 日/周同比）
    2. 收入 / 成本 / 毛利 组合趋势（柱 + 线双轴，支持 日/周/月）
    3. 承运结构（自有/承运商/社会运力，左）+ 成本构成（按费用类型，右）
    4. 客户毛利 TopN 排行
-->
<template>
  <ele-page>
    <profit-kpi-card />
    <profit-trend-card />
    <el-row :gutter="16" align="stretch" class="profit-mid-row">
      <el-col :md="12" :sm="24" :xs="24" class="profit-row-col">
        <carrier-structure-card />
      </el-col>
      <el-col :md="12" :sm="24" :xs="24" class="profit-row-col">
        <cost-structure-card />
      </el-col>
    </el-row>
    <profit-rank-card />
  </ele-page>
</template>

<script lang="ts" setup>
  import ProfitKpiCard from './components/profit-kpi-card.vue';
  import ProfitTrendCard from './components/profit-trend-card.vue';
  import CarrierStructureCard from './components/carrier-structure-card.vue';
  import CostStructureCard from './components/cost-structure-card.vue';
  import ProfitRankCard from './components/profit-rank-card.vue';
  import { provideProfitFilter } from './composables/use-profit-filter';

  defineOptions({ name: 'BusinessCockpitProfit' });

  provideProfitFilter();
</script>

<style lang="scss" scoped>
  .profit-mid-row {
    margin-bottom: 0;
  }

  .profit-row-col {
    display: flex;
    flex-direction: column;
  }

  .profit-row-col > :deep(*) {
    flex: 1;
    width: 100%;
    min-height: 0;
  }
</style>
