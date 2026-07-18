<!-- 利润总览 - 客户毛利排行 -->
<template>
  <ele-card
    class="rank-card"
    :header-style="{ paddingTop: 0, paddingBottom: 0 }"
  >
    <template #header>
      <div class="rank-card-title">客户毛利排行</div>
    </template>
    <template #extra>
      <el-radio-group v-model="sortBy" size="default" @change="load">
        <el-radio-button value="profit">按毛利</el-radio-button>
        <el-radio-button value="revenue">按收入</el-radio-button>
        <el-radio-button value="margin">按毛利率</el-radio-button>
      </el-radio-group>
    </template>
    <el-table
      :data="rows"
      v-loading="loading"
      size="default"
      stripe
      :max-height="440"
    >
      <el-table-column type="index" label="#" width="56" align="center" />
      <el-table-column prop="customerName" label="客户" min-width="160">
        <template #default="{ row }">
          <ele-ellipsis>{{ row.customerName }}</ele-ellipsis>
        </template>
      </el-table-column>
      <el-table-column label="收入" min-width="120" align="right">
        <template #default="{ row }">¥{{ formatAmount(row.revenue) }}</template>
      </el-table-column>
      <el-table-column label="成本" min-width="120" align="right">
        <template #default="{ row }">¥{{ formatAmount(row.cost) }}</template>
      </el-table-column>
      <el-table-column label="毛利" min-width="120" align="right">
        <template #default="{ row }">
          <span :class="row.grossProfit >= 0 ? 'val-pos' : 'val-neg'">
            ¥{{ formatAmount(row.grossProfit) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="毛利率" min-width="100" align="right">
        <template #default="{ row }">
          <el-tag
            v-if="row.grossMargin !== null"
            :type="row.grossMargin >= 0 ? 'success' : 'danger'"
            effect="light"
            size="small"
          >
            {{ (row.grossMargin * 100).toFixed(1) }}%
          </el-tag>
          <span v-else class="val-muted">—</span>
        </template>
      </el-table-column>
      <el-table-column
        prop="waybillCount"
        label="计划"
        width="90"
        align="right"
      />
      <el-table-column
        prop="vehicleQuantity"
        label="台数"
        width="90"
        align="right"
      />
      <template #empty>
        <span class="rank-empty">暂无客户毛利数据</span>
      </template>
    </el-table>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { getProfitCustomerRank } from '@/api/dashboard/profit';
  import type { ProfitCustomerRankItem } from '@/api/dashboard/profit/model';
  import { useProfitFilter } from '../composables/use-profit-filter';

  const { state } = useProfitFilter();

  const RANK_LIMIT = 20;

  const loading = ref(false);
  const sortBy = ref<'profit' | 'revenue' | 'margin'>('profit');
  const rows = ref<ProfitCustomerRankItem[]>([]);

  const formatAmount = (n: number) => {
    if (!Number.isFinite(n)) return '0';
    return Math.round(n).toLocaleString('zh-CN');
  };

  const load = async () => {
    loading.value = true;
    try {
      rows.value = await getProfitCustomerRank({
        start: state.start,
        end: state.end,
        limit: RANK_LIMIT,
        sort_by: sortBy.value
      });
    } catch (e: unknown) {
      const err = e as { message?: string };
      EleMessage.error({
        message: err?.message || '加载客户毛利排行失败',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  watch(() => [state.start, state.end], load);
  void load();
</script>

<style lang="scss" scoped>
  .rank-card {
    margin-bottom: 16px;

    :deep(.ele-card-header) {
      min-height: 52px;
    }
  }

  .rank-card-title {
    font-size: 16px;
    font-weight: 600;
  }

  .val-pos {
    color: var(--el-color-danger);
    font-variant-numeric: tabular-nums;
  }

  .val-neg {
    color: var(--el-color-success);
    font-variant-numeric: tabular-nums;
  }

  .val-muted {
    color: var(--el-text-color-placeholder);
  }

  .rank-empty {
    color: var(--el-text-color-placeholder);
    font-size: 13px;
  }
</style>
