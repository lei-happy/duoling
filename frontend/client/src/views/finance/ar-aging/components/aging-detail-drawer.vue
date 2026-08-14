<template>
  <el-drawer
    :model-value="visible"
    :size="880"
    :title="brief ? `${brief.customerName || '客户'} · 应收明细` : '应收明细'"
    destroy-on-close
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="load"
  >
    <div v-loading="loading">
      <el-alert
        v-if="brief?.alertMessage"
        :type="alertType"
        :closable="false"
        show-icon
        :title="brief.alertMessage"
        class="alert"
      />

      <el-descriptions v-if="brief" :column="3" border size="small">
        <el-descriptions-item label="未收余额">
          <span class="num strong"
            >¥ {{ formatMoney(brief.unpaidAmount) }}</span
          >
        </el-descriptions-item>
        <el-descriptions-item label="其中逾期">
          <span class="num" :class="{ danger: brief.overdueAmount > 0 }">
            ¥ {{ formatMoney(brief.overdueAmount) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="最长逾期">
          {{
            brief.maxOverdueDays > 0 ? `${brief.maxOverdueDays} 天` : '无逾期'
          }}
        </el-descriptions-item>
        <el-descriptions-item label="信用额度">
          {{
            brief.creditLimit === null || brief.creditLimit === undefined
              ? '未设置'
              : `¥ ${formatMoney(brief.creditLimit)}`
          }}
        </el-descriptions-item>
        <el-descriptions-item label="信用状态">
          <el-tag
            :type="
              (CREDIT_STATUS_MAP[brief.creditStatus]?.type as any) || 'info'
            "
            size="small"
          >
            {{ brief.creditStatusLabel }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="额度占用">
          <span v-if="brief.exceeded" class="danger">
            已超 ¥ {{ formatMoney(brief.exceededAmount) }}
          </span>
          <span v-else class="muted">额度内</span>
        </el-descriptions-item>
      </el-descriptions>

      <div class="list-head">
        <span class="list-title">未收结算单</span>
        <span class="muted">
          统计基准日 {{ result?.baseDate || '今天' }}，按到期日从早到晚排列
        </span>
      </div>

      <el-table :data="result?.list || []" size="small" max-height="460">
        <el-table-column prop="docNo" label="结算单号" min-width="170" />
        <el-table-column label="结算周期" width="185" align="center">
          <template #default="{ row }">
            <template v-if="row.periodStart">
              {{ row.periodStart }} ~ {{ row.periodEnd }}
            </template>
            <span v-else class="muted">--</span>
          </template>
        </el-table-column>
        <el-table-column label="结算金额" width="120" align="right">
          <template #default="{ row }">
            <span class="num">¥ {{ formatMoney(row.plannedAmount) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="已收" width="120" align="right">
          <template #default="{ row }">
            <span class="num received"
              >¥ {{ formatMoney(row.receivedAmount) }}</span
            >
          </template>
        </el-table-column>
        <el-table-column label="未收" width="120" align="right">
          <template #default="{ row }">
            <span class="num strong"
              >¥ {{ formatMoney(row.unpaidAmount) }}</span
            >
          </template>
        </el-table-column>
        <el-table-column label="到期日" width="120" align="center">
          <template #default="{ row }">
            <span :class="{ danger: row.overdueDays > 0 }">
              {{ row.dueDate || '--' }}
            </span>
            <el-tooltip
              v-if="row.dueDateOverridden"
              content="该单单独指定了到期日，未套用客户账期"
            >
              <span class="override-mark">改</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="账龄" width="120" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.overdueDays > 0 ? 'danger' : 'success'"
              size="small"
              effect="plain"
            >
              {{ row.bucketLabel || '--' }}
            </el-tag>
          </template>
        </el-table-column>
        <template #empty>
          <div class="empty-tip">这个客户当前没有未收结算单</div>
        </template>
      </el-table>
    </div>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    getAgingDetail,
    getCustomerCreditBrief
  } from '@/api/finance/ar-aging';
  import type {
    AgingDetailResult,
    CustomerCreditBrief
  } from '@/api/finance/ar-aging/model';
  import {
    ALERT_LEVEL_MAP,
    CREDIT_STATUS_MAP,
    formatMoney
  } from '../../status-config';

  const props = defineProps<{
    visible: boolean;
    customerId?: number | null;
    baseDate?: string;
  }>();

  const emit = defineEmits<{ (e: 'update:visible', v: boolean): void }>();

  const loading = ref(false);
  const brief = ref<CustomerCreditBrief | null>(null);
  const result = ref<AgingDetailResult | null>(null);

  /** el-alert 没有 danger，高危映射成 error */
  const alertType = computed(() => {
    const t = ALERT_LEVEL_MAP[brief.value?.alertLevel ?? 0]?.type || 'info';
    return (t === 'danger' ? 'error' : t) as
      | 'success'
      | 'info'
      | 'warning'
      | 'error';
  });

  const load = async () => {
    if (!props.customerId) return;
    loading.value = true;
    brief.value = null;
    result.value = null;
    try {
      const [b, d] = await Promise.all([
        // 不传 scene：单纯查看不该往审计流水里写预警事件
        getCustomerCreditBrief(props.customerId),
        getAgingDetail({
          customerId: props.customerId,
          baseDate: props.baseDate
        })
      ]);
      brief.value = b ?? null;
      result.value = d ?? null;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '明细加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .alert {
    margin-bottom: 12px;
  }

  .list-head {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 16px 0 8px;
  }

  .list-title {
    font-weight: 600;
  }

  .num {
    font-variant-numeric: tabular-nums;
  }

  .strong {
    font-weight: 600;
  }

  .received {
    color: var(--el-color-success);
  }

  .danger {
    color: var(--el-color-danger);
  }

  .muted {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .override-mark {
    margin-left: 4px;
    padding: 0 3px;
    border-radius: 2px;
    background: var(--el-fill-color);
    color: var(--el-text-color-secondary);
    font-size: 11px;
  }

  .empty-tip {
    padding: 24px 0;
    color: var(--el-text-color-secondary);
    text-align: center;
  }
</style>
