<template>
  <el-drawer
    :model-value="visible"
    :size="900"
    :title="detail ? `结算单 ${detail.docNo}` : '结算单详情'"
    destroy-on-close
    @update:model-value="updateVisible"
    @open="load"
  >
    <div v-loading="loading">
      <template v-if="detail">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="客户">
            {{ detail.customerName || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag
              :type="(SETTLE_STATUS_MAP[detail.status]?.type as any) || 'info'"
              size="small"
            >
              {{ detail.statusLabel }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="到期日">
            {{ detail.dueDate || '按客户账期' }}
          </el-descriptions-item>
          <el-descriptions-item label="结算金额">
            <span class="num strong"
              >¥ {{ formatMoney(detail.plannedAmount) }}</span
            >
          </el-descriptions-item>
          <el-descriptions-item label="已收金额">
            <span class="num received">
              ¥ {{ formatMoney(detail.receivedAmountTotal) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="未收金额">
            <span class="num"
              >¥ {{ formatMoney(detail.unreceivedAmount) }}</span
            >
          </el-descriptions-item>
          <el-descriptions-item label="收款方式">
            {{ detail.payMethodLabel || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="收款账户">
            {{ detail.receivedAccountLabel || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="到账时间">
            {{ formatDateTime(detail.receivedAt) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="开票">
            <template v-if="detail.invoiceRequired === 1">
              需开票 · 已开 ¥ {{ formatMoney(detail.invoiceAmountTotal) }}
            </template>
            <span v-else class="muted">不开票</span>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ detail.remark || '--' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="关联对账单" name="recons">
            <el-table :data="detail.recons" size="small" max-height="300">
              <el-table-column
                prop="reconDocNo"
                label="对账单号"
                min-width="170"
              />
              <el-table-column label="本单认领金额" width="150" align="right">
                <template #default="{ row }">
                  <span class="num"
                    >¥ {{ formatMoney(row.appliedAmount) }}</span
                  >
                </template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="140" />
              <el-table-column
                v-if="detail.actions.canLinkRecon"
                label="操作"
                width="90"
                align="center"
              >
                <template #default="{ row }">
                  <el-link
                    type="danger"
                    :underline="false"
                    v-permission="'finance:cust-settle:link-recon'"
                    @click="unlink(row.id, row.reconDocNo)"
                  >
                    解除
                  </el-link>
                </template>
              </el-table-column>
              <template #empty>
                <div class="empty-tip">还没有关联对账单</div>
              </template>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="到账构成" name="receipts">
            <el-table :data="detail.receipts" size="small" max-height="300">
              <el-table-column prop="receiptId" label="收款单" width="110" />
              <el-table-column label="核销金额" width="140" align="right">
                <template #default="{ row }">
                  <span class="num"
                    >¥ {{ formatMoney(row.appliedAmount) }}</span
                  >
                </template>
              </el-table-column>
              <el-table-column label="核销时间" width="180" align="center">
                <template #default="{ row }">
                  {{ formatDateTime(row.settledAt) || '--' }}
                </template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="140" />
              <template #empty>
                <div class="empty-tip">
                  暂无核销记录。整单直登的收款不产生核销明细。
                </div>
              </template>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="操作记录" name="events">
            <el-timeline v-if="events.length">
              <el-timeline-item
                v-for="e in events"
                :key="e.id"
                :timestamp="formatDateTime(e.eventTime)"
                placement="top"
              >
                <div class="event-title">
                  {{ EVENT_TYPE_LABELS[e.eventType] || `事件 ${e.eventType}` }}
                  <span v-if="e.operatorName" class="muted">
                    · {{ e.operatorName }}
                  </span>
                </div>
                <div v-if="e.reason" class="muted">{{ e.reason }}</div>
              </el-timeline-item>
            </el-timeline>
            <div v-else class="empty-tip">暂无操作记录</div>
          </el-tab-pane>
        </el-tabs>
      </template>
    </div>

    <template #footer>
      <div v-if="detail" class="drawer-footer">
        <el-button
          v-if="detail.actions.canSubmit"
          type="warning"
          v-permission="'finance:cust-settle:submit'"
          @click="submit"
        >
          提交审批
        </el-button>
        <el-button
          v-if="detail.actions.canApprove"
          type="primary"
          v-permission="'finance:cust-settle:approve'"
          @click="approve"
        >
          审批通过
        </el-button>
        <el-button
          v-if="detail.actions.canReject"
          type="danger"
          plain
          v-permission="'finance:cust-settle:reject'"
          @click="askReason('reject')"
        >
          审批驳回
        </el-button>
        <el-button
          v-if="detail.actions.canReceive"
          type="primary"
          v-permission="'finance:cust-settle:receive'"
          @click="receiveVisible = true"
        >
          登记收款
        </el-button>
        <el-button
          v-if="detail.actions.canWithdraw"
          v-permission="'finance:cust-settle:withdraw'"
          @click="askReason('withdraw')"
        >
          退回草稿
        </el-button>
        <el-button
          v-if="detail.actions.canCancelReceive"
          v-permission="'finance:cust-settle:cancel-receive'"
          @click="askReason('cancelReceive')"
        >
          撤销收款
        </el-button>
        <el-button
          v-if="detail.actions.canCancel"
          type="danger"
          plain
          v-permission="'finance:cust-settle:cancel'"
          @click="askReason('cancel')"
        >
          撤销结算单
        </el-button>
        <el-button @click="updateVisible(false)">关闭</el-button>
      </div>
    </template>

    <settlement-receive
      v-if="detail"
      v-model:visible="receiveVisible"
      :settle-id="detail.id"
      @done="reloadAll"
    />
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import SettlementReceive from './settlement-receive.vue';
  import {
    approveSettlement,
    cancelSettleReceive,
    cancelSettlement,
    getSettlement,
    listSettleEvents,
    rejectSettlement,
    submitSettlement,
    unlinkSettleRecon,
    withdrawSettlement
  } from '@/api/finance/customer-settlement';
  import type { SettleDetail } from '@/api/finance/customer-settlement/model';
  import type { FinanceDocEvent } from '@/api/finance/customer-recon/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    EVENT_TYPE_LABELS,
    formatMoney,
    SETTLE_STATUS_MAP
  } from '../../status-config';

  const props = defineProps<{ visible: boolean; settleId?: number | null }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'changed'): void;
  }>();

  const loading = ref(false);
  const activeTab = ref('recons');
  const detail = ref<SettleDetail | null>(null);
  const events = ref<FinanceDocEvent[]>([]);
  const receiveVisible = ref(false);

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const load = async () => {
    if (!props.settleId) return;
    loading.value = true;
    activeTab.value = 'recons';
    try {
      const [d, ev] = await Promise.all([
        getSettlement(props.settleId),
        listSettleEvents(props.settleId)
      ]);
      detail.value = d ?? null;
      events.value = ev;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '打开失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const reloadAll = async () => {
    await load();
    emit('changed');
  };

  const run = async (
    action: () => Promise<unknown>,
    texts: { loading: string; success: string; fail: string }
  ) => {
    const l = EleMessage.loading({ message: texts.loading, plain: true });
    try {
      await action();
      l.close();
      EleMessage.success({ message: texts.success, plain: true });
      await reloadAll();
    } catch (e: unknown) {
      l.close();
      const msg = (e as { message?: string }).message || texts.fail;
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const submit = async () => {
    if (!detail.value) return;
    await run(() => submitSettlement(detail.value!.id), {
      loading: '正在提交审批，请稍候…',
      success: '已提交审批',
      fail: '提交失败，请稍后重试'
    });
  };

  const approve = async () => {
    if (!detail.value) return;
    try {
      await ElMessageBox.confirm('通过后即可收款。', '审批通过', {
        type: 'warning',
        confirmButtonText: '通过',
        cancelButtonText: '取消'
      });
    } catch {
      return;
    }
    await run(() => approveSettlement(detail.value!.id), {
      loading: '正在审批，请稍候…',
      success: '已审批通过',
      fail: '审批失败，请稍后重试'
    });
  };

  const unlink = async (linkId: number, docNo?: string) => {
    if (!detail.value) return;
    try {
      await ElMessageBox.confirm(
        `解除后对账单「${docNo || linkId}」的金额会回到可结算池。`,
        '解除关联',
        { type: 'warning', confirmButtonText: '解除', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    await run(() => unlinkSettleRecon(detail.value!.id, linkId), {
      loading: '正在解除关联，请稍候…',
      success: '已解除关联',
      fail: '解除失败，请稍后重试'
    });
  };

  const REASON_ACTIONS: Record<
    string,
    { title: string; tip: string; success: string; fail: string }
  > = {
    reject: {
      title: '审批驳回',
      tip: '驳回后单据回到草稿，请说明原因（不少于 5 个字）',
      success: '已驳回',
      fail: '驳回失败，请稍后重试'
    },
    withdraw: {
      title: '退回草稿',
      tip: '退回后可继续调整，请说明原因（不少于 5 个字）',
      success: '已退回草稿',
      fail: '退回失败，请稍后重试'
    },
    cancelReceive: {
      title: '撤销收款',
      tip: '撤销后关联运单会解锁，请说明原因（不少于 5 个字）',
      success: '已撤销收款，关联运单已解锁',
      fail: '撤销失败，请稍后重试'
    },
    cancel: {
      title: '撤销结算单',
      tip: '撤销后对账单金额回到可结算池，请说明原因（不少于 5 个字）',
      success: '结算单已撤销',
      fail: '撤销失败，请稍后重试'
    }
  };

  const askReason = async (
    key: 'reject' | 'withdraw' | 'cancelReceive' | 'cancel'
  ) => {
    if (!detail.value) return;
    const cfg = REASON_ACTIONS[key];
    let reason = '';
    try {
      const { value } = await ElMessageBox.prompt(cfg.tip, cfg.title, {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValidator: (v: string) =>
          (v || '').trim().length >= 5 || '原因不少于 5 个字'
      });
      reason = (value || '').trim();
    } catch {
      return;
    }
    const id = detail.value.id;
    const calls: Record<string, () => Promise<unknown>> = {
      reject: () => rejectSettlement(id, reason),
      withdraw: () => withdrawSettlement(id, reason),
      cancelReceive: () => cancelSettleReceive(id, reason),
      cancel: () => cancelSettlement(id, reason)
    };
    await run(calls[key], {
      loading: `正在${cfg.title}，请稍候…`,
      success: cfg.success,
      fail: cfg.fail
    });
  };
</script>

<style lang="scss" scoped>
  .num {
    font-variant-numeric: tabular-nums;
  }

  .strong {
    font-weight: 600;
  }

  .received {
    color: var(--el-color-success);
  }

  .muted {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .detail-tabs {
    margin-top: 8px;
  }

  .empty-tip {
    padding: 24px 0;
    color: var(--el-text-color-secondary);
    text-align: center;
  }

  .event-title {
    font-weight: 500;
  }

  .drawer-footer {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-end;
  }
</style>
