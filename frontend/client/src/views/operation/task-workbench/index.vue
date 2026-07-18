<!--
  调度工作台 - 按状态聚合的"待我处理"驾驶舱

  布局（对齐计划工作台）：
    1. 顶部 统一筛选栏（任务单号/计划号/线路/承运方式等，切换阶段时不重建）
    2. 中部 5 张阶段卡（待分配 / 待派车 / 待装车 / 在途中 / 待签收）
       输入任务单号搜索时跨状态匹配并自动切到对应阶段
    3. 下部 列表 + 行内主按钮 + 批量主按钮
-->
<template>
  <ele-page>
    <task-pool-filter
      class="workbench-page__filter"
      :pool-key="activeTab"
      @search="onSearch"
      @reset="onFilterReset"
    />

    <kpi-cards
      class="workbench-page__cards"
      :stats="stats"
      :loading="statsLoading"
      :active-card-key="activeKpiCardKey"
      @select-card="onSelectCard"
    />

    <task-pool
      v-if="currentTab"
      :tab-key="activeTab"
      :list-subset="listSubset"
      :search-where="searchWhere"
      :reload-token="reloadToken"
      @action="onRowAction"
      @batch-action="onBatchAction"
      @open-detail="onOpenDetail"
      @sync-stats="loadStats"
      @auto-switch-pool="onAutoSwitchPool"
    />

    <!-- 任务单详情抽屉 -->
    <task-detail
      v-model:visible="detailVisible"
      :task-id="detailTaskId"
      @done="reloadAll"
    />

    <workbench-action-modals
      v-model:action-dialog="openActionDialog"
      v-model:finance-visible="financeEditVisible"
      v-model:edit-visible="editVisible"
      v-model:revert-action-key="revertActionKey"
      :targets="actionTargets"
      @done="reloadAll"
      @dispatch-done="onDispatchDone"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onActivated, onMounted, ref, watch } from 'vue';
  import { useRoute } from 'vue-router';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import KpiCards from './components/kpi-cards.vue';
  import TaskPoolFilter from './components/task-pool-filter.vue';
  import TaskPool from './components/task-pool.vue';
  import WorkbenchActionModals from './components/workbench-action-modals.vue';
  import TaskDetail from '../task/components/task-detail.vue';
  import { WORKBENCH_POOLS, getWorkbenchPool } from './workbench-pool-registry';
  import type { WorkbenchPool } from './workbench-pool-registry';
  import {
    batchUpdateTaskStatus,
    getTask,
    getTaskWorkbenchStats,
    removeTask,
    updateTaskStatus
  } from '@/api/operation/task';
  import type {
    Task,
    TaskParam,
    TaskWorkbenchStats
  } from '@/api/operation/task/model';
  import type { TaskActionConfig, TaskActionKey } from '../task/task-actions';
  import { CARRIER_TYPE } from '../task/status-config';

  type WorkbenchListSubset = 'all' | 'normal' | 'alert';

  defineOptions({ name: 'OperationTaskWorkbench' });

  const route = useRoute();

  const resolveInitialTab = (): string => {
    const tab = route.query.tab;
    if (typeof tab === 'string' && getWorkbenchPool(tab)) {
      return tab;
    }
    return WORKBENCH_POOLS[0]!.key;
  };

  const activeTab = ref<string>(resolveInitialTab());
  /** 与 KPI 卡片 key 一致（pending-assign、on-way 等） */
  const selectedPoolKey = ref<string>(resolveInitialTab());
  /** KPI：全部 / 正常(常) / 预警(警) */
  const listSubset = ref<WorkbenchListSubset>('all');
  const reloadToken = ref(0);
  /** 统一筛选条件（切换阶段卡时保留） */
  const searchWhere = ref<Partial<TaskParam>>({});

  const onSearch = (where: Partial<TaskParam>) => {
    searchWhere.value = where;
  };

  /** 与列表查询对齐：有 keyword 时仅传 keyword，否则传全部筛选（不含 status/子集） */
  const buildStatsParams = (): Partial<TaskParam> => {
    const search = searchWhere.value;
    const keyword = search.keyword?.trim();
    if (keyword) return { keyword };
    const {
      status: _s,
      onlyOverdue: _o,
      onlyNormal: _n,
      inTransitOverdue: _io,
      inTransitOnlyNormal: _in,
      ...rest
    } = { ...search };
    return rest;
  };

  /** 筛选重置：恢复默认阶段卡 + 全部子集 + 默认筛选条件 */
  const onFilterReset = (where: Partial<TaskParam>) => {
    searchWhere.value = where;
    const defaultKey = WORKBENCH_POOLS[0]!.key;
    activeTab.value = defaultKey;
    selectedPoolKey.value = defaultKey;
    listSubset.value = 'all';
  };

  /** 按任务单号跨状态命中后，自动切换到任务所在阶段 */
  const onAutoSwitchPool = (poolKey: string) => {
    if (poolKey === activeTab.value && listSubset.value === 'all') return;
    selectedPoolKey.value = poolKey;
    activeTab.value = poolKey;
    listSubset.value = 'all';
  };

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
      stats.value = (await getTaskWorkbenchStats(buildStatsParams())) ?? null;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message;
      if (msg) EleMessage.error({ message: msg, plain: true });
    } finally {
      statsLoading.value = false;
    }
  };

  watch(searchWhere, () => loadStats(), { deep: true });

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
    editVisible.value = false;
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
  const editVisible = ref(false);
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
    if (act.key === 'edit') {
      editVisible.value = true;
      return;
    }
    if (act.key === 'delete') {
      await runDeleteAction();
      return;
    }
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

  /** 删除任务单：仅 -1/0/9 状态允许；批量场景循环调用 */
  const runDeleteAction = async () => {
    if (actionTargets.value.length === 0) return;
    const single = actionTargets.value.length === 1;
    const tip = single
      ? `确定要删除任务单「${actionTargets.value[0].taskNo}」吗？`
      : `确认删除选中的 ${actionTargets.value.length} 张任务单？`;
    try {
      await ElMessageBox.confirm(tip, '操作确认', {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      });
    } catch {
      return;
    }
    let failCount = 0;
    for (const t of actionTargets.value) {
      if (!t.id) continue;
      try {
        await removeTask(t.id);
      } catch {
        failCount += 1;
      }
    }
    if (failCount > 0) {
      EleMessage.warning({
        message: `已删除 ${actionTargets.value.length - failCount} 张，失败 ${failCount} 张`,
        plain: true
      });
    } else {
      EleMessage.success({ message: '删除成功', plain: true });
    }
    await reloadAll();
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

<style scoped>
  .workbench-page__filter {
    margin-bottom: 12px;
  }

  .workbench-page__cards {
    margin-bottom: 12px;
  }
</style>
