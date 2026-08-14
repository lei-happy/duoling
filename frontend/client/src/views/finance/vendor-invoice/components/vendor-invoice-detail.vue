<template>
  <el-drawer
    :model-value="visible"
    :size="920"
    :title="detail ? `发票 ${detail.invoiceNo}` : '发票详情'"
    destroy-on-close
    @update:model-value="updateVisible"
    @open="load"
  >
    <div v-loading="loading">
      <template v-if="detail">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="供应商">
            {{ detail.vendorName || detail.sellerTitle || '--' }}
            <span class="muted">{{ detail.vendorTypeLabel }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag
              :type="
                (VENDOR_INVOICE_STATUS_MAP[detail.status]?.type as any) ||
                'info'
              "
              size="small"
            >
              {{ detail.statusLabel }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发票类型">
            {{ detail.invoiceTypeLabel }}
          </el-descriptions-item>
          <el-descriptions-item label="发票号码">
            {{ detail.invoiceNo }}
            <span v-if="detail.invoiceCode" class="muted">
              代码 {{ detail.invoiceCode }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="开票日期">
            {{ formatDate(detail.invoiceDate) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="收票时间">
            {{ formatDateTime(detail.receivedAt) || '--' }}
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
          <el-descriptions-item label="核销进度">
            <span class="num paid">
              ¥ {{ formatMoney(detail.settledAmount) }}
            </span>
            <span v-if="detail.unsettledAmount > 0" class="muted">
              待核销 {{ formatMoney(detail.unsettledAmount) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="购方主体">
            {{ detail.buyerTitle || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="抵扣">
            {{ detail.deductible === 1 ? '可抵扣' : '不可抵扣' }}
            <span v-if="detail.deductPeriod" class="muted">
              税期 {{ detail.deductPeriod }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="发票影像">
            <el-link
              v-if="detail.attachmentUrl"
              type="primary"
              :href="detail.attachmentUrl"
              target="_blank"
              :underline="false"
            >
              查看附件
            </el-link>
            <span v-else>未上传</span>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="3">
            {{ detail.remark || '--' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-alert
          v-if="detail.deductWarning"
          type="warning"
          :closable="false"
          show-icon
          class="tip-alert"
          :title="detail.deductWarning"
        />
        <el-alert
          v-else-if="detail.status === 9"
          type="error"
          :closable="false"
          show-icon
          class="tip-alert"
          :title="`这张票已作废：${detail.voidReason || '未填原因'}`"
        />

        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="核销明细" name="settles">
            <div v-if="detail.actions.canMatch" class="tab-toolbar">
              <el-button
                size="small"
                type="primary"
                plain
                v-permission="'finance:vendor-invoice:match'"
                @click="matchVisible = true"
              >
                核销到结算单
              </el-button>
              <span class="toolbar-tip">
                待核销 ¥ {{ formatMoney(detail.unsettledAmount) }}
              </span>
            </div>
            <el-table :data="detail.settles" size="small" max-height="280">
              <el-table-column
                prop="settleDocNo"
                label="结算单号"
                min-width="170"
              />
              <el-table-column label="核销金额" width="140" align="right">
                <template #default="{ row }">
                  <span class="num">
                    ¥ {{ formatMoney(row.appliedAmount) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="核销时间" width="170" align="center">
                <template #default="{ row }">
                  {{ formatDateTime(row.matchedAt) || '--' }}
                </template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="130" />
              <el-table-column
                v-if="detail.actions.canUnmatch"
                label="操作"
                width="90"
                align="center"
              >
                <template #default="{ row }">
                  <el-link
                    type="danger"
                    :underline="false"
                    v-permission="'finance:vendor-invoice:unmatch'"
                    @click="unmatch(row.id, row.settleDocNo)"
                  >
                    撤销
                  </el-link>
                </template>
              </el-table-column>
              <template #empty>
                <div class="empty-tip">
                  这张票还没核销。核销后结算单的票款缺口才会减少。
                </div>
              </template>
            </el-table>
          </el-tab-pane>

          <el-tab-pane
            v-if="detail.isMultiRate === 1"
            label="税率明细"
            name="items"
          >
            <el-table :data="detail.items" size="small" max-height="280">
              <el-table-column prop="itemName" label="项目" min-width="150" />
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
          v-if="detail.actions.canEdit"
          v-permission="'finance:vendor-invoice:edit'"
          @click="emit('edit', detail)"
        >
          修改票面
        </el-button>
        <el-button
          v-if="detail.actions.canVoid"
          type="danger"
          plain
          v-permission="'finance:vendor-invoice:void'"
          @click="askReason('void')"
        >
          作废
        </el-button>
        <el-button
          v-if="detail.actions.canCancel"
          v-permission="'finance:vendor-invoice:cancel'"
          @click="askReason('cancel')"
        >
          撤销登记
        </el-button>
        <el-button @click="updateVisible(false)">关闭</el-button>
      </div>
    </template>

    <invoice-match
      v-if="detail"
      v-model:visible="matchVisible"
      :invoice-id="detail.id"
      :unsettled-amount="detail.unsettledAmount"
      @done="reloadAll"
    />
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import InvoiceMatch from './invoice-match.vue';
  import {
    cancelVendorInvoice,
    getVendorInvoice,
    listVendorInvoiceEvents,
    unmatchVendorInvoice,
    voidVendorInvoice
  } from '@/api/finance/vendor-invoice';
  import type {
    FinanceDocEvent,
    VendorInvoiceDetail
  } from '@/api/finance/vendor-invoice/model';
  import { formatDate, formatDateTime } from '@/utils/date-util';
  import {
    EVENT_TYPE_LABELS,
    formatMoney,
    VENDOR_INVOICE_STATUS_MAP
  } from '../../status-config';

  const props = defineProps<{ visible: boolean; invoiceId?: number | null }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'changed'): void;
    (e: 'edit', invoice: VendorInvoiceDetail): void;
  }>();

  const loading = ref(false);
  const activeTab = ref('settles');
  const detail = ref<VendorInvoiceDetail | null>(null);
  const events = ref<FinanceDocEvent[]>([]);
  const matchVisible = ref(false);

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const load = async () => {
    if (!props.invoiceId) return;
    loading.value = true;
    activeTab.value = 'settles';
    try {
      const [d, ev] = await Promise.all([
        getVendorInvoice(props.invoiceId),
        listVendorInvoiceEvents(props.invoiceId)
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

  const unmatch = async (linkId: number, docNo?: string) => {
    if (!detail.value) return;
    try {
      await ElMessageBox.confirm(
        `撤销后结算单「${docNo || linkId}」的票款缺口会重新变大。`,
        '撤销核销',
        { type: 'warning', confirmButtonText: '撤销', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    await run(() => unmatchVendorInvoice(detail.value!.id, linkId), {
      loading: '正在撤销核销，请稍候…',
      success: '已撤销核销',
      fail: '撤销失败，请稍后重试'
    });
  };

  const REASON_ACTIONS: Record<
    string,
    { title: string; tip: string; success: string; fail: string }
  > = {
    void: {
      title: '作废发票',
      tip: '作废用于承运商红冲重开，核销明细会全部回退。请说明原因（不少于 5 个字）',
      success: '发票已作废，核销已回退',
      fail: '作废失败，请稍后重试'
    },
    cancel: {
      title: '撤销登记',
      tip: '撤销后这张票号可以重新登记，请说明原因（不少于 5 个字）',
      success: '已撤销登记',
      fail: '撤销失败，请稍后重试'
    }
  };

  const askReason = async (key: 'void' | 'cancel') => {
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
        key === 'void'
          ? voidVendorInvoice(id, reason)
          : cancelVendorInvoice(id, reason),
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
