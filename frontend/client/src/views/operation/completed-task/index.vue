<!--
  已完成任务（独立模块）

  与调度工作台分离的终态任务查看入口：已签收(5) / 已关闭(7) / 已取消(9)。
  逆向严格按《02.计划与任务单状态机联动设计.md》§4.5.1：
  - 仅「已签收(5)」可逆——「撤销签收」(item 3→2 反向聚合驱动 task 5→4)、「关闭任务」(5→7)；
  - 「已关闭(7)/已取消(9)」为终态，仅「详情」。

  页面自托管：统计（Tab 计数）、动作弹窗（撤销签收 / 关闭）、任务详情抽屉与刷新链路。
-->
<template>
  <ele-page>
    <ele-card :body-style="{ paddingBottom: '4px' }" class="completed-page__filter">
      <el-form :model="where" inline @submit.prevent>
        <el-form-item label="关键字">
          <el-input
            v-model="where.keyword"
            placeholder="任务单号 / 计划号"
            clearable
            style="width: 260px"
            @keyup.enter="onSearch"
            @clear="onSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="onSearch">
            搜索
          </el-button>
          <el-button :icon="Refresh" @click="onReset">重置</el-button>
        </el-form-item>
      </el-form>
    </ele-card>

    <completed-task-section
      :stats="stats"
      :reload-token="reloadToken"
      :search-where="searchWhere"
      @action="onRowAction"
      @open-detail="onOpenDetail"
    />

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
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { onActivated, onMounted, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { Refresh, Search } from '@element-plus/icons-vue';
  import CompletedTaskSection from '../task-workbench/components/completed-task-section.vue';
  import WorkbenchActionModals from '../task-workbench/components/workbench-action-modals.vue';
  import TaskDetail from '../task/components/task-detail.vue';
  import {
    getTaskWorkbenchStats,
    updateTaskStatus
  } from '@/api/operation/task';
  import type {
    Task,
    TaskParam,
    TaskWorkbenchStats
  } from '@/api/operation/task/model';
  import type { TaskActionConfig, TaskActionKey } from '../task/task-actions';

  defineOptions({ name: 'OperationCompletedTask' });

  const where = ref<{ keyword: string }>({ keyword: '' });
  const searchWhere = ref<Partial<TaskParam>>({});
  const reloadToken = ref(0);

  const onSearch = () => {
    const kw = where.value.keyword.trim();
    searchWhere.value = kw ? { keyword: kw } : {};
  };

  const onReset = () => {
    where.value.keyword = '';
    searchWhere.value = {};
  };

  // ============================================
  // KPI 统计（仅用于 Tab 计数徽标）
  // ============================================
  const stats = ref<TaskWorkbenchStats | null>(null);

  const loadStats = async () => {
    try {
      const kw = where.value.keyword.trim();
      stats.value =
        (await getTaskWorkbenchStats(kw ? { keyword: kw } : {})) ?? null;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message;
      if (msg) EleMessage.error({ message: msg, plain: true });
    }
  };

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
  // 行内语义化动作（撤销签收 / 关闭任务）
  // ============================================
  const actionTargets = ref<Task[]>([]);
  const openActionDialog = ref<NonNullable<TaskActionConfig['dialog']> | null>(
    null
  );
  const financeEditVisible = ref(false);
  const editVisible = ref(false);
  const revertActionKey = ref<TaskActionKey | null>(null);

  const onRowAction = async (row: Task, act: TaskActionConfig) => {
    actionTargets.value = [row];
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
    if (act.confirm) {
      await runConfirmAction(act);
    }
  };

  const runConfirmAction = async (act: TaskActionConfig) => {
    if (actionTargets.value.length === 0) return;
    const target = actionTargets.value[0];
    if (!target?.id) return;
    const tip =
      act.key === 'close'
        ? `确认关闭任务单「${target.taskNo}」？关闭后不可再变更状态。`
        : `确认执行「${act.label}」？`;
    try {
      await ElMessageBox.confirm(tip, '操作确认', {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      });
    } catch {
      return;
    }
    const targetStatus = act.key === 'close' ? 7 : null;
    if (targetStatus === null) return;
    try {
      await updateTaskStatus(target.id, { status: targetStatus });
      EleMessage.success({ message: `${act.label}成功`, plain: true });
      await reloadAll();
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || `${act.label}失败`;
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const reloadAll = async () => {
    await loadStats();
    reloadToken.value += 1;
  };

  onMounted(() => {
    reloadAll();
  });

  onActivated(() => {
    reloadAll();
  });
</script>

<style scoped>
  .completed-page__filter {
    margin-bottom: 12px;
  }
</style>
