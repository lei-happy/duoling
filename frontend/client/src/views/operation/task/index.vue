<template>
  <ele-page>
    <task-search @search="(w) => reload(w, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        v-model:selections="selections"
        :default-sort="{ prop: 'createdAt', order: 'descending' }"
        cache-key="OperationTaskTableV2"
      >
        <template #toolbar>
          <el-text type="info" size="small">
            新建配载请前往
            <el-link type="primary" :underline="false" @click="goTaskCreate">
              「手动配载」
            </el-link>
            ；常用作业请前往
            <el-link type="primary" :underline="false" @click="goWorkbench">
              「调度工作台」
            </el-link>
            按状态批量处理
          </el-text>
        </template>

        <template #carrierType="{ row }">
          <el-tag
            :type="(CARRIER_TYPE_MAP[row.carrierType]?.type as any) || 'info'"
            size="small"
          >
            {{ CARRIER_TYPE_MAP[row.carrierType]?.label || '--' }}
          </el-tag>
        </template>

        <template #origin="{ row }">
          <span class="route-cell-text" :title="row.origin?.trim() || undefined">
            {{ row.origin || '--' }}
          </span>
        </template>

        <template #destination="{ row }">
          <div class="destination-cell">
            <span
              class="route-cell-text"
              :title="row.destination?.trim() || undefined"
            >
              {{ row.destination || '--' }}
            </span>
            <el-tag
              v-if="(row.segmentCount || 0) > 1"
              size="small"
              type="info"
              effect="plain"
              class="destination-cell__tag"
            >
              {{ row.segmentCount }} 段
            </el-tag>
          </div>
        </template>

        <template #carrierResource="{ row }">
          <div v-if="row.carrierType === CARRIER_TYPE.CARRIER">
            {{ row.carrierName || '--' }}
          </div>
          <div v-else>
            {{ row.mainDriverName || '--' }}
            <span v-if="row.plateNumber" class="ele-text-secondary">
              / {{ row.plateNumber }}
            </span>
          </div>
        </template>

        <template #status="{ row }">
          <el-tag
            :type="(TASK_STATUS_MAP[row.status]?.type as any) || 'info'"
            size="small"
          >
            {{ TASK_STATUS_MAP[row.status]?.label || '--' }}
          </el-tag>
        </template>

        <template #prepaidAmount="{ row }">
          <span style="font-variant-numeric: tabular-nums">
            {{ formatAmount(row.prepaidAmount) }}
          </span>
        </template>

        <template #waybillStatusSummary="{ row }">
          <waybill-status-summary :summary="row.waybillStatusSummary" inline />
        </template>

        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :wrap="false"
            :items="actionItems(row)"
          />
        </template>
      </ele-pro-table>
    </ele-card>

    <task-edit v-model:visible="editVisible" :data="editData" @done="reload" />
    <task-detail
      v-model:visible="detailVisible"
      :task-id="detailTaskId"
      @done="reload"
    />

    <!-- 行内主按钮触发的语义化弹窗 -->
    <action-assign-carrier
      v-model:visible="actionVisible['assign-carrier']"
      :task="actionTask"
      @done="reload"
    />
    <action-dispatch
      v-model:visible="actionVisible.dispatch"
      :task="actionTask"
      @done="onDispatchDone"
    />
    <action-plan-route
      v-model:visible="actionVisible['plan-route']"
      :task="actionTask"
      @done="reload"
    />
    <action-confirm-load
      v-model:visible="actionVisible['confirm-load']"
      :tasks="actionTask ? [actionTask] : []"
      @done="reload"
    />
    <action-confirm-arrive
      v-model:visible="actionVisible['confirm-arrive']"
      :tasks="actionTask ? [actionTask] : []"
      @done="reload"
    />
    <action-confirm-sign
      v-model:visible="actionVisible['confirm-sign']"
      :tasks="actionTask ? [actionTask] : []"
      @done="reload"
    />
    <action-revert
      v-if="actionTask && revertActionKey"
      v-model:visible="actionVisible.revert"
      :tasks="[actionTask]"
      :action-key="revertActionKey"
      @done="reload"
    />
    <action-revert-sign
      v-model:visible="actionVisible['revert-sign']"
      :tasks="actionTask ? [actionTask] : []"
      @done="reload"
    />
    <action-force-cancel
      v-model:visible="actionVisible['force-cancel']"
      :tasks="actionTask ? [actionTask] : []"
      @done="reload"
    />
    <action-cancel-task
      v-model:visible="actionVisible['cancel-task']"
      :tasks="actionTask ? [actionTask] : []"
      @done="reload"
    />

    <!-- 费用单创建：新建费用单（预付等，按节点过滤）/ 生成结算单 -->
    <finance-edit
      v-if="actionTask"
      v-model:visible="financeEditVisible"
      :task="actionTask"
      :doc-id="null"
      :init-doc-type="financeInitDocType"
      :init-is-final="financeInitIsFinal"
      @done="reload"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, ref, reactive, nextTick } from 'vue';
  import { useRouter } from 'vue-router';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import type { ButtonItem } from 'ele-admin-plus/es/ele-buttons/types';
  import TaskEdit from './components/task-edit.vue';
  import TaskDetail from './components/task-detail.vue';
  import TaskSearch from './components/task-search.vue';
  import WaybillStatusSummary from './components/waybill-status-summary.vue';
  import ActionAssignCarrier from '../task-workbench/components/action-assign-carrier.vue';
  import ActionDispatch from '../task-workbench/components/action-dispatch.vue';
  import ActionPlanRoute from '../task-workbench/components/action-plan-route.vue';
  import ActionConfirmLoad from '../task-workbench/components/action-confirm-load.vue';
  import ActionConfirmArrive from '../task-workbench/components/action-confirm-arrive.vue';
  import ActionConfirmSign from '../task-workbench/components/action-confirm-sign.vue';
  import ActionRevert from '../task-workbench/components/action-revert.vue';
  import ActionRevertSign from '../task-workbench/components/action-revert-sign.vue';
  import ActionForceCancel from '../task-workbench/components/action-force-cancel.vue';
  import ActionCancelTask from '../task-workbench/components/action-cancel-task.vue';
  import FinanceEdit from '../task-finance/components/finance-edit.vue';
  import {
    getTask,
    pageTasks,
    removeTask,
    updateTaskStatus
  } from '@/api/operation/task';
  import type { Task, TaskParam } from '@/api/operation/task/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    CARRIER_TYPE,
    CARRIER_TYPE_MAP,
    TASK_STATUS_MAP
  } from './status-config';
  import {
    buildTaskListActionItems,
    resolveTaskListActionColumnMinWidth
  } from './task-actions';
  import type { TaskActionConfig, TaskActionKey } from './task-actions';
  import { getCreatableDocTypes } from '@/api/operation/task-finance';
  import { usePermission } from '@/utils/use-permission';

  defineOptions({ name: 'OperationTask' });

  const router = useRouter();
  const { hasPermission } = usePermission();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Task[]>([]);
  const editVisible = ref(false);
  const editData = ref<Task | null>(null);
  const detailVisible = ref(false);
  const detailTaskId = ref<number | null>(null);

  const formatAmount = (v?: number | null) => {
    if (v === null || v === undefined) return '--';
    return Number(v).toFixed(2);
  };

  const actionColumnMinWidth = resolveTaskListActionColumnMinWidth();

  const columns = computed<Columns>(() => [
    { prop: 'taskNo', label: '任务单号', minWidth: 160 },
    {
      prop: 'carrierType',
      label: '承运方式',
      width: 96,
      align: 'center',
      slot: 'carrierType'
    },
    {
      prop: 'origin',
      label: '出发地',
      minWidth: 140,
      slot: 'origin'
    },
    {
      prop: 'destination',
      label: '目的地',
      minWidth: 160,
      slot: 'destination'
    },
    {
      columnKey: 'carrierResource',
      label: '司机/车牌/承运商',
      minWidth: 200,
      slot: 'carrierResource'
    },
    {
      prop: 'totalQuantity',
      label: '台数',
      width: 80,
      align: 'center'
    },
    {
      prop: 'waybillCount',
      label: '计划数',
      width: 80,
      align: 'center'
    },
    {
      columnKey: 'waybillStatusSummary',
      label: '计划状态',
      minWidth: 180,
      align: 'center',
      slot: 'waybillStatusSummary'
    },
    {
      prop: 'plannedLoadTime',
      label: '计划装车',
      width: 150,
      align: 'center',
      formatter: (row) => formatDateTime(row.plannedLoadTime) || '--'
    },
    {
      prop: 'prepaidAmount',
      label: '已预付',
      width: 100,
      align: 'right',
      slot: 'prepaidAmount'
    },
    {
      prop: 'status',
      label: '状态',
      width: 88,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'createdAt',
      label: '创建时间',
      width: 160,
      align: 'center',
      formatter: (row) => formatDateTime(row.createdAt) || '--'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: actionColumnMinWidth,
      minWidth: actionColumnMinWidth,
      align: 'center',
      fixed: 'right',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where }) => {
    return pageTasks({
      ...(where as TaskParam | undefined),
      ...pages
    }).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));
  };

  const reload = (where?: TaskParam, page?: number) => {
    const t = tableRef.value;
    if (!t) return;
    const hasWhere = where !== undefined;
    const hasPage = page !== undefined;
    if (!hasWhere && !hasPage) {
      nextTick(() => t.reload?.());
      return;
    }
    const opt: { where?: TaskParam; page?: number } = {};
    if (hasWhere) opt.where = where;
    if (hasPage) opt.page = page;
    t.reload?.(opt);
  };

  const openEdit = (row?: Task) => {
    editData.value = row ? { ...row } : null;
    editVisible.value = true;
  };

  const openDetail = (row: Task) => {
    detailTaskId.value = row.id ?? null;
    detailVisible.value = true;
  };

  const goWorkbench = () => {
    router.push('/operation/task-workbench');
  };

  const goTaskCreate = () => {
    router.push('/operation/task-create');
  };

  // ============================================
  // 行内语义化动作
  // ============================================
  const actionTask = ref<Task | null>(null);
  const actionVisible = reactive({
    'assign-carrier': false,
    dispatch: false,
    'plan-route': false,
    'confirm-load': false,
    'confirm-arrive': false,
    'confirm-sign': false,
    revert: false,
    'revert-sign': false,
    'force-cancel': false,
    'cancel-task': false
  });
  const financeEditVisible = ref(false);
  const financeInitDocType = ref<number | undefined>(undefined);
  const financeInitIsFinal = ref<number | undefined>(undefined);
  const revertActionKey = ref<TaskActionKey | null>(null);

  /** 操作列：btn-items + 悬停「更多」，见开发手册 17 */
  const actionItems = (row: Task): ButtonItem[] =>
    buildTaskListActionItems(row, {
      hasPermission,
      onDetail: () => openDetail(row),
      onAction: (act) => triggerAction(row, act)
    });

  /**
   * 派车成功后：优先引导创建预付单（贴合"派完车即预付"动线）；
   * 若未触发预付引导，再对自有车未规划路线的任务引导规划。
   */
  const maybePromptPrepay = async (t: Task | null): Promise<boolean> => {
    if (!t?.id) return false;
    if (!hasPermission('operation:task-finance:add')) return false;
    let creatable: number[] = [];
    try {
      const res = await getCreatableDocTypes(t.id);
      creatable = res?.docTypes ?? [];
    } catch {
      return false;
    }
    // 预付单(1)在当前节点不可发起则不打扰
    if (!creatable.includes(1)) return false;
    try {
      await ElMessageBox.confirm(
        `运力已派完，是否立即为任务单「${t.taskNo}」创建预付单？`,
        '创建预付单',
        {
          type: 'info',
          confirmButtonText: '立即创建',
          cancelButtonText: '暂不创建'
        }
      );
    } catch {
      return false;
    }
    actionTask.value = t;
    financeInitDocType.value = 1;
    financeInitIsFinal.value = 0;
    financeEditVisible.value = true;
    return true;
  };

  const onDispatchDone = async () => {
    const t = actionTask.value;
    if (!t?.id) {
      reload();
      return;
    }
    let updated: Task | null = null;
    try {
      updated = (await getTask(t.id)) ?? null;
    } catch {
      updated = null;
    }
    reload();
    if (await maybePromptPrepay(updated)) {
      return;
    }
    if (
      updated &&
      updated.carrierType === CARRIER_TYPE.SELF &&
      (updated.segmentCount ?? 0) === 0
    ) {
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
        actionTask.value = updated;
        actionVisible['plan-route'] = true;
      } catch {
        // 用户选择稍后
      }
    }
  };

  const triggerAction = async (row: Task, act: TaskActionConfig) => {
    actionTask.value = row;
    if (act.key === 'edit') {
      openEdit(row);
      return;
    }
    if (act.key === 'delete') {
      await runDeleteAction(row);
      return;
    }
    if (act.dialog === 'revert') {
      revertActionKey.value = act.key;
      actionVisible.revert = true;
      return;
    }
    if (act.dialog) {
      actionVisible[act.dialog] = true;
      return;
    }
    if (act.openSettlement) {
      financeInitDocType.value = 3;
      financeInitIsFinal.value = 1;
      financeEditVisible.value = true;
      return;
    }
    if (act.openFinance) {
      // 不预设类型：由弹框按当前节点配置过滤，通常落到预付单
      financeInitDocType.value = undefined;
      financeInitIsFinal.value = undefined;
      financeEditVisible.value = true;
      return;
    }
    if (act.confirm) {
      await runConfirmAction(row, act);
    }
  };

  const runConfirmAction = async (row: Task, act: TaskActionConfig) => {
    const confirmMessages: Record<string, string> = {
      depart: `确认任务单「${row.taskNo}」已出发？将推进到「在途」状态。`,
      close: `确认关闭任务单「${row.taskNo}」？关闭后不可再变更状态。`
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
    if (targetStatus === null || !row.id) return;
    try {
      await updateTaskStatus(row.id, { status: targetStatus });
      EleMessage.success({ message: `${act.label}成功`, plain: true });
      reload();
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || `${act.label}失败`;
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const runDeleteAction = async (row: Task) => {
    if (!row.id) return;
    try {
      await ElMessageBox.confirm(
        `确定要删除任务单「${row.taskNo}」吗？`,
        '提示',
        { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
      );
      await removeTask(row.id);
      EleMessage.success({ message: '删除成功', plain: true });
      reload();
    } catch (err: unknown) {
      const e = err as { message?: string } | string | undefined;
      if (e === 'cancel') return;
      const msg = (typeof e === 'object' && e?.message) || '';
      if (msg) EleMessage.error({ message: msg, plain: true });
    }
  };
</script>

<style lang="scss" scoped>
  .route-cell-text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
  }

  .destination-cell {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    max-width: 100%;
    white-space: nowrap;
    vertical-align: middle;
  }

  .destination-cell__tag {
    flex-shrink: 0;
  }
</style>
