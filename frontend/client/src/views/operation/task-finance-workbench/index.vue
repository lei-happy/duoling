<!--
  费用工作台 - 按状态聚合的费用单驾驶舱

  布局：
    - 顶部 KPI 卡片（草稿/待审批/待支付/今日已支付）
    - 主 Tab 池：草稿 / 待审批 / 待支付 / 已支付台账 / 已撤销
    - 每个 Tab 内：费用单池表格 + 行内主按钮（语义化）+ 批量主按钮
-->
<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '12px' }">
      <kpi-cards
        :stats="stats"
        :loading="statsLoading"
        @select-status="onSelectStatus"
      />

      <el-tabs v-model="activeTab" type="border-card" @tab-change="onTabChange">
        <el-tab-pane
          v-for="tab in TABS"
          :key="tab.key"
          :name="tab.key"
          :label="tabLabel(tab)"
        >
          <finance-pool
            v-if="activeTab === tab.key"
            :tab-key="tab.key"
            :status="tab.status"
            :primary-action-key="tab.actionKey"
            :reload-token="reloadToken"
            @action="onRowAction"
            @batch-action="onBatchAction"
            @open-detail="onOpenDetail"
          />
        </el-tab-pane>
      </el-tabs>
    </ele-card>

    <!-- 费用单详情/编辑抽屉 -->
    <finance-edit
      v-if="currentTask"
      v-model:visible="editVisible"
      :task="currentTask"
      :doc-id="editingDocId"
      @done="reloadAll"
    />

    <!-- 标记已支付弹窗（单条 + 批量） -->
    <action-pay
      v-model:visible="payVisible"
      :docs="payTargets"
      @done="reloadAll"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import KpiCards from './components/kpi-cards.vue';
  import FinancePool from './components/finance-pool.vue';
  import ActionPay from './components/action-pay.vue';
  import FinanceEdit from '../task-finance/components/finance-edit.vue';
  import {
    approveFinanceDoc,
    batchFinanceAction,
    cancelFinanceDoc,
    getFinanceWorkbenchStats,
    submitFinanceDoc
  } from '@/api/operation/task-finance';
  import type {
    TaskFinanceDocListItem,
    TaskFinanceWorkbenchStats
  } from '@/api/operation/task-finance/model';
  import { getTask } from '@/api/operation/task';
  import type { Task } from '@/api/operation/task/model';
  import type {
    FinanceActionConfig,
    FinanceActionKey
  } from '../task-finance/task-finance-actions';

  defineOptions({ name: 'OperationTaskFinanceWorkbench' });

  interface TabConfig {
    key: string;
    label: string;
    status: number;
    actionKey: FinanceActionKey | null;
    countKey: keyof TaskFinanceWorkbenchStats['totals'];
  }

  const TABS: TabConfig[] = [
    {
      key: 'draft',
      label: '草稿',
      status: 0,
      actionKey: 'submit',
      countKey: 'draft'
    },
    {
      key: 'pending-review',
      label: '待审批',
      status: 1,
      actionKey: 'approve',
      countKey: 'pendingReview'
    },
    {
      key: 'pending-pay',
      label: '待支付',
      status: 2,
      actionKey: 'pay',
      countKey: 'pendingPay'
    },
    {
      key: 'paid',
      label: '已支付台账',
      status: 3,
      actionKey: null,
      countKey: 'paid'
    },
    {
      key: 'cancelled',
      label: '已撤销',
      status: 4,
      actionKey: null,
      countKey: 'cancelled'
    }
  ];

  const activeTab = ref<string>(TABS[1].key); // 默认进入"待审批"
  const reloadToken = ref(0);

  const tabLabel = (tab: TabConfig) => {
    if (!stats.value) return tab.label;
    const c = stats.value.totals[tab.countKey] || 0;
    return `${tab.label} (${c})`;
  };

  // ============================================
  // KPI
  // ============================================
  const stats = ref<TaskFinanceWorkbenchStats | null>(null);
  const statsLoading = ref(false);

  const loadStats = async () => {
    statsLoading.value = true;
    try {
      stats.value = await getFinanceWorkbenchStats();
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message;
      if (msg) EleMessage.error({ message: msg, plain: true });
    } finally {
      statsLoading.value = false;
    }
  };

  const onSelectStatus = (status: number) => {
    const t = TABS.find((x) => x.status === status);
    if (t) activeTab.value = t.key;
  };

  const onTabChange = () => {
    payTargets.value = [];
  };

  // ============================================
  // 详情/编辑
  // ============================================
  const editVisible = ref(false);
  const editingDocId = ref<number | null>(null);
  const currentTask = ref<Task | null>(null);

  const onOpenDetail = async (row: TaskFinanceDocListItem) => {
    try {
      const t = await getTask(row.taskId);
      currentTask.value = t;
      editingDocId.value = row.id;
      editVisible.value = true;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '打开失败';
      EleMessage.error({ message: msg, plain: true });
    }
  };

  // ============================================
  // 行内 / 批量 语义化动作
  // ============================================
  const payVisible = ref(false);
  const payTargets = ref<TaskFinanceDocListItem[]>([]);

  const onRowAction = async (
    row: TaskFinanceDocListItem,
    act: FinanceActionConfig
  ) => {
    if (act.dialog === 'pay') {
      payTargets.value = [row];
      payVisible.value = true;
      return;
    }
    if (act.confirm) {
      await runConfirmAction([row], act);
    }
  };

  const onBatchAction = async (
    rows: TaskFinanceDocListItem[],
    act: FinanceActionConfig
  ) => {
    if (act.dialog === 'pay') {
      payTargets.value = rows;
      payVisible.value = true;
      return;
    }
    if (act.confirm) {
      await runConfirmAction(rows, act);
    }
  };

  const runConfirmAction = async (
    rows: TaskFinanceDocListItem[],
    act: FinanceActionConfig
  ) => {
    if (rows.length === 0) return;
    const single = rows.length === 1;
    const messages: Record<string, string> = {
      submit: single
        ? `确认提交费用单「${rows[0].docNo}」进行审批？`
        : `确认批量提交 ${rows.length} 张费用单进行审批？`,
      approve: single
        ? `确认审批通过费用单「${rows[0].docNo}」？`
        : `确认批量审批通过 ${rows.length} 张费用单？`,
      cancel: single
        ? `确认撤销费用单「${rows[0].docNo}」？`
        : `确认批量撤销 ${rows.length} 张费用单？`
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
    try {
      if (single) {
        const id = rows[0].id;
        if (act.key === 'submit') {
          await submitFinanceDoc(id);
        } else if (act.key === 'approve') {
          await approveFinanceDoc(id);
        } else if (act.key === 'cancel') {
          await cancelFinanceDoc(id);
        }
      } else {
        const ids = rows.map((r) => r.id).filter(Boolean);
        const action =
          act.key === 'submit'
            ? 'submit'
            : act.key === 'approve'
              ? 'approve'
              : act.key === 'cancel'
                ? 'cancel'
                : null;
        if (!action) return;
        const res = await batchFinanceAction({ ids, action });
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
    reloadToken.value += 1;
    await loadStats();
  };

  onMounted(() => {
    loadStats();
  });
</script>
