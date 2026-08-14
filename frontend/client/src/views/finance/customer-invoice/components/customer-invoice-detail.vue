<template>
  <el-drawer
    :model-value="visible"
    :size="920"
    :title="detail ? `开票申请 ${detail.docNo}` : '开票申请详情'"
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
              :type="
                (CUSTOMER_INVOICE_STATUS_MAP[detail.status]?.type as any) ||
                'info'
              "
              size="small"
            >
              {{ detail.statusLabel }}
            </el-tag>
            <span v-if="detail.isRedFlush === 1" class="muted">红字票</span>
          </el-descriptions-item>
          <el-descriptions-item label="发票类型">
            {{ detail.invoiceTypeLabel }}
          </el-descriptions-item>
          <el-descriptions-item label="发票号码">
            {{ detail.invoiceNo || '未开票' }}
            <span v-if="detail.invoiceCode" class="muted">
              代码 {{ detail.invoiceCode }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="开票日期">
            {{ formatDate(detail.invoiceDate) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="开票时间">
            {{ formatDateTime(detail.issuedAt) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="价税合计">
            <span class="num strong">
              ¥ {{ formatMoney(detail.amountInclTax) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="不含税 / 税额">
            <span class="num">
              {{ formatMoney(detail.amountExclTax) }} /
              {{ formatMoney(detail.taxAmount) }}
            </span>
            <span v-if="detail.taxRate != null" class="muted">
              {{ detail.taxRate }}%
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="开票主体">
            {{ detail.sellerTitle || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="购方名称">
            {{ detail.buyerTitle || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="购方税号">
            {{ detail.buyerTaxNo || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="发票文件">
            <el-link
              v-if="detail.pdfUrl"
              type="primary"
              :href="detail.pdfUrl"
              target="_blank"
              :underline="false"
            >
              查看 PDF
            </el-link>
            <span v-else>未上传</span>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="3">
            {{ detail.remark || '--' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-alert
          v-if="detail.warning"
          type="warning"
          :closable="false"
          show-icon
          class="tip-alert"
          :title="detail.warning"
        />
        <el-alert
          v-else-if="detail.status === 9"
          type="error"
          :closable="false"
          show-icon
          class="tip-alert"
          :title="`这张票已作废：${detail.voidReason || '未填原因'}`"
        />
        <el-alert
          v-else-if="detail.status === 3"
          type="success"
          :closable="false"
          show-icon
          class="tip-alert"
          title="已开票，关联结算单已锁定；金额有误请作废或红冲，不要直接改结算单"
        />

        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="关联结算单" name="settles">
            <div v-if="detail.actions.canEdit" class="tab-toolbar">
              <el-button
                size="small"
                type="primary"
                plain
                v-permission="'finance:cust-invoice:edit'"
                @click="linkVisible = true"
              >
                补挂结算单
              </el-button>
              <span class="toolbar-tip">
                关联合计需与票面价税合计一致才能开票
              </span>
            </div>
            <el-table :data="detail.settles" size="small" max-height="260">
              <el-table-column
                prop="settleDocNo"
                label="结算单号"
                min-width="180"
              />
              <el-table-column label="开票金额" width="150" align="right">
                <template #default="{ row }">
                  <span class="num"
                    >¥ {{ formatMoney(row.appliedAmount) }}</span
                  >
                </template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="130" />
              <el-table-column
                v-if="detail.actions.canEdit"
                label="操作"
                width="90"
                align="center"
              >
                <template #default="{ row }">
                  <el-link
                    type="danger"
                    :underline="false"
                    v-permission="'finance:cust-invoice:edit'"
                    @click="unlink(row.id, row.settleDocNo)"
                  >
                    移除
                  </el-link>
                </template>
              </el-table-column>
              <template #empty>
                <div class="empty-tip">还没挂结算单，先补挂再提交开票</div>
              </template>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="开票明细" name="items">
            <el-table :data="detail.items" size="small" max-height="260">
              <el-table-column prop="itemName" label="品名" min-width="160" />
              <el-table-column label="税率" width="90" align="center">
                <template #default="{ row }">
                  {{ row.taxRate != null ? `${row.taxRate}%` : '--' }}
                </template>
              </el-table-column>
              <el-table-column label="不含税额" width="130" align="right">
                <template #default="{ row }">
                  <span class="num">
                    ¥ {{ formatMoney(row.amountExclTax) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="税额" width="130" align="right">
                <template #default="{ row }">
                  <span class="num">¥ {{ formatMoney(row.taxAmount) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="价税合计" width="130" align="right">
                <template #default="{ row }">
                  <span class="num strong">
                    ¥ {{ formatMoney(row.amountInclTax) }}
                  </span>
                </template>
              </el-table-column>
              <template #empty>
                <div class="empty-tip">没有开票行</div>
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
          type="primary"
          v-permission="'finance:cust-invoice:submit'"
          @click="submit"
        >
          提交开票
        </el-button>
        <el-button
          v-if="detail.actions.canIssue"
          type="success"
          v-permission="'finance:cust-invoice:issue'"
          @click="issueVisible = true"
        >
          登记开票
        </el-button>
        <el-button
          v-if="detail.actions.canWithdraw"
          v-permission="'finance:cust-invoice:edit'"
          @click="askReason('withdraw')"
        >
          退回草稿
        </el-button>
        <el-button
          v-if="detail.actions.canRedFlush"
          type="warning"
          plain
          v-permission="'finance:cust-invoice:red-flush'"
          @click="askReason('redFlush')"
        >
          红冲
        </el-button>
        <el-button
          v-if="detail.actions.canVoid"
          type="danger"
          plain
          v-permission="'finance:cust-invoice:void'"
          @click="askReason('void')"
        >
          作废
        </el-button>
        <el-button
          v-if="detail.actions.canCancel"
          v-permission="'finance:cust-invoice:edit'"
          @click="askReason('cancel')"
        >
          撤销申请
        </el-button>
        <el-button @click="updateVisible(false)">关闭</el-button>
      </div>
    </template>

    <!-- 登记开票结果 -->
    <el-dialog
      v-model="issueVisible"
      title="登记开票结果"
      width="480px"
      append-to-body
    >
      <el-form :model="issueForm" label-width="88px">
        <el-form-item label="发票号码" required>
          <el-input
            v-model="issueForm.invoiceNo"
            placeholder="税控系统开出的发票号"
            maxlength="50"
          />
        </el-form-item>
        <el-form-item label="发票代码">
          <el-input v-model="issueForm.invoiceCode" maxlength="30" />
        </el-form-item>
        <el-form-item label="开票日期">
          <el-date-picker
            v-model="issueForm.invoiceDate"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="留空按今天"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="PDF 链接">
          <el-input
            v-model="issueForm.pdfUrl"
            placeholder="选填，方便客户自取"
            maxlength="500"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="issueVisible = false">取消</el-button>
        <el-button type="primary" @click="doIssue">确认已开票</el-button>
      </template>
    </el-dialog>

    <!-- 补挂结算单 -->
    <el-dialog
      v-if="detail"
      v-model="linkVisible"
      title="补挂结算单"
      width="720px"
      append-to-body
      @open="loadCandidates"
    >
      <el-table
        ref="candTableRef"
        :data="candidates"
        v-loading="candLoading"
        size="small"
        height="320"
        row-key="settleId"
        @selection-change="
          (rows: InvoiceSettleCandidate[]) => (candSelected = rows)
        "
      >
        <el-table-column type="selection" width="42" />
        <el-table-column prop="docNo" label="结算单号" min-width="170" />
        <el-table-column label="结算金额" width="120" align="right">
          <template #default="{ row }">
            ¥ {{ formatMoney(row.plannedAmount) }}
          </template>
        </el-table-column>
        <el-table-column label="本次可开" width="120" align="right">
          <template #default="{ row }">
            ¥ {{ formatMoney(row.availableAmount) }}
          </template>
        </el-table-column>
        <el-table-column label="账期" width="110" align="center">
          <template #default="{ row }">{{ row.dueDate || '--' }}</template>
        </el-table-column>
        <template #empty>
          <div class="empty-tip">这个客户没有其他可开票的结算单</div>
        </template>
      </el-table>
      <template #footer>
        <el-button @click="linkVisible = false">取消</el-button>
        <el-button type="primary" @click="doLink">挂上</el-button>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { reactive, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import {
    cancelCustomerInvoice,
    getCustomerInvoice,
    issueCustomerInvoice,
    linkInvoiceSettles,
    listCustomerInvoiceEvents,
    listInvoiceSettleCandidates,
    redFlushCustomerInvoice,
    submitCustomerInvoice,
    unlinkInvoiceSettle,
    voidCustomerInvoice,
    withdrawCustomerInvoice
  } from '@/api/finance/customer-invoice';
  import type {
    CustomerInvoiceDetail,
    FinanceDocEvent,
    InvoiceIssuePayload,
    InvoiceSettleCandidate
  } from '@/api/finance/customer-invoice/model';
  import { formatDate, formatDateTime } from '@/utils/date-util';
  import {
    CUSTOMER_INVOICE_STATUS_MAP,
    EVENT_TYPE_LABELS,
    formatMoney
  } from '../../status-config';

  const props = defineProps<{ visible: boolean; invoiceId?: number | null }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'changed'): void;
  }>();

  const loading = ref(false);
  const activeTab = ref('settles');
  const detail = ref<CustomerInvoiceDetail | null>(null);
  const events = ref<FinanceDocEvent[]>([]);

  const issueVisible = ref(false);
  const issueForm = reactive<InvoiceIssuePayload>({ invoiceNo: '' });

  const linkVisible = ref(false);
  const candTableRef = ref();
  const candidates = ref<InvoiceSettleCandidate[]>([]);
  const candSelected = ref<InvoiceSettleCandidate[]>([]);
  const candLoading = ref(false);

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const load = async () => {
    if (!props.invoiceId) return;
    loading.value = true;
    activeTab.value = 'settles';
    try {
      const [d, ev] = await Promise.all([
        getCustomerInvoice(props.invoiceId),
        listCustomerInvoiceEvents(props.invoiceId)
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
    await run(() => submitCustomerInvoice(detail.value!.id), {
      loading: '正在提交开票申请，请稍候…',
      success: '已提交，等开票员登记发票号',
      fail: '提交失败，请稍后重试'
    });
  };

  const doIssue = async () => {
    if (!detail.value) return;
    if (!issueForm.invoiceNo?.trim()) {
      EleMessage.warning({ message: '请填发票号码', plain: true });
      return;
    }
    const id = detail.value.id;
    const payload = { ...issueForm };
    issueVisible.value = false;
    await run(() => issueCustomerInvoice(id, payload), {
      loading: '正在登记开票结果，请稍候…',
      success: '已登记开票，关联结算单已锁定',
      fail: '登记失败，请稍后重试'
    });
    issueForm.invoiceNo = '';
    issueForm.invoiceCode = void 0;
    issueForm.invoiceDate = void 0;
    issueForm.pdfUrl = void 0;
  };

  const loadCandidates = async () => {
    if (!detail.value) return;
    candLoading.value = true;
    candSelected.value = [];
    try {
      const res = await listInvoiceSettleCandidates({
        customerId: detail.value.customerId,
        invoiceId: detail.value.id
      });
      candidates.value = res?.list ?? [];
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '加载失败，请重试',
        plain: true
      });
    } finally {
      candLoading.value = false;
    }
  };

  const doLink = async () => {
    if (!detail.value) return;
    if (!candSelected.value.length) {
      EleMessage.warning({ message: '请勾选要挂上的结算单', plain: true });
      return;
    }
    const id = detail.value.id;
    const allocations = candSelected.value.map((r) => ({
      settleId: r.settleId
    }));
    linkVisible.value = false;
    await run(() => linkInvoiceSettles(id, allocations), {
      loading: '正在挂结算单，请稍候…',
      success: '已挂上，票面金额已同步',
      fail: '挂接失败，请稍后重试'
    });
  };

  const unlink = async (linkId: number, docNo?: string) => {
    if (!detail.value) return;
    try {
      await ElMessageBox.confirm(
        `移除后结算单「${docNo || linkId}」的开票进度会回退。`,
        '移除结算单',
        { type: 'warning', confirmButtonText: '移除', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    await run(() => unlinkInvoiceSettle(detail.value!.id, linkId), {
      loading: '正在移除结算单，请稍候…',
      success: '已移除',
      fail: '移除失败，请稍后重试'
    });
  };

  const REASON_ACTIONS: Record<
    string,
    { title: string; tip: string; success: string; fail: string }
  > = {
    withdraw: {
      title: '退回草稿',
      tip: '退回后可以继续改票面与结算单。请说明原因（不少于 5 个字）',
      success: '已退回草稿',
      fail: '退回失败，请稍后重试'
    },
    void: {
      title: '作废发票',
      tip: '作废用于当月开错票，结算单会解锁并回退开票进度。请说明原因（不少于 5 个字）',
      success: '发票已作废，结算单已解锁',
      fail: '作废失败，请稍后重试'
    },
    redFlush: {
      title: '红冲发票',
      tip: '红冲会生成一张红字票冲掉原票，适用于跨月开错。请说明原因（不少于 5 个字）',
      success: '已红冲，红字票已生成',
      fail: '红冲失败，请稍后重试'
    },
    cancel: {
      title: '撤销申请',
      tip: '撤销后这份申请作废，结算单回到待开票池。请说明原因（不少于 5 个字）',
      success: '已撤销开票申请',
      fail: '撤销失败，请稍后重试'
    }
  };

  const askReason = async (
    key: 'withdraw' | 'void' | 'redFlush' | 'cancel'
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
    const call = () => {
      if (key === 'withdraw') return withdrawCustomerInvoice(id, reason);
      if (key === 'void') return voidCustomerInvoice(id, reason);
      if (key === 'redFlush') return redFlushCustomerInvoice(id, reason);
      return cancelCustomerInvoice(id, reason);
    };
    await run(call, {
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

  .muted {
    margin-left: 6px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .tip-alert {
    margin-top: 12px;
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

  .toolbar-tip {
    color: var(--el-text-color-secondary);
    font-size: 12px;
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
