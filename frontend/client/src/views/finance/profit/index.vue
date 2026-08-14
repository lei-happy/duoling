<!--
  经营核算（文档 13）

  口径与经营驾驶舱的利润看板**不同**：这里只认已对账确认的收入与已审批的成本，按财务
  期间归期；驾驶舱用计费引擎理论值、按运单创建时间归期。两边数字对不平是正常的，
  页面顶部常驻说明，不要试图让它们一致。
-->
<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '12px' }">
      <div class="page-toolbar">
        <el-radio-group v-model="periodType" @change="onPeriodTypeChange">
          <el-radio-button value="month">月</el-radio-button>
          <el-radio-button value="quarter">季</el-radio-button>
          <el-radio-button value="year">年</el-radio-button>
        </el-radio-group>
        <el-date-picker
          v-if="periodType === 'month'"
          v-model="monthValue"
          type="month"
          value-format="YYYY-MM"
          placeholder="选月份"
          :clearable="false"
          style="width: 150px"
          @change="loadAll"
        />
        <template v-else-if="periodType === 'quarter'">
          <el-date-picker
            v-model="yearValue"
            type="year"
            value-format="YYYY"
            :clearable="false"
            style="width: 110px"
            @change="loadAll"
          />
          <el-select v-model="quarter" style="width: 100px" @change="loadAll">
            <el-option v-for="q in 4" :key="q" :value="q" :label="`Q${q}`" />
          </el-select>
        </template>
        <el-date-picker
          v-else
          v-model="yearValue"
          type="year"
          value-format="YYYY"
          :clearable="false"
          style="width: 110px"
          @change="loadAll"
        />

        <business-entity-select
          v-model="enterpriseId"
          placeholder="全部经营主体"
          style="width: 200px"
          @change="loadAll"
        />

        <el-radio-group v-model="taxMode" @change="loadAll">
          <el-radio-button value="excl">不含税</el-radio-button>
          <el-radio-button value="incl">含税</el-radio-button>
        </el-radio-group>

        <div class="toolbar-right">
          <el-button
            type="primary"
            plain
            :loading="exporting"
            v-permission="'finance:profit:export'"
            @click="doExport"
          >
            导出底稿
          </el-button>
        </div>
      </div>

      <el-alert type="info" :closable="false" class="tip-alert" show-icon>
        <template #title>
          财务确认口径：收入取已确认对账单与已结算金额，成本取已审批的承运商结算单、
          司机工资单与任务费用单，按财务期间归期。与「经营驾驶舱」的理论毛利口径不同，
          两边数字不需要对平。
        </template>
      </el-alert>

      <finance-kpi-cards :cards="kpiCards" />

      <div v-if="kpi && kpi.unallocatedCost > 0" class="warn-line">
        本期有 ¥
        {{ formatMoney(kpi.unallocatedCost) }} 成本没能摊到运单（多为整单费用或
        运单已删），维度表里单独列为「未分摊」。
      </div>
      <div v-if="kpi && kpi.noInvoiceCost > 0" class="warn-line">
        有 ¥
        {{ formatMoney(kpi.noInvoiceCost) }} 成本还没收到票，按不含税口径会少抵
        ¥ {{ formatMoney(kpi.missingInvoiceTaxLoss) }} 税额，建议先催票。
      </div>

      <el-tabs v-model="dimension" class="page-tabs" @tab-change="loadRows">
        <el-tab-pane
          v-for="d in ACCOUNTING_DIMENSION_OPTIONS"
          :key="d.value"
          :label="d.label"
          :name="d.value"
        />
      </el-tabs>

      <el-table
        :data="rows"
        v-loading="loadingRows"
        size="small"
        max-height="460"
        :default-sort="{ prop: 'grossProfit', order: 'descending' }"
      >
        <el-table-column label="维度值" min-width="180">
          <template #default="{ row }">
            {{ row.dimensionLabel || row.dimensionValue }}
          </template>
        </el-table-column>
        <el-table-column
          prop="revenue"
          label="确认收入"
          width="140"
          align="right"
          sortable
        >
          <template #default="{ row }">
            <span class="num">¥ {{ formatMoney(displayRevenue(row)) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="cost"
          label="成本"
          width="140"
          align="right"
          sortable
        >
          <template #default="{ row }">
            <span class="num">¥ {{ formatMoney(displayCost(row)) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="grossProfit"
          label="毛利"
          width="140"
          align="right"
          sortable
        >
          <template #default="{ row }">
            <span
              class="num strong"
              :class="row.grossProfit >= 0 ? 'pos' : 'neg'"
            >
              ¥ {{ formatMoney(row.grossProfit) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          prop="grossMarginRate"
          label="毛利率"
          width="110"
          align="right"
          sortable
        >
          <template #default="{ row }">
            {{
              row.grossMarginRate == null
                ? '--'
                : `${(row.grossMarginRate * 100).toFixed(1)}%`
            }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" align="center">
          <template #default="{ row }">
            <el-link
              type="primary"
              :underline="false"
              v-permission="'finance:profit:drill-down'"
              @click="openDrill(row)"
            >
              下钻
            </el-link>
          </template>
        </el-table-column>
        <template #empty>
          <div class="empty-tip">
            本期这个维度还没有已确认的收入或已审批的成本
          </div>
        </template>
      </el-table>
    </ele-card>

    <!-- 下钻明细 -->
    <el-drawer
      v-model="drillVisible"
      :size="880"
      :title="`${drill?.dimensionLabel || drill?.dimensionValue || ''} · ${
        drill?.periodLabel || ''
      }`"
      destroy-on-close
    >
      <div v-loading="drillLoading">
        <template v-if="drill">
          <div class="drill-sum">
            收入 ¥ {{ formatMoney(drill.revenueTotal) }} · 成本 ¥
            {{ formatMoney(drill.costTotal) }} · 毛利 ¥
            {{ formatMoney(drill.revenueTotal - drill.costTotal) }}
          </div>
          <el-tabs v-model="drillTab">
            <el-tab-pane
              :label="`收入单据（${drill.revenueDocs.length}）`"
              name="revenue"
            >
              <el-table :data="drill.revenueDocs" size="small" max-height="420">
                <el-table-column prop="docNo" label="单号" min-width="170" />
                <el-table-column
                  prop="docKindLabel"
                  label="单据类型"
                  width="130"
                />
                <el-table-column
                  prop="counterparty"
                  label="客户"
                  min-width="140"
                />
                <el-table-column label="计入金额" width="130" align="right">
                  <template #default="{ row }">
                    <span class="num">¥ {{ formatMoney(row.amount) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="归期" width="120" align="center">
                  <template #default="{ row }">
                    {{ (row.periodEnd || '').slice(0, 10) || '--' }}
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            <el-tab-pane
              :label="`成本单据（${drill.costDocs.length}）`"
              name="cost"
            >
              <el-table :data="drill.costDocs" size="small" max-height="420">
                <el-table-column prop="docNo" label="单号" min-width="170" />
                <el-table-column
                  prop="docKindLabel"
                  label="单据类型"
                  width="130"
                />
                <el-table-column
                  prop="counterparty"
                  label="对方"
                  min-width="140"
                />
                <el-table-column label="计入金额" width="130" align="right">
                  <template #default="{ row }">
                    <span class="num">¥ {{ formatMoney(row.amount) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="单据总额" width="130" align="right">
                  <template #default="{ row }">
                    <span class="num muted-num">
                      {{
                        row.docAmount == null
                          ? '--'
                          : formatMoney(row.docAmount)
                      }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column label="归期" width="120" align="center">
                  <template #default="{ row }">
                    {{ (row.periodEnd || '').slice(0, 10) || '--' }}
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </template>
      </div>
    </el-drawer>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import BusinessEntitySelect from '@/components/BusinessEntitySelect/index.vue';
  import FinanceKpiCards from '../components/finance-kpi-cards.vue';
  import type { FinanceKpiCard } from '../components/finance-kpi-cards.vue';
  import {
    drillDownAccounting,
    exportAccountingWorksheet,
    getAccountingKpi,
    listAccountingByDimension
  } from '@/api/finance/profit';
  import type {
    AccountingKpi,
    DimensionRow,
    DrillDownResult
  } from '@/api/finance/profit/model';
  import { ACCOUNTING_DIMENSION_OPTIONS, formatMoney } from '../status-config';

  defineOptions({ name: 'FinanceProfit' });

  const now = new Date();
  const periodType = ref<'month' | 'quarter' | 'year'>('month');
  const monthValue = ref(
    `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  );
  const yearValue = ref(String(now.getFullYear()));
  const quarter = ref(Math.floor(now.getMonth() / 3) + 1);
  const enterpriseId = ref<number | undefined>();
  const taxMode = ref<'excl' | 'incl'>('excl');

  const kpi = ref<AccountingKpi | null>(null);
  const rows = ref<DimensionRow[]>([]);
  const dimension = ref('customer');
  const loadingRows = ref(false);
  const exporting = ref(false);

  const drillVisible = ref(false);
  const drillLoading = ref(false);
  const drillTab = ref('revenue');
  const drill = ref<DrillDownResult | null>(null);

  const period = computed(() => {
    if (periodType.value === 'month') return monthValue.value;
    if (periodType.value === 'quarter')
      return `${yearValue.value}-Q${quarter.value}`;
    return yearValue.value;
  });

  const isExcl = computed(() => taxMode.value === 'excl');

  const displayRevenue = (row: DimensionRow) =>
    isExcl.value ? row.revenueExclTax : row.revenue;

  const displayCost = (row: DimensionRow) =>
    isExcl.value ? row.costExclTax : row.cost;

  const kpiCards = computed<FinanceKpiCard[]>(() => {
    const k = kpi.value;
    if (!k) return [];
    const revenue = isExcl.value ? k.revenueExclTax : k.confirmedRevenue;
    const cost = isExcl.value ? k.costExclTax : k.costInclTax;
    const profit = isExcl.value ? k.grossProfitExclTax : k.grossProfitInclTax;
    return [
      {
        key: 'revenue',
        label: isExcl.value ? '确认收入（不含税）' : '确认收入（含税）',
        value: formatMoney(revenue),
        unit: '元',
        type: 'primary',
        hint: `${k.revenueDocCount} 张单据 · ${k.periodLabel}`
      },
      {
        key: 'realized',
        label: '其中已收妥',
        value: formatMoney(k.realizedRevenue),
        unit: '元',
        type: 'success',
        hint: '已收款的结算单金额'
      },
      {
        key: 'cost',
        label: isExcl.value ? '成本（不含税）' : '成本（含税）',
        value: formatMoney(cost),
        unit: '元',
        type: 'warning',
        hint: `${k.costDocCount} 张单据`
      },
      {
        key: 'profit',
        label: '毛利',
        value: formatMoney(profit),
        unit: '元',
        type: profit >= 0 ? 'success' : 'danger',
        hint:
          k.grossMarginRate == null
            ? undefined
            : `毛利率 ${(k.grossMarginRate * 100).toFixed(1)}%`
      },
      {
        key: 'tax',
        label: '销项税率',
        value: `${k.outputTaxRate}%`,
        type: 'info',
        hint: '默认税率来自系统参数，实际按本期已开票加权'
      }
    ];
  });

  const onPeriodTypeChange = () => loadAll();

  const loadKpi = async () => {
    try {
      kpi.value =
        (await getAccountingKpi({
          period: period.value,
          enterpriseId: enterpriseId.value,
          taxMode: taxMode.value
        })) ?? null;
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '指标加载失败，请重试',
        plain: true
      });
    }
  };

  const loadRows = async () => {
    loadingRows.value = true;
    try {
      const res = await listAccountingByDimension({
        dimension: dimension.value,
        period: period.value,
        enterpriseId: enterpriseId.value,
        taxMode: taxMode.value
      });
      rows.value = res?.list ?? [];
    } catch (e: unknown) {
      EleMessage.error({
        message:
          (e as { message?: string }).message || '维度数据加载失败，请重试',
        plain: true
      });
    } finally {
      loadingRows.value = false;
    }
  };

  const loadAll = async () => {
    await Promise.all([loadKpi(), loadRows()]);
  };

  const openDrill = async (row: DimensionRow) => {
    drillVisible.value = true;
    drillLoading.value = true;
    drillTab.value = 'revenue';
    drill.value = null;
    try {
      drill.value =
        (await drillDownAccounting({
          dimension: dimension.value,
          dimensionValue: row.dimensionValue,
          period: period.value,
          enterpriseId: enterpriseId.value
        })) ?? null;
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '下钻失败，请重试',
        plain: true
      });
    } finally {
      drillLoading.value = false;
    }
  };

  const doExport = async () => {
    exporting.value = true;
    try {
      await exportAccountingWorksheet({
        period: period.value,
        enterpriseId: enterpriseId.value
      });
      EleMessage.success({ message: '底稿已导出', plain: true });
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '导出失败，请稍后重试',
        plain: true
      });
    } finally {
      exporting.value = false;
    }
  };

  onMounted(loadAll);
</script>

<style lang="scss" scoped>
  .page-toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
  }

  .toolbar-right {
    margin-left: auto;
  }

  .tip-alert {
    margin-bottom: 12px;
  }

  .warn-line {
    margin-bottom: 8px;
    color: var(--el-color-warning);
    font-size: 13px;
  }

  .page-tabs {
    margin-top: 4px;

    :deep(.el-tabs__header) {
      margin-bottom: 8px;
    }
  }

  .num {
    font-variant-numeric: tabular-nums;
  }

  .strong {
    font-weight: 600;
  }

  .pos {
    color: var(--el-color-success);
  }

  .neg {
    color: var(--el-color-danger);
  }

  .muted-num {
    color: var(--el-text-color-secondary);
  }

  .empty-tip {
    padding: 28px 0;
    color: var(--el-text-color-secondary);
    text-align: center;
  }

  .drill-sum {
    margin-bottom: 10px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }
</style>
