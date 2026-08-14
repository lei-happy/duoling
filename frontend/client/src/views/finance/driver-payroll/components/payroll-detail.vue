<template>
  <el-drawer
    :model-value="visible"
    :size="1000"
    :title="detail ? `工资单 ${detail.docNo}` : '工资单详情'"
    destroy-on-close
    @update:model-value="updateVisible"
    @open="load"
  >
    <div v-loading="loading">
      <template v-if="detail">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="司机">
            {{ detail.driverName || '--' }}
            <span v-if="detail.driverPhone" class="muted">
              {{ detail.driverPhone }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag
              :type="(PAYROLL_STATUS_MAP[detail.status]?.type as any) || 'info'"
              size="small"
            >
              {{ detail.statusLabel }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="工资周期">
            {{ formatDate(detail.periodStart) }} ~
            {{ formatDate(detail.periodEnd) }}
          </el-descriptions-item>
          <el-descriptions-item label="工资模式">
            {{ detail.payrollModelLabel }} · {{ detail.periodTypeLabel }}
          </el-descriptions-item>
          <el-descriptions-item label="任务数">
            {{ detail.taskCount }} 个 / {{ detail.totalSignedQuantity }} 台
          </el-descriptions-item>
          <el-descriptions-item label="任务提成">
            <span class="num">
              ¥ {{ formatMoney(detail.totalCommissionAmount) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="应发合计">
            <span class="num strong"
              >¥ {{ formatMoney(detail.grossAmount) }}</span
            >
          </el-descriptions-item>
          <el-descriptions-item label="扣减 / 抵账">
            <span class="num deduct">
              -{{ formatMoney(detail.totalDeductionAmount) }}
            </span>
            <span class="num offset">
              抵 {{ formatMoney(detail.totalPrepaidOffsetAmount) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="实发金额">
            <span class="num strong" :class="{ danger: detail.netAmount < 0 }">
              ¥ {{ formatMoney(detail.netAmount) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="发薪账户">
            {{
              [
                detail.accountTypeLabel,
                detail.accountNameSnapshot,
                detail.accountNoMasked
              ]
                .filter(Boolean)
                .join(' · ') || '--'
            }}
          </el-descriptions-item>
          <el-descriptions-item label="发放时间">
            {{ formatDateTime(detail.paidAt) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="发放方式">
            {{ detail.payMethodLabel || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="3">
            {{ detail.remark || '--' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-alert
          v-if="detail.netAmount < 0"
          type="warning"
          :closable="false"
          show-icon
          class="tip-alert"
          title="实发为负数：预支与扣减已超过应发，建议减少本期抵账额度，余额留到下期继续抵。"
        />
        <el-alert
          v-else-if="detail.actions.needAdjustApproval"
          type="warning"
          :closable="false"
          show-icon
          class="tip-alert"
          title="本单调整金额较大，需要主管审批调整后才能提交。"
        />

        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="任务提成" name="tasks">
            <div v-if="detail.actions.canEdit" class="tab-toolbar">
              <el-button
                size="small"
                type="primary"
                plain
                v-permission="'finance:driver-payroll:add-task'"
                @click="addTaskVisible = true"
              >
                补挂任务
              </el-button>
            </div>
            <el-table :data="detail.tasks" size="small" max-height="300">
              <el-table-column prop="taskNo" label="任务号" min-width="150" />
              <el-table-column prop="plateNumber" label="车牌" width="105" />
              <el-table-column label="交车时间" width="150" align="center">
                <template #default="{ row }">
                  {{ formatDate(row.signedAt) || '--' }}
                </template>
              </el-table-column>
              <el-table-column label="计件" width="130" align="right">
                <template #default="{ row }">
                  {{ formatQuantity(row.quantity) }}
                  {{ row.billingBaseLabel || '' }}
                  × {{ formatMoney(row.unitPrice) }}
                </template>
              </el-table-column>
              <el-table-column label="提成金额" width="120" align="right">
                <template #default="{ row }">
                  <span class="num">
                    ¥ {{ formatMoney(row.commissionAmount) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="调整" width="110" align="right">
                <template #default="{ row }">
                  <el-tooltip
                    v-if="row.adjustAmount"
                    :content="row.adjustReason || '未填原因'"
                    placement="top"
                  >
                    <span class="num adjust">
                      {{ formatMoney(row.adjustAmount) }}
                    </span>
                  </el-tooltip>
                  <span v-else class="muted">--</span>
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
                    v-permission="'finance:driver-payroll:edit'"
                    @click="openAdjust(row)"
                  >
                    调整
                  </el-link>
                  <el-divider direction="vertical" />
                  <el-link
                    type="danger"
                    :underline="false"
                    v-permission="'finance:driver-payroll:edit'"
                    @click="removeTask(row.id, row.taskNo)"
                  >
                    移除
                  </el-link>
                </template>
              </el-table-column>
              <template #empty>
                <div class="empty-tip">
                  还没有任务提成。月薪固定的司机可以只填工资项。
                </div>
              </template>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="工资项" name="items">
            <div v-if="detail.actions.canEdit" class="tab-toolbar">
              <el-button
                size="small"
                type="primary"
                plain
                v-permission="'finance:driver-payroll:edit-item'"
                @click="openItem(null)"
              >
                新增工资项
              </el-button>
              <span class="toolbar-tip">
                油卡与借款抵扣由系统按预支记录自动生成，不能手工改。
              </span>
            </div>
            <el-table :data="detail.items" size="small" max-height="300">
              <el-table-column label="项目" min-width="150">
                <template #default="{ row }">
                  {{ row.itemName || row.itemType }}
                  <el-tag
                    v-if="row.isSystem"
                    size="small"
                    type="info"
                    effect="plain"
                    class="sys-tag"
                  >
                    系统
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="方向" width="100" align="center">
                <template #default="{ row }">
                  <el-tag
                    :type="
                      (PAYROLL_ITEM_CATEGORY_MAP[row.category]?.type as any) ||
                      'info'
                    "
                    size="small"
                    effect="plain"
                  >
                    {{ row.categoryLabel }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="金额" width="130" align="right">
                <template #default="{ row }">
                  <span class="num" :class="itemClass(row.category)">
                    {{ row.category === 1 ? '' : '-' }}
                    {{ formatMoney(row.amount) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column
                prop="formula"
                label="计算说明"
                min-width="160"
              />
              <el-table-column
                v-if="detail.actions.canEdit"
                label="操作"
                width="120"
                align="center"
              >
                <template #default="{ row }">
                  <template v-if="!row.isSystem">
                    <el-link
                      type="primary"
                      :underline="false"
                      v-permission="'finance:driver-payroll:edit-item'"
                      @click="openItem(row)"
                    >
                      修改
                    </el-link>
                    <el-divider direction="vertical" />
                    <el-link
                      type="danger"
                      :underline="false"
                      v-permission="'finance:driver-payroll:edit-item'"
                      @click="removeItem(row.id, row.itemName || row.itemType)"
                    >
                      删除
                    </el-link>
                  </template>
                  <span v-else class="muted">--</span>
                </template>
              </el-table-column>
              <template #empty>
                <div class="empty-tip">还没有工资项</div>
              </template>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="工资条" name="payslip">
            <div v-if="payslip" class="payslip">
              <div class="payslip-head">
                {{ payslip.driverName }} ·
                {{ formatDate(payslip.periodStart) }} ~
                {{ formatDate(payslip.periodEnd) }}
              </div>
              <div class="payslip-section">
                <div class="section-title">应发</div>
                <div
                  v-for="(l, i) in payslip.additions"
                  :key="`a${i}`"
                  class="payslip-line"
                >
                  <span>{{ l.itemName || l.itemType }}</span>
                  <span v-if="l.formula" class="formula">{{ l.formula }}</span>
                  <span class="num">{{ formatMoney(l.amount) }}</span>
                </div>
                <div class="payslip-line total">
                  <span>应发合计</span>
                  <span class="num">{{
                    formatMoney(payslip.grossAmount)
                  }}</span>
                </div>
              </div>
              <div v-if="payslip.deductions.length" class="payslip-section">
                <div class="section-title">扣减</div>
                <div
                  v-for="(l, i) in payslip.deductions"
                  :key="`d${i}`"
                  class="payslip-line"
                >
                  <span>{{ l.itemName || l.itemType }}</span>
                  <span v-if="l.formula" class="formula">{{ l.formula }}</span>
                  <span class="num deduct">-{{ formatMoney(l.amount) }}</span>
                </div>
              </div>
              <div v-if="payslip.offsets.length" class="payslip-section">
                <div class="section-title">抵账</div>
                <div
                  v-for="(l, i) in payslip.offsets"
                  :key="`o${i}`"
                  class="payslip-line"
                >
                  <span>{{ l.itemName || l.itemType }}</span>
                  <span v-if="l.formula" class="formula">{{ l.formula }}</span>
                  <span class="num offset">-{{ formatMoney(l.amount) }}</span>
                </div>
              </div>
              <div class="payslip-net">
                实发 ¥ {{ formatMoney(payslip.netAmount) }}
              </div>
            </div>
            <div v-else class="empty-tip">工资条生成中，请稍候…</div>
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
          v-if="detail.actions.needAdjustApproval"
          type="warning"
          v-permission="'finance:driver-payroll:approve'"
          @click="approveAdjust"
        >
          审批调整
        </el-button>
        <el-button
          v-if="detail.actions.canSubmit"
          type="warning"
          v-permission="'finance:driver-payroll:submit'"
          @click="submit"
        >
          提交审批
        </el-button>
        <el-button
          v-if="detail.actions.canApprove"
          type="primary"
          v-permission="'finance:driver-payroll:approve'"
          @click="approve"
        >
          审批通过
        </el-button>
        <el-button
          v-if="detail.actions.canReject"
          type="danger"
          plain
          v-permission="'finance:driver-payroll:reject'"
          @click="askReason('reject')"
        >
          审批驳回
        </el-button>
        <el-button
          v-if="detail.actions.canPay"
          type="primary"
          v-permission="'finance:driver-payroll:pay'"
          @click="payVisible = true"
        >
          登记发放
        </el-button>
        <el-button
          v-if="detail.actions.canWithdraw"
          v-permission="'finance:driver-payroll:withdraw'"
          @click="askReason('withdraw')"
        >
          退回草稿
        </el-button>
        <el-button
          v-if="detail.actions.canCancelPayment"
          v-permission="'finance:driver-payroll:cancel-payment'"
          @click="askReason('cancelPay')"
        >
          撤销发放
        </el-button>
        <el-button
          v-if="detail.actions.canCancel"
          type="danger"
          plain
          v-permission="'finance:driver-payroll:cancel'"
          @click="askReason('cancel')"
        >
          撤销工资单
        </el-button>
        <el-button @click="updateVisible(false)">关闭</el-button>
      </div>
    </template>

    <payroll-add-tasks
      v-if="detail"
      v-model:visible="addTaskVisible"
      :payroll-id="detail.id"
      :driver-id="detail.driverId"
      :period-start="detail.periodStart"
      :period-end="detail.periodEnd"
      :default-unit-price="defaultUnitPrice"
      @done="reloadAll"
    />

    <payroll-task-adjust
      v-if="detail"
      v-model:visible="adjustVisible"
      :payroll-id="detail.id"
      :link="adjustLink"
      @done="reloadAll"
    />

    <payroll-item-edit
      v-if="detail"
      v-model:visible="itemVisible"
      :payroll-id="detail.id"
      :item="editingItem"
      @done="reloadAll"
    />

    <payroll-pay
      v-if="detail"
      v-model:visible="payVisible"
      :payroll-id="detail.id"
      @done="reloadAll"
    />
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import PayrollAddTasks from './payroll-add-tasks.vue';
  import PayrollItemEdit from './payroll-item-edit.vue';
  import PayrollPay from './payroll-pay.vue';
  import PayrollTaskAdjust from './payroll-task-adjust.vue';
  import {
    approvePayroll,
    approvePayrollAdjust,
    cancelPayroll,
    cancelPayrollPay,
    getPayroll,
    getPayslip,
    listPayrollEvents,
    rejectPayroll,
    removePayrollItem,
    removePayrollTask,
    submitPayroll,
    withdrawPayroll
  } from '@/api/finance/driver-payroll';
  import type {
    FinanceDocEvent,
    PayrollDetail,
    PayrollItem,
    PayrollTaskLink,
    Payslip
  } from '@/api/finance/driver-payroll/model';
  import { formatDate, formatDateTime } from '@/utils/date-util';
  import {
    EVENT_TYPE_LABELS,
    formatMoney,
    formatQuantity,
    PAYROLL_ITEM_CATEGORY_MAP,
    PAYROLL_STATUS_MAP
  } from '../../status-config';

  const props = defineProps<{ visible: boolean; payrollId?: number | null }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'changed'): void;
  }>();

  const loading = ref(false);
  const activeTab = ref('tasks');
  const detail = ref<PayrollDetail | null>(null);
  const payslip = ref<Payslip | null>(null);
  const events = ref<FinanceDocEvent[]>([]);

  const addTaskVisible = ref(false);
  const adjustVisible = ref(false);
  const adjustLink = ref<PayrollTaskLink | null>(null);
  const itemVisible = ref(false);
  const editingItem = ref<PayrollItem | null>(null);
  const payVisible = ref(false);

  const updateVisible = (v: boolean) => emit('update:visible', v);

  /** 补挂时沿用已有行的单价，省得每次重填 */
  const defaultUnitPrice = computed(
    () => detail.value?.tasks?.[0]?.unitPrice ?? void 0
  );

  const itemClass = (category: number) =>
    category === 2 ? 'deduct' : category === 3 ? 'offset' : '';

  const load = async () => {
    if (!props.payrollId) return;
    loading.value = true;
    activeTab.value = 'tasks';
    try {
      const [d, slip, ev] = await Promise.all([
        getPayroll(props.payrollId),
        getPayslip(props.payrollId).catch(() => null),
        listPayrollEvents(props.payrollId)
      ]);
      detail.value = d ?? null;
      payslip.value = slip ?? null;
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

  const openAdjust = (link: PayrollTaskLink) => {
    adjustLink.value = link;
    adjustVisible.value = true;
  };

  const openItem = (item: PayrollItem | null) => {
    editingItem.value = item;
    itemVisible.value = true;
  };

  const removeTask = async (linkId: number, taskNo?: string) => {
    if (!detail.value) return;
    try {
      await ElMessageBox.confirm(
        `移除任务「${taskNo || linkId}」后，这一趟的提成不再计入本单。`,
        '移除任务',
        { type: 'warning', confirmButtonText: '移除', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    await run(() => removePayrollTask(detail.value!.id, linkId), {
      loading: '正在移除任务，请稍候…',
      success: '已移除任务',
      fail: '移除失败，请稍后重试'
    });
  };

  const removeItem = async (itemId: number, name: string) => {
    if (!detail.value) return;
    try {
      await ElMessageBox.confirm(`确认删除工资项「${name}」？`, '删除工资项', {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      });
    } catch {
      return;
    }
    await run(() => removePayrollItem(detail.value!.id, itemId), {
      loading: '正在删除工资项，请稍候…',
      success: '已删除工资项',
      fail: '删除失败，请稍后重试'
    });
  };

  const approveAdjust = async () => {
    if (!detail.value) return;
    await run(() => approvePayrollAdjust(detail.value!.id), {
      loading: '正在审批调整，请稍候…',
      success: '调整已审批，可以提交了',
      fail: '审批失败，请稍后重试'
    });
  };

  const submit = async () => {
    if (!detail.value) return;
    await run(() => submitPayroll(detail.value!.id), {
      loading: '正在提交审批，请稍候…',
      success: '已提交审批',
      fail: '提交失败，请稍后重试'
    });
  };

  const approve = async () => {
    if (!detail.value) return;
    try {
      await ElMessageBox.confirm('通过后即可发放工资。', '审批通过', {
        type: 'warning',
        confirmButtonText: '通过',
        cancelButtonText: '取消'
      });
    } catch {
      return;
    }
    await run(() => approvePayroll(detail.value!.id), {
      loading: '正在审批，请稍候…',
      success: '已审批通过，可安排发放',
      fail: '审批失败，请稍后重试'
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
      title: '撤销发放',
      tip: '撤销后任务的发薪标记会回退，请说明原因（不少于 5 个字）',
      success: '已撤销发放',
      fail: '撤销失败，请稍后重试'
    },
    cancel: {
      title: '撤销工资单',
      tip: '撤销后任务回到可计提成池，请说明原因（不少于 5 个字）',
      success: '工资单已撤销',
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
      reject: () => rejectPayroll(id, reason),
      withdraw: () => withdrawPayroll(id, reason),
      cancelPay: () => cancelPayrollPay(id, reason),
      cancel: () => cancelPayroll(id, reason)
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

  .deduct {
    color: var(--el-color-danger);
  }

  .offset {
    margin-left: 8px;
    color: var(--el-color-warning);
  }

  .adjust {
    color: var(--el-color-warning);
  }

  .danger {
    color: var(--el-color-danger);
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

  .sys-tag {
    margin-left: 6px;
  }

  .empty-tip {
    padding: 24px 0;
    color: var(--el-text-color-secondary);
    text-align: center;
  }

  .event-title {
    font-weight: 500;
  }

  .payslip {
    max-width: 560px;
    padding: 16px 20px;
    border: 1px solid var(--el-border-color-light);
    border-radius: 6px;
  }

  .payslip-head {
    padding-bottom: 10px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    font-weight: 600;
  }

  .payslip-section {
    margin-top: 12px;
  }

  .section-title {
    margin-bottom: 6px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .payslip-line {
    display: flex;
    align-items: baseline;
    gap: 8px;
    padding: 3px 0;

    .num {
      margin-left: auto;
    }
  }

  .formula {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .total {
    border-top: 1px dashed var(--el-border-color-light);
    font-weight: 600;
  }

  .payslip-net {
    margin-top: 14px;
    padding-top: 10px;
    border-top: 1px solid var(--el-border-color-lighter);
    font-size: 16px;
    font-weight: 600;
    text-align: right;
    font-variant-numeric: tabular-nums;
  }

  .drawer-footer {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-end;
  }
</style>
