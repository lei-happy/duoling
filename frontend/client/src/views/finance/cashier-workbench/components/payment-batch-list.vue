<!-- 打款批次列表：提交、审批、执行打款都从这里进详情做 -->
<template>
  <div>
    <div class="panel-toolbar">
      <el-input
        v-model="where.keyword"
        placeholder="批次号"
        clearable
        style="width: 180px"
        @change="load"
      />
      <el-select
        v-model="where.status"
        placeholder="状态"
        clearable
        style="width: 130px"
        @change="load"
      >
        <el-option
          v-for="o in PAYMENT_BATCH_STATUS_OPTIONS"
          :key="o.value"
          :value="o.value"
          :label="o.label"
        />
      </el-select>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        value-format="YYYY-MM-DD"
        start-placeholder="创建起"
        end-placeholder="创建止"
        style="width: 230px"
        @change="onDateChange"
      />
      <el-button @click="load">刷新</el-button>
    </div>

    <el-table :data="rows" v-loading="loading" size="small" max-height="460">
      <el-table-column label="批次号" min-width="180">
        <template #default="{ row }">
          <el-link
            type="primary"
            :underline="false"
            @click="openDetail(row.id)"
          >
            {{ row.docNo }}
          </el-link>
          <div class="muted">{{ formatDateTime(row.createdAt) }}</div>
        </template>
      </el-table-column>
      <el-table-column label="付款账户" min-width="170">
        <template #default="{ row }">
          <div>{{ row.bankAccountLabel || '--' }}</div>
          <div class="muted">{{ row.payMethodLabel || '' }}</div>
        </template>
      </el-table-column>
      <el-table-column label="笔数" width="120" align="center">
        <template #default="{ row }">
          {{ row.itemCount }} 笔
          <div v-if="row.failCount" class="fail-text">
            失败 {{ row.failCount }}
          </div>
        </template>
      </el-table-column>
      <el-table-column label="批次金额" width="140" align="right">
        <template #default="{ row }">
          <span class="num strong">¥ {{ formatMoney(row.totalAmount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="已付" width="140" align="right">
        <template #default="{ row }">
          <span class="num paid">¥ {{ formatMoney(row.paidAmount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="计划付款日" width="120" align="center">
        <template #default="{ row }">{{ row.planPayDate || '--' }}</template>
      </el-table-column>
      <el-table-column label="状态" width="110" align="center">
        <template #default="{ row }">
          <el-tag
            :type="
              (PAYMENT_BATCH_STATUS_MAP[row.status]?.type as any) || 'info'
            "
            size="small"
          >
            {{ row.statusLabel }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="90" align="center">
        <template #default="{ row }">
          <el-link
            type="primary"
            :underline="false"
            @click="openDetail(row.id)"
          >
            处理
          </el-link>
        </template>
      </el-table-column>
      <template #empty>
        <div class="empty-tip">还没有打款批次，去「待打款」勾单合成一个</div>
      </template>
    </el-table>

    <div class="panel-pager">
      <el-pagination
        v-model:current-page="where.page"
        v-model:page-size="where.limit"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="load"
      />
    </div>

    <payment-batch-detail
      v-model:visible="detailVisible"
      :batch-id="detailId"
      @changed="onChanged"
    />
  </div>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import PaymentBatchDetail from './payment-batch-detail.vue';
  import { pagePaymentBatches } from '@/api/finance/payment-batch';
  import type {
    PaymentBatchListItem,
    PaymentBatchParam
  } from '@/api/finance/payment-batch/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    formatMoney,
    PAYMENT_BATCH_STATUS_MAP,
    PAYMENT_BATCH_STATUS_OPTIONS
  } from '../../status-config';

  const emit = defineEmits<{ (e: 'done'): void }>();

  const loading = ref(false);
  const rows = ref<PaymentBatchListItem[]>([]);
  const total = ref(0);
  const dateRange = ref<[string, string] | null>(null);
  const where = reactive<PaymentBatchParam>({ page: 1, limit: 20 });

  const detailVisible = ref(false);
  const detailId = ref<number | null>(null);

  const load = async () => {
    loading.value = true;
    try {
      const res = await pagePaymentBatches({ ...where });
      rows.value = res?.list ?? [];
      total.value = res?.count ?? 0;
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '加载失败，请重试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  const onDateChange = () => {
    where.dateFrom = dateRange.value?.[0];
    where.dateTo = dateRange.value?.[1];
    where.page = 1;
    load();
  };

  const openDetail = (batchId: number) => {
    detailId.value = batchId;
    detailVisible.value = true;
  };

  const onChanged = () => {
    load();
    emit('done');
  };

  onMounted(load);
</script>

<style lang="scss" scoped>
  .panel-toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }

  .panel-pager {
    display: flex;
    justify-content: flex-end;
    margin-top: 10px;
  }

  .num {
    font-variant-numeric: tabular-nums;
  }

  .strong {
    font-weight: 600;
  }

  .paid {
    color: var(--el-color-success);
  }

  .muted {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .fail-text {
    color: var(--el-color-danger);
    font-size: 12px;
  }

  .empty-tip {
    padding: 28px 0;
    color: var(--el-text-color-secondary);
    text-align: center;
  }
</style>
