<template>
  <el-drawer
    :model-value="visible"
    title="任务单详情"
    direction="rtl"
    size="1000px"
    :destroy-on-close="true"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
  >
    <div v-loading="loading" class="task-detail">
      <template v-if="task">
        <!-- 头部摘要 -->
        <div class="task-detail__header">
          <div>
            <div class="task-detail__no">
              {{ task.taskNo }}
              <el-tag
                :type="(TASK_STATUS_MAP[task.status || 0]?.type as any) || 'info'"
                style="margin-left: 8px"
                size="small"
              >
                {{ TASK_STATUS_MAP[task.status || 0]?.label }}
              </el-tag>
              <el-tag
                :type="(CARRIER_TYPE_MAP[task.carrierType || 1]?.type as any) || 'info'"
                style="margin-left: 4px"
                size="small"
                effect="plain"
              >
                {{ CARRIER_TYPE_MAP[task.carrierType || 1]?.label }}
              </el-tag>
            </div>
            <div class="task-detail__name">{{ task.taskName || '--' }}</div>
          </div>
          <div class="task-detail__actions">
            <el-button
              v-if="primaryAction"
              :type="primaryAction.buttonType"
              size="small"
              v-permission="primaryAction.permission"
              @click="triggerAction(primaryAction)"
            >
              {{ primaryAction.label }}
            </el-button>
            <el-button
              v-if="showPlanRoute"
              :type="planRouteAction.buttonType"
              size="small"
              plain
              v-permission="planRouteAction.permission"
              @click="triggerAction(planRouteAction)"
            >
              {{ planRouteAction.label
              }}<span
                v-if="(task?.segmentCount ?? 0) === 0"
                style="margin-left: 4px"
                >·未规划</span
              >
            </el-button>
            <el-button
              v-for="act in secondaryActions"
              :key="act.key"
              :type="act.buttonType"
              size="small"
              plain
              v-permission="act.permission"
              @click="triggerAction(act)"
            >
              {{ act.label }}
            </el-button>
            <el-button
              type="success"
              size="small"
              :icon="Plus"
              v-permission="'operation:task-finance:add'"
              @click="openFinanceEdit(null)"
            >
              新建费用单
            </el-button>
          </div>
        </div>

        <!-- 状态时间轴 -->
        <el-divider content-position="left">状态时间轴</el-divider>
        <el-steps
          :active="statusStep"
          align-center
          finish-status="success"
          class="task-detail__steps"
        >
          <el-step title="待分配" />
          <el-step title="待派车" />
          <el-step title="已派车" />
          <el-step title="已装车" />
          <el-step title="在途" />
          <el-step title="已到达" />
          <el-step title="已签收" />
          <el-step title="已结算" />
        </el-steps>

        <!-- 基础信息 -->
        <el-divider content-position="left">基础信息</el-divider>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="承运资源">
            <div v-if="task.carrierType === 2">
              {{ task.carrierName || '--' }}
            </div>
            <div v-else>
              {{ task.mainDriverName || '--' }}
              <span v-if="task.plateNumber" class="ele-text-secondary">
                / {{ task.plateNumber }}
              </span>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="主驾电话">
            {{ task.mainDriverPhone || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="挂车">
            {{ task.trailerPlateNumber || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="计划装车">
            {{ formatDateTime(task.plannedLoadTime) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="实际装车">
            {{ formatDateTime(task.actualLoadTime) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="计划到达">
            {{ formatDateTime(task.plannedArriveTime) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="实际到达">
            {{ formatDateTime(task.actualArriveTime) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="承运成本">
            {{ formatAmount(task.carrierCostAmount) }}
          </el-descriptions-item>
          <el-descriptions-item label="已预付/补款/结算">
            <span style="font-variant-numeric: tabular-nums">
              {{ formatAmount(task.prepaidAmount) }} /
              {{ formatAmount(task.supplementAmount) }} /
              {{ formatAmount(task.settledAmount) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="3">
            {{ task.remark || '--' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- Tab: 分段进度 / 挂接货物 / 费用单 -->
        <el-divider />
        <el-tabs v-model="activeTab" type="border-card">
          <el-tab-pane name="segments" :label="`分段进度 (${segments.length})`">
            <el-table :data="segments" border size="small">
              <el-table-column label="段" prop="segmentNo" width="60" align="center" />
              <el-table-column label="起点" prop="fromLocation" min-width="180" />
              <el-table-column label="终点" prop="toLocation" min-width="180" />
              <el-table-column label="公里数" prop="mileage" width="100" align="right" />
              <el-table-column label="计划装车" min-width="160">
                <template #default="{ row }">
                  {{ formatDateTime(row.plannedLoadTime) || '--' }}
                </template>
              </el-table-column>
              <el-table-column label="实际装车" min-width="160">
                <template #default="{ row }">
                  {{ formatDateTime(row.actualLoadTime) || '--' }}
                </template>
              </el-table-column>
              <el-table-column label="实际到达" min-width="160">
                <template #default="{ row }">
                  {{ formatDateTime(row.actualArriveTime) || '--' }}
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag size="small">
                    {{ SEGMENT_STATUS_LABEL[row.status] || row.status }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane name="cargoes" :label="`挂接货物 (${items.length})`">
            <el-table :data="items" border size="small">
              <el-table-column label="运单号" prop="waybillNo" min-width="140" />
              <el-table-column label="客户" prop="customerName" min-width="120" />
              <el-table-column label="品牌/车型" min-width="160">
                <template #default="{ row }">
                  {{ row.vehicleBrand || '--' }} / {{ row.vehicleModel || '--' }}
                </template>
              </el-table-column>
              <el-table-column label="台数" prop="quantity" width="80" align="center" />
              <el-table-column label="归属段" prop="segmentId" width="80" align="center">
                <template #default="{ row }">
                  {{ row.segmentId ?? '--' }}
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag size="small">
                    {{ ITEM_STATUS_LABEL[row.status] || row.status }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane name="finance" :label="`费用单 (${financeDocs.length})`">
            <el-table :data="financeDocs" border size="small">
              <el-table-column label="单据号" prop="docNo" min-width="160" />
              <el-table-column label="类型" width="90" align="center">
                <template #default="{ row }">
                  <el-tag size="small" :type="DOC_TYPE_LABEL[row.docType]?.type as any">
                    {{ DOC_TYPE_LABEL[row.docType]?.label }}
                  </el-tag>
                  <el-tag
                    v-if="row.isFinal === 1"
                    type="danger"
                    size="small"
                    effect="plain"
                    style="margin-left: 4px"
                  >
                    终结
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="收款人" prop="payeeName" min-width="140" />
              <el-table-column label="计划金额" prop="plannedAmount" width="120" align="right" />
              <el-table-column label="实际金额" prop="actualAmount" width="120" align="right">
                <template #default="{ row }">
                  {{ formatAmount(row.actualAmount) }}
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag size="small" :type="FIN_STATUS_LABEL[row.status]?.type as any">
                    {{ FIN_STATUS_LABEL[row.status]?.label }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="计划支付时间" min-width="160">
                <template #default="{ row }">
                  {{ formatDateTime(row.plannedPayTime) || '--' }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" align="center">
                <template #default="{ row }">
                  <el-link type="primary" :underline="false" @click="openFinanceEdit(row)">
                    详情/编辑
                  </el-link>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </template>
    </div>

    <!-- 语义化动作弹窗 -->
    <action-assign-carrier
      v-model:visible="actionVisible['assign-carrier']"
      :task="task"
      @done="onActionDone"
    />
    <action-dispatch
      v-model:visible="actionVisible.dispatch"
      :task="task"
      @done="onDispatchDone"
    />
    <action-plan-route
      v-model:visible="actionVisible['plan-route']"
      :task="task"
      @done="onActionDone"
    />
    <action-confirm-load
      v-model:visible="actionVisible['confirm-load']"
      :tasks="task ? [task] : []"
      @done="onActionDone"
    />
    <action-confirm-arrive
      v-model:visible="actionVisible['confirm-arrive']"
      :tasks="task ? [task] : []"
      @done="onActionDone"
    />
    <action-confirm-sign
      v-model:visible="actionVisible['confirm-sign']"
      :tasks="task ? [task] : []"
      @done="onActionDone"
    />

    <!-- 费用单创建/编辑 -->
    <finance-edit
      v-if="task"
      v-model:visible="financeEditVisible"
      :task="task"
      :doc-id="editingFinanceId"
      :init-doc-type="financeInitDocType"
      :init-is-final="financeInitIsFinal"
      @done="onFinanceDone"
    />
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { Plus } from '@element-plus/icons-vue';
  import {
    getTask,
    listTaskFinanceSummary,
    listTaskSegments,
    listTaskWaybillItems,
    updateTaskStatus
  } from '@/api/operation/task';
  import type {
    Task,
    TaskSegment,
    TaskWaybillItem,
    TaskFinanceSummaryItem
  } from '@/api/operation/task/model';
  import { formatDateTime } from '@/utils/date-util';
  import { CARRIER_TYPE_MAP, TASK_STATUS_MAP } from '../status-config';
  import {
    TASK_ACTION_CONFIGS,
    getPrimaryTaskAction,
    getSecondaryTaskActions,
    shouldShowPlanRoute
  } from '../task-actions';
  import type { TaskActionConfig } from '../task-actions';
  import FinanceEdit from '../../task-finance/components/finance-edit.vue';
  import ActionAssignCarrier from '../../task-workbench/components/action-assign-carrier.vue';
  import ActionDispatch from '../../task-workbench/components/action-dispatch.vue';
  import ActionPlanRoute from '../../task-workbench/components/action-plan-route.vue';
  import ActionConfirmLoad from '../../task-workbench/components/action-confirm-load.vue';
  import ActionConfirmArrive from '../../task-workbench/components/action-confirm-arrive.vue';
  import ActionConfirmSign from '../../task-workbench/components/action-confirm-sign.vue';

  const props = defineProps<{ visible: boolean; taskId: number | null }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const loading = ref(false);
  const task = ref<Task | null>(null);
  const segments = ref<TaskSegment[]>([]);
  const items = ref<TaskWaybillItem[]>([]);
  const financeDocs = ref<TaskFinanceSummaryItem[]>([]);
  const activeTab = ref('segments');

  const SEGMENT_STATUS_LABEL: Record<number, string> = {
    0: '待装车',
    1: '装车中',
    2: '在途',
    3: '已到达',
    4: '已卸车'
  };
  const ITEM_STATUS_LABEL: Record<number, string> = {
    0: '待装车',
    1: '已装车',
    2: '已卸车',
    3: '已签收'
  };
  const DOC_TYPE_LABEL: Record<number, { label: string; type: string }> = {
    1: { label: '预付单', type: 'primary' },
    2: { label: '补款单', type: 'warning' },
    3: { label: '结算单', type: 'success' }
  };
  const FIN_STATUS_LABEL: Record<number, { label: string; type: string }> = {
    0: { label: '草稿', type: 'info' },
    1: { label: '待审批', type: 'warning' },
    2: { label: '已审批', type: 'primary' },
    3: { label: '已支付', type: 'success' },
    4: { label: '已撤销', type: 'danger' }
  };

  const formatAmount = (v?: number | null) => {
    if (v === null || v === undefined) return '--';
    return Number(v).toFixed(2);
  };

  watch(
    () => [props.visible, props.taskId] as const,
    async ([v, id]) => {
      if (v && id) {
        await load(id);
      }
    }
  );

  const load = async (id: number) => {
    loading.value = true;
    try {
      const [t, segs, its, fins] = await Promise.all([
        getTask(id),
        listTaskSegments(id),
        listTaskWaybillItems(id),
        listTaskFinanceSummary(id)
      ]);
      task.value = t;
      segments.value = segs;
      items.value = its;
      financeDocs.value = fins;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '加载失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const statusStep = computed(() => {
    const s = task.value?.status ?? 0;
    if (s === 9) return 0;
    const map: Record<number, number> = {
      [-1]: 0,
      0: 1,
      1: 2,
      2: 3,
      3: 4,
      4: 5,
      5: 6,
      6: 7,
      7: 8
    };
    return map[s] ?? 0;
  });

  // ============================================
  // 语义化动作
  // ============================================
  const primaryAction = computed(() => getPrimaryTaskAction(task.value?.status));
  const secondaryActions = computed(() =>
    getSecondaryTaskActions(task.value?.status)
  );

  const actionVisible = reactive({
    'assign-carrier': false,
    dispatch: false,
    'plan-route': false,
    'confirm-load': false,
    'confirm-arrive': false,
    'confirm-sign': false
  });

  const planRouteAction = TASK_ACTION_CONFIGS['plan-route'];
  const showPlanRoute = computed(() =>
    task.value ? shouldShowPlanRoute(task.value) : false
  );

  const financeInitDocType = ref<number | undefined>(undefined);
  const financeInitIsFinal = ref<number | undefined>(undefined);

  const triggerAction = async (act: TaskActionConfig) => {
    if (!task.value?.id) return;
    if (act.dialog) {
      actionVisible[act.dialog] = true;
      return;
    }
    if (act.openSettlement) {
      // 生成结算单 → 打开费用单创建并预填类型=结算单 + is_final=1
      financeInitDocType.value = 3;
      financeInitIsFinal.value = 1;
      editingFinanceId.value = null;
      financeEditVisible.value = true;
      return;
    }
    if (act.confirm) {
      await runConfirmAction(act);
    }
  };

  const runConfirmAction = async (act: TaskActionConfig) => {
    if (!task.value?.id) return;
    const confirmMessages: Record<string, string> = {
      depart: `确认任务单「${task.value.taskNo}」已出发？将推进到「在途」状态。`,
      close: `确认关闭任务单「${task.value.taskNo}」？关闭后不可再变更状态。`
    };
    try {
      await ElMessageBox.confirm(
        confirmMessages[act.key] || `确认执行「${act.label}」？`,
        '操作确认',
        { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    const targetStatus =
      act.key === 'depart' ? 3 : act.key === 'close' ? 7 : null;
    if (targetStatus === null) return;
    try {
      const updated = await updateTaskStatus(task.value.id, {
        status: targetStatus
      });
      task.value = updated;
      EleMessage.success({ message: `${act.label}成功`, plain: true });
      await reload();
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || `${act.label}失败`;
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const reload = async () => {
    if (task.value?.id) await load(task.value.id);
  };

  const onActionDone = async () => {
    await reload();
    emit('done');
  };

  /** 派车成功后：若自有车且尚未规划路线，引导立即规划 */
  const onDispatchDone = async () => {
    await reload();
    emit('done');
    if (!task.value) return;
    const t = task.value;
    if (t.carrierType === 1 && (t.segmentCount ?? 0) === 0) {
      try {
        await ElMessageBox.confirm(
          '已派车成功。该任务是自有车且尚未规划运输路线，建议立即规划（含起终点、里程）。',
          '继续规划路线？',
          {
            type: 'info',
            confirmButtonText: '立即规划',
            cancelButtonText: '稍后再说'
          }
        );
        actionVisible['plan-route'] = true;
      } catch {
        // 用户选择稍后再说，忽略
      }
    }
  };

  // ============================================
  // 费用单创建/编辑
  // ============================================
  const financeEditVisible = ref(false);
  const editingFinanceId = ref<number | null>(null);

  const openFinanceEdit = (row: TaskFinanceSummaryItem | null) => {
    editingFinanceId.value = row?.id ?? null;
    financeInitDocType.value = undefined;
    financeInitIsFinal.value = undefined;
    financeEditVisible.value = true;
  };

  const onFinanceDone = async () => {
    if (task.value?.id) {
      await load(task.value.id);
    }
    emit('done');
  };
</script>

<style lang="scss" scoped>
  .task-detail {
    padding: 0 4px;
    &__header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
    }
    &__no {
      font-size: 18px;
      font-weight: 600;
    }
    &__name {
      color: #666;
      margin-top: 4px;
    }
    &__actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }
    &__steps {
      margin: 8px 0 16px;
    }
  }
</style>
