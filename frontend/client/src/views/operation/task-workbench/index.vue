<!--
  调度工作台 - 按状态聚合的"待我处理"驾驶舱

  布局：
    - 顶部 KPI 卡片区（点击切换列表筛选状态）
    - 下方标准列表：状态池表格 + 行内主按钮（语义化）+ 批量主按钮
-->
<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '12px' }">
      <kpi-cards
        :stats="stats"
        :loading="statsLoading"
        :active-card-key="activeKpiCardKey"
        @select-card="onSelectCard"
      />

      <task-pool
        v-if="currentTab"
        :key="`${activeTab}-${listSubset}`"
        :tab-key="activeTab"
        :list-subset="listSubset"
        :reload-token="reloadToken"
        @action="onRowAction"
        @batch-action="onBatchAction"
        @open-detail="onOpenDetail"
        @sync-stats="loadStats"
      />
    </ele-card>

    <!-- 任务单详情抽屉 -->
    <task-detail
      v-model:visible="detailVisible"
      :task-id="detailTaskId"
      @done="reloadAll"
    />

    <workbench-action-modals
      v-model:action-dialog="openActionDialog"
      v-model:finance-visible="financeEditVisible"
      v-model:revert-action-key="revertActionKey"
      :targets="actionTargets"
      @done="reloadAll"
      @dispatch-done="onDispatchDone"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onActivated, onMounted, ref, watch } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import KpiCards from './components/kpi-cards.vue';
  import TaskPool from './components/task-pool.vue';
  import WorkbenchActionModals from './components/workbench-action-modals.vue';
  import TaskDetail from '../task/components/task-detail.vue';
  import { WORKBENCH_POOLS, getWorkbenchPool } from './workbench-pool-registry';
  import type { WorkbenchPool } from './workbench-pool-registry';
  import {
    batchUpdateTaskStatus,
    getTask,
    getTaskWorkbenchStats,
    updateTaskStatus
  } from '@/api/operation/task';
  import type { Task, TaskWorkbenchStats } from '@/api/operation/task/model';
  import type {
    TaskActionConfig,
    TaskActionKey
  } from '../task/task-actions';

  type WorkbenchListSubset = 'all' | 'normal' | 'alert';

  defineOptions({ name: 'OperationTaskWorkbench' });

  const activeTab = ref<string>(WORKBENCH_POOLS[0]!.key);
  /** 与 KPI 卡片 key 一致（pending-assign、on-way 等） */
  const selectedPoolKey = ref<string>(WORKBENCH_POOLS[0]!.key);
  /** KPI：全部 / 正常(常) / 预警(警) */
  const listSubset = ref<WorkbenchListSubset>('all');
  const reloadToken = ref(0);

  const activeKpiCardKey = computed(() =>
    listSubset.value === 'all'
      ? selectedPoolKey.value
      : `${selectedPoolKey.value}:${listSubset.value}`
  );

  const currentTab = computed<WorkbenchPool | undefined>(() =>
    getWorkbenchPool(activeTab.value)
  );

  // ============================================
  // KPI
  // ============================================
  const stats = ref<TaskWorkbenchStats | null>(null);
  const statsLoading = ref(false);

  const loadStats = async () => {
    statsLoading.value = true;
    try {
      stats.value = (await getTaskWorkbenchStats()) ?? null;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message;
      if (msg) EleMessage.error({ message: msg, plain: true });
    } finally {
      statsLoading.value = false;
    }
  };

  const onSelectCard = (payload: {
    cardKey: string;
    status: number | number[];
    subset: WorkbenchListSubset;
  }) => {
    selectedPoolKey.value = payload.cardKey;
    listSubset.value = payload.subset;
    const status = payload.status;
    const targetTab = WORKBENCH_POOLS.find((t) => {
      const a = Array.isArray(t.status) ? t.status : [t.status];
      const b = Array.isArray(status) ? status : [status];
      return a.every((s) => b.includes(s)) && b.every((s) => a.includes(s));
    });
    if (targetTab) activeTab.value = targetTab.key;
  };

  watch(activeTab, () => {
    actionTargets.value = [];
    openActionDialog.value = null;
    financeEditVisible.value = false;
  });

  // ============================================
  // 详情
  // ============================================
  const detailVisible = ref(false);
  const detailTaskId = ref<number | null>(null);

  const onOpenDetail = (row: Task) => {
    detailTaskId.value = row.id ?? null;
    detailVisible.value = true;
  };

  // ============================================
  // 行内 / 批量 语义化动作
  // ============================================
  const actionTargets = ref<Task[]>([]);
  const openActionDialog = ref<NonNullable<TaskActionConfig['dialog']> | null>(
    null
  );
  const financeEditVisible = ref(false);
  const revertActionKey = ref<TaskActionKey | null>(null);

  /** 单任务派车 / 生成结算单要求单选 */
  const actionSingleTask = computed<Task | null>(() =>
    actionTargets.value.length > 0 ? actionTargets.value[0] : null
  );

  const onRowAction = async (row: Task, act: TaskActionConfig) => {
    actionTargets.value = [row];
    await triggerAction(act);
  };

  const onBatchAction = async (rows: Task[], act: TaskActionConfig) => {
    if (act.key === 'assign-carrier') {
      EleMessage.warning({
        message: '分配承运需确认承运方式，请逐单操作',
        plain: true
      });
      return;
    }
    if (act.key === 'dispatch') {
      EleMessage.warning({
        message: '派车涉及承运方选择，请逐单操作',
        plain: true
      });
      return;
    }
    if (act.key === 'plan-route') {
      EleMessage.warning({
        message: '路线规划需逐单填写起终点，请逐单操作',
        plain: true
      });
      return;
    }
    if (act.openSettlement) {
      EleMessage.warning({
        message: '生成结算单需逐单填写费用项，请逐单操作',
        plain: true
      });
      return;
    }
    actionTargets.value = rows;
    await triggerAction(act);
  };

  const triggerAction = async (act: TaskActionConfig) => {
    if (act.dialog === 'revert') {
      revertActionKey.value = act.key;
      openActionDialog.value = 'revert';
      return;
    }
    if (act.dialog) {
      openActionDialog.value = act.dialog;
      return;
    }
    if (act.openSettlement) {
      financeEditVisible.value = true;
      return;
    }
    if (act.confirm) {
      await runConfirmAction(act);
    }
  };

  const runConfirmAction = async (act: TaskActionConfig) => {
    if (actionTargets.value.length === 0) return;
    const single = actionTargets.value.length === 1;
    const messages: Record<string, string> = {
      depart: single
        ? `确认任务单「${actionTargets.value[0].taskNo}」已出发？将推进到「在途」状态。`
        : `确认批量推进 ${actionTargets.value.length} 张任务单为「在途」状态？`,
      close: single
        ? `确认关闭任务单「${actionTargets.value[0].taskNo}」？关闭后不可再变更状态。`
        : `确认批量关闭 ${actionTargets.value.length} 张任务单？`
    };
    try {
      await ElMessageBox.confirm(
        messages[act.key] || `确认执行「${act.label}」？`,
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
      if (actionTargets.value.length === 1) {
        const id = actionTargets.value[0].id;
        if (!id) return;
        await updateTaskStatus(id, { status: targetStatus });
      } else {
        const ids = actionTargets.value.map((t) => t.id!).filter(Boolean);
        const res = await batchUpdateTaskStatus({
          ids,
          status: targetStatus
        });
        if (res && res.failed > 0) {
          EleMessage.warning({
            message: `成功 ${res.success} 张，失败 ${res.failed} 张`,
            plain: true
          });
        }
      }
      EleMessage.success({ message: `${act.label}成功`, plain: true });
      await reloadAll();
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || `${act.label}失败`;
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const reloadAll = async () => {
    await refreshWorkbench();
  };

  /** 派车成功后：若自有车且尚未规划路线，引导继续规划 */
  const onDispatchDone = async () => {
    const t = actionSingleTask.value;
    if (!t?.id) {
      await reloadAll();
      return;
    }
    let updated: Task | null = null;
    try {
      updated = (await getTask(t.id)) ?? null;
    } catch {
      updated = null;
    }
    await reloadAll();
    if (
      updated &&
      updated.carrierType === 1 &&
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
        actionTargets.value = [updated];
        openActionDialog.value = 'plan-route';
      } catch {
        // ignore
      }
    }
  };

  const refreshWorkbench = async () => {
    await loadStats();
    reloadToken.value += 1;
  };

  onMounted(() => {
    refreshWorkbench();
  });

  onActivated(() => {
    refreshWorkbench();
  });
</script>
