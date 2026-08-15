<template>
  <el-drawer
    :model-value="visible"
    :size="960"
    :title="detail ? `结算单 ${detail.docNo}` : '结算单详情'"
    destroy-on-close
    @update:model-value="updateVisible"
    @open="load"
  >
    <div v-loading="loading">
      <template v-if="detail">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="承运商">
            {{ detail.carrierName || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag
              :type="
                (CARRIER_SETTLE_STATUS_MAP[detail.status]?.type as any) ||
                'info'
              "
              size="small"
            >
              {{ detail.statusLabel }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="到期日">
            {{ detail.dueDate || '未设到期日' }}
          </el-descriptions-item>
          <el-descriptions-item label="应付金额">
            <span class="num strong">
              ¥ {{ formatMoney(detail.plannedAmount) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="已付金额">
            <span class="num paid">
              ¥ {{ formatMoney(detail.paidAmountTotal) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="未付金额">
            <span class="num">¥ {{ formatMoney(detail.unpaidAmount) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="付款方式">
            {{ detail.payMethodLabel || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="付款账户">
            {{ detail.settlementAccountLabel || '--' }}
            <span v-if="detail.bankAccountMasked" class="muted">
              {{ detail.bankAccountMasked }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="付款时间">
            {{ formatDateTime(detail.paidAt) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="进项票" :span="2">
            <template v-if="detail.invoiceMatched === 1">
              票款相符 · 已收 ¥ {{ formatMoney(detail.invoiceAmountTotal) }}
            </template>
            <template v-else>
              已收 ¥ {{ formatMoney(detail.invoiceAmountTotal) }}，还差
              <span class="gap"
                >¥ {{ formatMoney(detail.invoiceGapAmount) }}</span
              >
            </template>
          </el-descriptions-item>
          <el-descriptions-item label="结算方式">
            <el-tag
              v-if="detail.isOffsetOnly === 1"
              type="info"
              size="small"
              effect="plain"
            >
              纯抵账
            </el-tag>
            <span v-else>实付</span>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="3">
            {{ detail.remark || '--' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="关联对账单" name="recons">
            <div v-if="detail.actions.canLinkRecon" class="tab-toolbar">
              <el-button
                size="small"
                type="primary"
                plain
                v-permission="'finance:carrier-settle:link-recon'"
                @click="openLink"
              >
                补挂对账单
              </el-button>
              <el-button
                size="small"
                v-permission="'finance:carrier-settle:edit'"
                @click="openAccount"
              >
                更换付款账户
              </el-button>
            </div>
            <el-table :data="detail.recons" size="small" max-height="300">
              <el-table-column
                prop="reconDocNo"
                label="对账单号"
                min-width="170"
              />
              <el-table-column label="本单认领金额" width="150" align="right">
                <template #default="{ row }">
                  <span class="num">
                    ¥ {{ formatMoney(row.appliedAmount) }}
                  </span>
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
                  <btn-items
                    :items="[
                      {
                        title: '解除',
                        icon: DeleteOutlined,
                        danger: true,
                        permission: 'finance:carrier-settle:link-recon',
                        onClick: () => unlink(row.id, row.reconDocNo)
                      }
                    ]"
                    type="link"
                    :wrap="false"
                  />
                </template>
              </el-table-column>
              <template #empty>
                <div class="empty-tip">还没有关联对账单</div>
              </template>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="进项票构成" name="invoices">
            <el-table :data="detail.invoices" size="small" max-height="300">
              <el-table-column prop="invoiceId" label="发票" width="110" />
              <el-table-column label="核销金额" width="140" align="right">
                <template #default="{ row }">
                  <span class="num">
                    ¥ {{ formatMoney(row.appliedAmount) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="核销时间" width="180" align="center">
                <template #default="{ row }">
                  {{ formatDateTime(row.matchedAt) || '--' }}
                </template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="140" />
              <template #empty>
                <div class="empty-tip">
                  还没收到进项票。收票后到「进项发票」页登记并核销到本单。
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
          v-permission="'finance:carrier-settle:submit'"
          @click="submit"
        >
          提交审批
        </el-button>
        <el-button
          v-if="detail.actions.canApprove"
          type="primary"
          v-permission="'finance:carrier-settle:approve'"
          @click="approve"
        >
          审批通过
        </el-button>
        <el-button
          v-if="detail.actions.canReject"
          type="danger"
          plain
          v-permission="'finance:carrier-settle:reject'"
          @click="askReason('reject')"
        >
          审批驳回
        </el-button>
        <el-button
          v-if="detail.actions.canPay"
          type="primary"
          v-permission="'finance:carrier-settle:pay'"
          @click="payVisible = true"
        >
          登记付款
        </el-button>
        <el-button
          v-if="detail.actions.canWithdraw"
          v-permission="'finance:carrier-settle:withdraw'"
          @click="askReason('withdraw')"
        >
          退回草稿
        </el-button>
        <el-button
          v-if="detail.actions.canCancelPayment"
          v-permission="'finance:carrier-settle:cancel-payment'"
          @click="askReason('cancelPay')"
        >
          撤销付款
        </el-button>
        <el-button
          v-if="detail.actions.canCancel"
          type="danger"
          plain
          v-permission="'finance:carrier-settle:cancel'"
          @click="askReason('cancel')"
        >
          撤销结算单
        </el-button>
        <el-button @click="updateVisible(false)">关闭</el-button>
      </div>
    </template>

    <carrier-settlement-pay
      v-if="detail"
      v-model:visible="payVisible"
      :settle-id="detail.id"
      @done="reloadAll"
    />
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { DeleteOutlined } from '@/components/icons';
  import CarrierSettlementPay from './carrier-settlement-pay.vue';
  import {
    approveCarrierSettle,
    cancelCarrierSettle,
    cancelSettlePay,
    getCarrierSettle,
    linkSettleRecons,
    listCarrierAccounts,
    listCarrierSettleEvents,
    listSettleReconCandidates,
    rejectCarrierSettle,
    submitCarrierSettle,
    unlinkSettleRecon,
    updateSettleAccount,
    withdrawCarrierSettle
  } from '@/api/finance/carrier-settlement';
  import type { CarrierSettleDetail } from '@/api/finance/carrier-settlement/model';
  import type { FinanceDocEvent } from '@/api/finance/customer-recon/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    CARRIER_SETTLE_STATUS_MAP,
    EVENT_TYPE_LABELS,
    formatMoney
  } from '../../status-config';

  const props = defineProps<{ visible: boolean; settleId?: number | null }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'changed'): void;
  }>();

  const loading = ref(false);
  const activeTab = ref('recons');
  const detail = ref<CarrierSettleDetail | null>(null);
  const events = ref<FinanceDocEvent[]>([]);
  const payVisible = ref(false);

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const load = async () => {
    if (!props.settleId) return;
    loading.value = true;
    activeTab.value = 'recons';
    try {
      const [d, ev] = await Promise.all([
        getCarrierSettle(props.settleId),
        listCarrierSettleEvents(props.settleId)
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
    await run(() => submitCarrierSettle(detail.value!.id), {
      loading: '正在提交审批，请稍候…',
      success: '已提交审批',
      fail: '提交失败，请稍后重试'
    });
  };

  const approve = async () => {
    if (!detail.value) return;
    try {
      await ElMessageBox.confirm('通过后即可安排付款。', '审批通过', {
        type: 'warning',
        confirmButtonText: '通过',
        cancelButtonText: '取消'
      });
    } catch {
      return;
    }
    await run(() => approveCarrierSettle(detail.value!.id), {
      loading: '正在审批，请稍候…',
      success: '已审批通过，可安排付款',
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

  /** 补挂对账单：候选少且只需选一张，用选择框比再开一个抽屉更省事 */
  const openLink = async () => {
    if (!detail.value) return;
    const settleId = detail.value.id;
    let candidates;
    try {
      const res = await listSettleReconCandidates({
        carrierId: detail.value.carrierId,
        settleId
      });
      candidates = res?.list ?? [];
    } catch (e: unknown) {
      const msg =
        (e as { message?: string }).message || '对账单加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
      return;
    }
    if (!candidates.length) {
      EleMessage.info({
        message: '这个承运商暂时没有可补挂的对账单',
        plain: true
      });
      return;
    }
    const options = candidates
      .map(
        (c, i) =>
          `${i + 1}. ${c.docNo}（可认领 ¥ ${formatMoney(c.availableAmount)}）`
      )
      .join('\n');
    let pick = '';
    try {
      const { value } = await ElMessageBox.prompt(
        `输入序号选择要补挂的对账单：\n${options}`,
        '补挂对账单',
        {
          confirmButtonText: '补挂',
          cancelButtonText: '取消',
          inputValidator: (v: string) => {
            const n = Number((v || '').trim());
            return (
              (Number.isInteger(n) && n >= 1 && n <= candidates.length) ||
              `请输入 1 ~ ${candidates.length} 之间的序号`
            );
          }
        }
      );
      pick = (value || '').trim();
    } catch {
      return;
    }
    const target = candidates[Number(pick) - 1];
    await run(
      () =>
        linkSettleRecons(settleId, [
          { reconId: target.reconId, appliedAmount: target.availableAmount }
        ]),
      {
        loading: '正在补挂对账单，请稍候…',
        success: `已补挂对账单 ${target.docNo}`,
        fail: '补挂失败，请稍后重试'
      }
    );
  };

  const openAccount = async () => {
    if (!detail.value) return;
    const settleId = detail.value.id;
    let accounts;
    try {
      accounts = await listCarrierAccounts(detail.value.carrierId);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '账户加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
      return;
    }
    if (!accounts.length) {
      EleMessage.info({
        message: '这个承运商还没有配置结算账户，请先到承运商档案维护',
        plain: true
      });
      return;
    }
    const options = accounts
      .map(
        (a, i) =>
          `${i + 1}. ${a.accountLabel || a.bankAccountName || '账户'}` +
          `${a.bankAccountMasked ? ` · ${a.bankAccountMasked}` : ''}`
      )
      .join('\n');
    let pick = '';
    try {
      const { value } = await ElMessageBox.prompt(
        `输入序号选择付款账户：\n${options}`,
        '更换付款账户',
        {
          confirmButtonText: '更换',
          cancelButtonText: '取消',
          inputValidator: (v: string) => {
            const n = Number((v || '').trim());
            return (
              (Number.isInteger(n) && n >= 1 && n <= accounts.length) ||
              `请输入 1 ~ ${accounts.length} 之间的序号`
            );
          }
        }
      );
      pick = (value || '').trim();
    } catch {
      return;
    }
    const target = accounts[Number(pick) - 1];
    await run(() => updateSettleAccount(settleId, target.accountId), {
      loading: '正在更换付款账户，请稍候…',
      success: '已更换付款账户',
      fail: '更换失败，请稍后重试'
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
    cancelPay: {
      title: '撤销付款',
      tip: '撤销后关联任务会解锁，请说明原因（不少于 5 个字）',
      success: '已撤销付款，关联任务已解锁',
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
    key: 'reject' | 'withdraw' | 'cancelPay' | 'cancel'
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
      reject: () => rejectCarrierSettle(id, reason),
      withdraw: () => withdrawCarrierSettle(id, reason),
      cancelPay: () => cancelSettlePay(id, reason),
      cancel: () => cancelCarrierSettle(id, reason)
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

  .paid {
    color: var(--el-color-success);
  }

  .gap {
    color: var(--el-color-warning);
    font-variant-numeric: tabular-nums;
  }

  .muted {
    margin-left: 6px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .detail-tabs {
    margin-top: 8px;
  }

  .tab-toolbar {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
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
