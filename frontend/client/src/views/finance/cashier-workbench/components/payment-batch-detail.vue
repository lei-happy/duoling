<!--
  打款批次详情

  执行打款时默认「全部成功」，个别笔失败就在勾选框里取消并填原因；失败笔留在批次里，
  补打完成后批次才会变成已执行。
-->
<template>
  <el-drawer
    :model-value="visible"
    :size="960"
    :title="detail ? `打款批次 ${detail.docNo}` : '打款批次'"
    destroy-on-close
    @update:model-value="updateVisible"
    @open="load"
  >
    <div v-loading="loading">
      <template v-if="detail">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="状态">
            <el-tag
              :type="
                (PAYMENT_BATCH_STATUS_MAP[detail.status]?.type as any) || 'info'
              "
              size="small"
            >
              {{ detail.statusLabel }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="付款账户">
            {{ detail.bankAccountLabel || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="付款方式">
            {{ detail.payMethodLabel || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="批次金额">
            <span class="num strong">
              ¥ {{ formatMoney(detail.totalAmount) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="已付金额">
            <span class="num paid">¥ {{ formatMoney(detail.paidAmount) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="笔数">
            {{ detail.itemCount }} 笔
            <span v-if="detail.successCount" class="muted">
              成功 {{ detail.successCount }}
            </span>
            <span v-if="detail.failCount" class="fail-text">
              失败 {{ detail.failCount }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="计划付款日">
            {{ detail.planPayDate || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="执行时间">
            {{ formatDateTime(detail.execFinishedAt) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(detail.createdAt) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="3">
            {{ detail.remark || '--' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-alert
          v-if="detail.status === 6"
          type="warning"
          :closable="false"
          show-icon
          class="tip-alert"
          title="有笔数打款失败，补打成功后批次才算完成"
        />
        <el-alert
          v-else-if="detail.status === 4"
          type="error"
          :closable="false"
          show-icon
          class="tip-alert"
          :title="`批次已撤销：${detail.cancelReason || '未填原因'}`"
        />

        <div class="section-head">
          <span class="section-title">批次明细</span>
          <el-button
            v-if="detail.actions.canExecute"
            size="small"
            type="primary"
            v-permission="'finance:cashier-wb:batch-pay'"
            @click="openExec"
          >
            执行打款
          </el-button>
        </div>

        <el-table :data="detail.items" size="small" max-height="320">
          <el-table-column label="单据" min-width="180">
            <template #default="{ row }">
              <div>{{ row.docNo || `#${row.docId}` }}</div>
              <div class="muted">{{ row.docKindLabel }}</div>
            </template>
          </el-table-column>
          <el-table-column label="收款方" min-width="170">
            <template #default="{ row }">
              <div>{{ row.payeeName || '--' }}</div>
              <div v-if="row.payeeBankAccount" class="muted">
                {{ row.payeeBankName }} {{ row.payeeBankAccount }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="金额" width="130" align="right">
            <template #default="{ row }">
              <span class="num">¥ {{ formatMoney(row.amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="执行结果" width="120" align="center">
            <template #default="{ row }">
              <el-tag
                :type="
                  (BATCH_EXEC_STATUS_MAP[row.execStatus]?.type as any) || 'info'
                "
                size="small"
              >
                {{ row.execStatusLabel }}
              </el-tag>
              <div v-if="row.failReason" class="fail-text">
                {{ row.failReason }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="银行流水号" min-width="140">
            <template #default="{ row }">{{
              row.bankSerialNo || '--'
            }}</template>
          </el-table-column>
          <el-table-column
            v-if="detail.actions.canEdit"
            label="操作"
            width="80"
            align="center"
          >
            <template #default="{ row }">
              <el-link
                type="danger"
                :underline="false"
                @click="removeItem(row.id, row.docNo)"
              >
                移出
              </el-link>
            </template>
          </el-table-column>
          <template #empty>
            <div class="empty-tip">批次里没有单据</div>
          </template>
        </el-table>

        <div class="section-head">
          <span class="section-title">操作记录</span>
        </div>
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
      </template>
    </div>

    <template #footer>
      <div v-if="detail" class="drawer-footer">
        <el-button
          v-if="detail.actions.canSubmit"
          type="primary"
          v-permission="'finance:cashier-wb:batch-pay'"
          @click="submit"
        >
          提交审批
        </el-button>
        <el-button
          v-if="detail.actions.canApprove"
          type="success"
          v-permission="'finance:cashier-wb:batch-pay'"
          @click="approve"
        >
          审批通过
        </el-button>
        <el-button
          v-if="detail.actions.canReject"
          v-permission="'finance:cashier-wb:batch-pay'"
          @click="askReason('reject')"
        >
          拒绝
        </el-button>
        <el-button
          v-if="detail.actions.canExecute"
          type="primary"
          v-permission="'finance:cashier-wb:batch-pay'"
          @click="openExec"
        >
          执行打款
        </el-button>
        <el-button
          v-if="detail.actions.canCancel"
          type="danger"
          plain
          v-permission="'finance:cashier-wb:batch-pay'"
          @click="askReason('cancel')"
        >
          撤销批次
        </el-button>
        <el-button @click="updateVisible(false)">关闭</el-button>
      </div>
    </template>

    <!-- 执行打款 -->
    <el-dialog
      v-model="execVisible"
      title="执行打款"
      width="760px"
      append-to-body
    >
      <div class="exec-tip">
        默认按全部成功登记。某笔没打成功就取消勾选并填原因，失败笔会留在批次里等补打。
      </div>
      <el-table :data="execRows" size="small" max-height="340">
        <el-table-column label="成功" width="70" align="center">
          <template #default="{ row }">
            <el-checkbox v-model="row.success" />
          </template>
        </el-table-column>
        <el-table-column label="单据" min-width="150">
          <template #default="{ row }">{{ row.docNo }}</template>
        </el-table-column>
        <el-table-column label="收款方" min-width="130">
          <template #default="{ row }">{{ row.payeeName || '--' }}</template>
        </el-table-column>
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">
            ¥ {{ formatMoney(row.amount) }}
          </template>
        </el-table-column>
        <el-table-column label="银行流水号 / 失败原因" min-width="200">
          <template #default="{ row }">
            <el-input
              v-if="row.success"
              v-model="row.bankSerialNo"
              size="small"
              placeholder="选填，回单上的流水号"
              maxlength="64"
            />
            <el-input
              v-else
              v-model="row.failReason"
              size="small"
              placeholder="如：账号错误被退回"
              maxlength="255"
            />
          </template>
        </el-table-column>
      </el-table>
      <div class="exec-sum">
        本次成功 {{ execSuccessCount }} 笔，合计 ¥
        {{ formatMoney(execSuccessAmount) }}
      </div>
      <template #footer>
        <el-button @click="execVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="doExec">
          确认已打款
        </el-button>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import {
    approvePaymentBatch,
    cancelPaymentBatch,
    executePaymentBatch,
    getPaymentBatch,
    listPaymentBatchEvents,
    rejectPaymentBatch,
    removePaymentBatchItem,
    submitPaymentBatch
  } from '@/api/finance/payment-batch';
  import type {
    FinanceDocEvent,
    PaymentBatchDetail
  } from '@/api/finance/payment-batch/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    BATCH_EXEC_STATUS_MAP,
    EVENT_TYPE_LABELS,
    formatMoney,
    PAYMENT_BATCH_STATUS_MAP
  } from '../../status-config';

  interface ExecRow {
    itemId: number;
    docNo?: string;
    payeeName?: string;
    amount: number;
    success: boolean;
    bankSerialNo?: string;
    failReason?: string;
  }

  const props = defineProps<{ visible: boolean; batchId?: number | null }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'changed'): void;
  }>();

  const loading = ref(false);
  const saving = ref(false);
  const detail = ref<PaymentBatchDetail | null>(null);
  const events = ref<FinanceDocEvent[]>([]);
  const execVisible = ref(false);
  const execRows = ref<ExecRow[]>([]);

  const execSuccessCount = computed(
    () => execRows.value.filter((r) => r.success).length
  );

  const execSuccessAmount = computed(() =>
    execRows.value
      .filter((r) => r.success)
      .reduce((sum, r) => sum + Number(r.amount || 0), 0)
  );

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const load = async () => {
    if (!props.batchId) return;
    loading.value = true;
    try {
      const [d, ev] = await Promise.all([
        getPaymentBatch(props.batchId),
        listPaymentBatchEvents(props.batchId)
      ]);
      detail.value = d ?? null;
      events.value = ev;
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '打开失败，请重试',
        plain: true
      });
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
      EleMessage.error({
        message: (e as { message?: string }).message || texts.fail,
        plain: true
      });
    }
  };

  const submit = async () => {
    if (!detail.value) return;
    await run(() => submitPaymentBatch(detail.value!.id), {
      loading: '正在提交批次，请稍候…',
      success: '已提交审批',
      fail: '提交失败，请稍后重试'
    });
  };

  const approve = async () => {
    if (!detail.value) return;
    await run(() => approvePaymentBatch(detail.value!.id), {
      loading: '正在审批批次，请稍候…',
      success: '已审批，可以打款了',
      fail: '审批失败，请稍后重试'
    });
  };

  const removeItem = async (itemId: number, docNo?: string) => {
    if (!detail.value) return;
    try {
      await ElMessageBox.confirm(
        `移出后单据「${docNo || itemId}」会回到待打款池。`,
        '移出批次',
        { type: 'warning', confirmButtonText: '移出', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    await run(() => removePaymentBatchItem(detail.value!.id, itemId), {
      loading: '正在移出单据，请稍候…',
      success: '已移出',
      fail: '移出失败，请稍后重试'
    });
  };

  const openExec = () => {
    if (!detail.value) return;
    execRows.value = detail.value.items
      .filter((x) => x.execStatus !== 1)
      .map((x) => ({
        itemId: x.id,
        docNo: x.docNo,
        payeeName: x.payeeName,
        amount: x.amount,
        success: true,
        bankSerialNo: x.bankSerialNo,
        failReason: void 0
      }));
    if (!execRows.value.length) {
      EleMessage.info({ message: '这个批次已经全部打款成功了', plain: true });
      return;
    }
    execVisible.value = true;
  };

  const doExec = async () => {
    if (!detail.value) return;
    const bad = execRows.value.find(
      (r) => !r.success && !(r.failReason || '').trim()
    );
    if (bad) {
      EleMessage.warning({
        message: `请填「${bad.docNo}」的失败原因，方便后续补打`,
        plain: true
      });
      return;
    }
    saving.value = true;
    const id = detail.value.id;
    const results = execRows.value.map((r) => ({
      itemId: r.itemId,
      success: r.success,
      bankSerialNo: r.success ? r.bankSerialNo : void 0,
      failReason: r.success ? void 0 : r.failReason
    }));
    try {
      await executePaymentBatch(id, { results });
      execVisible.value = false;
      EleMessage.success({ message: '已登记打款结果', plain: true });
      await reloadAll();
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '登记失败，请稍后重试',
        plain: true
      });
    } finally {
      saving.value = false;
    }
  };

  const REASON_ACTIONS: Record<
    string,
    { title: string; tip: string; success: string; fail: string }
  > = {
    reject: {
      title: '拒绝批次',
      tip: '拒绝后批次退回草稿，可以改账户或移出单据。请说明原因（不少于 5 个字）',
      success: '已拒绝，批次退回草稿',
      fail: '操作失败，请稍后重试'
    },
    cancel: {
      title: '撤销批次',
      tip: '撤销后批次里的单会回到待打款池。请说明原因（不少于 5 个字）',
      success: '批次已撤销，单已放回待付池',
      fail: '撤销失败，请稍后重试'
    }
  };

  const askReason = async (key: 'reject' | 'cancel') => {
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
    await run(
      () =>
        key === 'reject'
          ? rejectPaymentBatch(id, reason)
          : cancelPaymentBatch(id, reason),
      {
        loading: `正在${cfg.title}，请稍候…`,
        success: cfg.success,
        fail: cfg.fail
      }
    );
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

  .muted {
    margin-left: 6px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .fail-text {
    margin-left: 6px;
    color: var(--el-color-danger);
    font-size: 12px;
  }

  .tip-alert {
    margin-top: 12px;
  }

  .section-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 16px 0 8px;
  }

  .section-title {
    font-weight: 600;
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

  .exec-tip {
    margin-bottom: 10px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .exec-sum {
    margin-top: 8px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }
</style>
