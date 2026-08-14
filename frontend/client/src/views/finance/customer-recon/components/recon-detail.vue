<template>
  <el-drawer
    :model-value="visible"
    :size="1000"
    :title="detail ? `对账单 ${detail.docNo}` : '对账单详情'"
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
          <el-descriptions-item label="对账周期">
            {{ formatDate(detail.periodStart) }} ~
            {{ formatDate(detail.periodEnd) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag
              :type="(RECON_STATUS_MAP[detail.status]?.type as any) || 'info'"
              size="small"
            >
              {{ detail.statusLabel }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="运单数">
            {{ detail.waybillCount }} 单 /
            {{ formatQuantity(detail.totalQuantity) }} 台
          </el-descriptions-item>
          <el-descriptions-item label="对账金额">
            <span class="num strong"
              >¥ {{ formatMoney(detail.plannedAmount) }}</span
            >
          </el-descriptions-item>
          <el-descriptions-item label="其中调整">
            <span class="num">{{ formatMoney(detail.adjustAmountTotal) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="已进结算">
            <span class="num"
              >¥ {{ formatMoney(detail.appliedAmountTotal) }}</span
            >
          </el-descriptions-item>
          <el-descriptions-item label="已收款">
            <span class="num"
              >¥ {{ formatMoney(detail.receivedAmountTotal) }}</span
            >
          </el-descriptions-item>
          <el-descriptions-item label="客户回签">
            <template v-if="detail.confirmedByCustomerAt">
              {{ detail.confirmedByCustomerName }}
              ·
              {{ formatDateTime(detail.confirmedByCustomerAt) }}
            </template>
            <span v-else class="muted">未回签</span>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="3">
            {{ detail.remark || '--' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-alert
          v-if="detail.actions.needAdjustApproval"
          type="warning"
          :closable="false"
          show-icon
          class="tip-alert"
          title="本单调整金额较大，需要业务主管审批后才能确认"
        />
        <el-alert
          v-else-if="detail.dirtyLineCount"
          type="warning"
          :closable="false"
          show-icon
          class="tip-alert"
          :title="`有 ${detail.dirtyLineCount} 行的业务数据变了，建议先重新核对`"
        />

        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="对账明细" name="lines">
            <div class="tab-toolbar">
              <el-button
                v-if="detail.actions.canEdit"
                size="small"
                type="primary"
                plain
                v-permission="'finance:cust-recon:add-waybill'"
                @click="addVisible = true"
              >
                补挂运单
              </el-button>
              <el-button
                v-if="detail.actions.canRecalc"
                size="small"
                v-permission="'finance:cust-recon:recalc'"
                @click="recalc"
              >
                回灌重算
              </el-button>
            </div>
            <el-table :data="detail.lines" size="small" max-height="360">
              <el-table-column
                prop="waybillNo"
                label="运单号"
                min-width="150"
              />
              <el-table-column
                prop="billingBaseLabel"
                label="计费基础"
                width="94"
                align="center"
              />
              <el-table-column label="数量" width="80" align="right">
                <template #default="{ row }">
                  {{ formatQuantity(row.quantity) }}
                </template>
              </el-table-column>
              <el-table-column label="单价" width="100" align="right">
                <template #default="{ row }">{{
                  formatMoney(row.unitPrice)
                }}</template>
              </el-table-column>
              <el-table-column label="行金额" width="110" align="right">
                <template #default="{ row }">
                  <span class="num">{{ formatMoney(row.amount) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="调整" width="110" align="right">
                <template #default="{ row }">
                  <span v-if="row.adjustAmount" class="num adjust">
                    {{ formatMoney(row.adjustAmount) }}
                  </span>
                  <span v-else>--</span>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="120" align="center">
                <template #default="{ row }">
                  <el-tooltip
                    v-if="row.reconDirty"
                    :content="row.dirtyReason || '业务数据已变更'"
                  >
                    <el-tag type="warning" size="small" effect="plain">
                      待重核
                    </el-tag>
                  </el-tooltip>
                  <span v-else class="muted">正常</span>
                </template>
              </el-table-column>
              <el-table-column
                v-if="detail.actions.canEdit"
                label="操作"
                width="120"
                align="center"
              >
                <template #default="{ row }">
                  <el-link
                    type="primary"
                    :underline="false"
                    v-permission="'finance:cust-recon:adjust-line'"
                    @click="openAdjust(row)"
                  >
                    调整
                  </el-link>
                  <el-divider direction="vertical" />
                  <el-link
                    type="danger"
                    :underline="false"
                    v-permission="'finance:cust-recon:remove-waybill'"
                    @click="removeLine(row)"
                  >
                    移除
                  </el-link>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane name="diffs">
            <template #label>
              一致性核对
              <el-badge
                v-if="detail.diffOpenCount"
                :value="detail.diffOpenCount"
                class="tab-badge"
              />
            </template>
            <div class="tab-toolbar">
              <el-button
                v-if="detail.actions.canCheck"
                size="small"
                type="primary"
                plain
                v-permission="'finance:cust-recon:check'"
                @click="check"
              >
                重新核对
              </el-button>
              <span v-if="checkedAt" class="muted">
                上次核对 {{ formatDateTime(checkedAt) }}
              </span>
            </div>
            <el-table :data="diffs" size="small" max-height="360">
              <el-table-column
                prop="diffTypeLabel"
                label="差异类型"
                width="110"
              />
              <el-table-column label="严重度" width="90" align="center">
                <template #default="{ row }">
                  <el-tag
                    :type="row.severity === 2 ? 'danger' : 'warning'"
                    size="small"
                    effect="plain"
                  >
                    {{ row.severityLabel }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="bizDocNo"
                label="业务单据"
                min-width="140"
              />
              <el-table-column label="快照 → 当前" min-width="180">
                <template #default="{ row }">
                  {{ row.expectedValue || '--' }} →
                  {{ row.actualValue || '--' }}
                </template>
              </el-table-column>
              <el-table-column label="差额" width="110" align="right">
                <template #default="{ row }">
                  <span class="num">{{ formatMoney(row.diffAmount) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="处置" width="130" align="center">
                <template #default="{ row }">
                  <el-tag
                    v-if="row.status !== 0"
                    type="success"
                    size="small"
                    effect="plain"
                  >
                    {{ row.statusLabel }}
                  </el-tag>
                  <el-link
                    v-else
                    type="primary"
                    :underline="false"
                    @click="openResolve(row)"
                  >
                    去处置
                  </el-link>
                </template>
              </el-table-column>
              <template #empty>
                <div class="empty-tip">暂无差异，本单与业务数据一致</div>
              </template>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="操作记录" name="events">
            <el-timeline v-if="events.length" class="event-line">
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
          v-if="detail.actions.needAdjustApproval"
          type="warning"
          v-permission="'finance:cust-recon:adjust-line'"
          @click="approveAdjust"
        >
          审批大额调整
        </el-button>
        <el-button
          v-if="detail.actions.canConfirm"
          type="primary"
          v-permission="'finance:cust-recon:confirm'"
          @click="confirm(false)"
        >
          确认对账
        </el-button>
        <el-button
          v-if="detail.actions.canForceConfirm"
          type="danger"
          plain
          v-permission="'finance:cust-recon:force-confirm'"
          @click="confirm(true)"
        >
          带差异强制确认
        </el-button>
        <el-button
          v-if="detail.actions.canCustomerSign && !detail.confirmedByCustomerAt"
          type="primary"
          plain
          v-permission="'finance:cust-recon:customer-sign'"
          @click="signVisible = true"
        >
          登记回签
        </el-button>
        <el-button
          v-if="detail.actions.canWithdraw"
          v-permission="'finance:cust-recon:withdraw'"
          @click="askReason('withdraw')"
        >
          退回草稿
        </el-button>
        <el-button
          v-if="detail.actions.canUnlockSettled"
          v-permission="'finance:cust-recon:unlock'"
          @click="askReason('unlock')"
        >
          解锁已结清
        </el-button>
        <el-button
          v-if="detail.actions.canCancel"
          type="danger"
          plain
          v-permission="'finance:cust-recon:cancel'"
          @click="askReason('cancel')"
        >
          撤销对账单
        </el-button>
        <el-button @click="updateVisible(false)">关闭</el-button>
      </div>
    </template>

    <recon-add-waybills
      v-if="detail"
      v-model:visible="addVisible"
      :recon-id="detail.id"
      :customer-id="detail.customerId"
      :period-start="detail.periodStart"
      :period-end="detail.periodEnd"
      @done="reloadAll"
    />

    <recon-line-adjust
      v-if="detail"
      v-model:visible="adjustVisible"
      :recon-id="detail.id"
      :line="adjustLine"
      @done="reloadAll"
    />

    <recon-sign
      v-if="detail"
      v-model:visible="signVisible"
      :recon-id="detail.id"
      @done="reloadAll"
    />

    <recon-diff-resolve
      v-model:visible="resolveVisible"
      :diff="resolveDiff"
      @done="reloadAll"
    />
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import ReconAddWaybills from './recon-add-waybills.vue';
  import ReconLineAdjust from './recon-line-adjust.vue';
  import ReconSign from './recon-sign.vue';
  import ReconDiffResolve from '../../components/recon-diff-resolve.vue';
  import {
    approveReconAdjust,
    cancelRecon,
    checkRecon,
    confirmRecon,
    getRecon,
    listReconDiffs,
    listReconEvents,
    recalcRecon,
    removeReconLine,
    unlockSettledRecon,
    withdrawRecon
  } from '@/api/finance/customer-recon';
  import type {
    FinanceDocEvent,
    ReconDetail as ReconDetailModel,
    ReconDiff,
    ReconLine
  } from '@/api/finance/customer-recon/model';
  import { formatDate, formatDateTime } from '@/utils/date-util';
  import {
    EVENT_TYPE_LABELS,
    formatMoney,
    formatQuantity,
    RECON_STATUS_MAP
  } from '../../status-config';

  const props = defineProps<{ visible: boolean; reconId?: number | null }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'changed'): void;
  }>();

  const loading = ref(false);
  const activeTab = ref('lines');
  const detail = ref<ReconDetailModel | null>(null);
  const diffs = ref<ReconDiff[]>([]);
  const events = ref<FinanceDocEvent[]>([]);
  const checkedAt = ref<string | undefined>(void 0);

  const addVisible = ref(false);
  const adjustVisible = ref(false);
  const adjustLine = ref<ReconLine | null>(null);
  const signVisible = ref(false);
  const resolveVisible = ref(false);
  const resolveDiff = ref<ReconDiff | null>(null);

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const load = async () => {
    if (!props.reconId) return;
    loading.value = true;
    activeTab.value = 'lines';
    try {
      const [d, df, ev] = await Promise.all([
        getRecon(props.reconId),
        listReconDiffs(props.reconId),
        listReconEvents(props.reconId)
      ]);
      detail.value = d ?? null;
      diffs.value = df;
      events.value = ev;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '打开失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  /** 单据被改动后：刷新抽屉自身 + 通知列表 */
  const reloadAll = async () => {
    await load();
    emit('changed');
  };

  const openAdjust = (row: ReconLine) => {
    adjustLine.value = row;
    adjustVisible.value = true;
  };

  const openResolve = (row: ReconDiff) => {
    resolveDiff.value = row;
    resolveVisible.value = true;
  };

  const run = async (
    action: () => Promise<unknown>,
    { loadingText, successText, failText }: Record<string, string>
  ) => {
    const l = EleMessage.loading({ message: loadingText, plain: true });
    try {
      await action();
      l.close();
      EleMessage.success({ message: successText, plain: true });
      await reloadAll();
    } catch (e: unknown) {
      l.close();
      const msg = (e as { message?: string }).message || failText;
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const removeLine = async (row: ReconLine) => {
    try {
      await ElMessageBox.confirm(
        `确定把运单「${row.waybillNo}」从本单移除？`,
        '移除对账明细',
        { type: 'warning', confirmButtonText: '移除', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    if (!detail.value) return;
    await run(() => removeReconLine(detail.value!.id, row.id), {
      loadingText: '正在移除，请稍候…',
      successText: '已移除该运单',
      failText: '移除失败，请稍后重试'
    });
  };

  const recalc = async () => {
    if (!detail.value) return;
    await run(() => recalcRecon(detail.value!.id, true), {
      loadingText: '正在按业务数据重算，请稍候…',
      successText: '已按最新业务数据重算',
      failText: '重算失败，请稍后重试'
    });
  };

  const check = async () => {
    if (!detail.value) return;
    const l = EleMessage.loading({
      message: '正在核对，请稍候…',
      plain: true
    });
    try {
      const report = await checkRecon(detail.value.id);
      l.close();
      checkedAt.value = report?.checkedAt;
      const blocking = report?.blockingCount ?? 0;
      const warning = report?.warningCount ?? 0;
      if (!blocking && !warning) {
        EleMessage.success({
          message: '核对通过，与业务数据一致',
          plain: true
        });
      } else {
        EleMessage.warning({
          message: `核对出 ${blocking} 条阻塞差异、${warning} 条提示差异，请在「一致性核对」处置`,
          plain: true
        });
        activeTab.value = 'diffs';
      }
      await reloadAll();
    } catch (e: unknown) {
      l.close();
      const msg = (e as { message?: string }).message || '核对失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const approveAdjust = async () => {
    if (!detail.value) return;
    try {
      await ElMessageBox.confirm(
        '确认这些调整金额都已与客户谈定？审批后即可确认对账。',
        '审批大额调整',
        {
          type: 'warning',
          confirmButtonText: '审批通过',
          cancelButtonText: '取消'
        }
      );
    } catch {
      return;
    }
    await run(() => approveReconAdjust(detail.value!.id), {
      loadingText: '正在审批，请稍候…',
      successText: '大额调整已审批通过',
      failText: '审批失败，请稍后重试'
    });
  };

  const confirm = async (force: boolean) => {
    if (!detail.value) return;
    let reason: string | undefined;
    if (force) {
      try {
        const { value } = await ElMessageBox.prompt(
          '本单还有未处置差异，强制确认会留下记录。请说明原因（不少于 10 个字）',
          '带差异强制确认',
          {
            confirmButtonText: '强制确认',
            cancelButtonText: '取消',
            inputValidator: (v: string) =>
              (v || '').trim().length >= 10 || '原因不少于 10 个字'
          }
        );
        reason = (value || '').trim();
      } catch {
        return;
      }
    } else {
      try {
        await ElMessageBox.confirm(
          '确认后客户方可回签，运单将不能再改动。',
          '确认对账',
          {
            type: 'warning',
            confirmButtonText: '确认',
            cancelButtonText: '再看看'
          }
        );
      } catch {
        return;
      }
    }
    await run(() => confirmRecon(detail.value!.id, reason), {
      loadingText: '正在确认对账单，请稍候…',
      successText: '对账单已确认',
      failText: '确认失败，请稍后重试'
    });
  };

  const REASON_ACTIONS: Record<
    string,
    { title: string; tip: string; success: string; fail: string }
  > = {
    withdraw: {
      title: '退回草稿',
      tip: '退回后可继续调整明细，请说明原因（不少于 5 个字）',
      success: '已退回草稿，可继续修改',
      fail: '退回失败，请稍后重试'
    },
    cancel: {
      title: '撤销对账单',
      tip: '撤销后本单不再生效，运单会回到可对账池。请说明原因（不少于 5 个字）',
      success: '对账单已撤销',
      fail: '撤销失败，请稍后重试'
    },
    unlock: {
      title: '解锁已结清',
      tip: '解锁后本单回到已确认，可再调整。请说明原因（不少于 5 个字）',
      success: '已解锁，可继续调整',
      fail: '解锁失败，请稍后重试'
    }
  };

  const askReason = async (key: 'withdraw' | 'cancel' | 'unlock') => {
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
    const call =
      key === 'withdraw'
        ? () => withdrawRecon(id, reason)
        : key === 'cancel'
          ? () => cancelRecon(id, reason)
          : () => unlockSettledRecon(id, reason);
    await run(call, {
      loadingText: `正在${cfg.title}，请稍候…`,
      successText: cfg.success,
      failText: cfg.fail
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

  .adjust {
    color: var(--el-color-warning);
  }

  .muted {
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

  .tab-badge {
    margin-left: 6px;
  }

  .empty-tip {
    padding: 24px 0;
    color: var(--el-text-color-secondary);
    text-align: center;
  }

  .event-line {
    padding-left: 4px;
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
