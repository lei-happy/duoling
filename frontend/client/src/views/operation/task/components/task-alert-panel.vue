<!--
  任务详情抽屉 · 预警区块

  展示这张任务单当前踩了哪些预警线，并就地完成处置闭环：
  认领（我来跟）→ 已处理（跟完了）→ 忽略（这条不用管，必须写原因）。

  已处置的预警不删除，折叠在下方供复盘 —— 「这单为什么晚了」的答案通常在这里。
-->
<template>
  <div class="task-alert-panel" v-loading="loading">
    <div v-if="activeAlerts.length === 0" class="task-alert-panel__empty">
      <el-icon class="task-alert-panel__empty-icon"><CircleCheck /></el-icon>
      <span>这张任务单目前没有需要处理的预警</span>
    </div>

    <div v-else class="task-alert-panel__list">
      <div
        v-for="alert in activeAlerts"
        :key="alert.id"
        class="alert-item"
        :class="`alert-item--${alert.level === 2 ? 'critical' : 'warn'}`"
      >
        <div class="alert-item__main">
          <div class="alert-item__title">
            <el-tag
              :type="alert.level === 2 ? 'danger' : 'warning'"
              size="small"
              effect="dark"
            >
              {{ alert.levelLabel || (alert.level === 2 ? '严重' : '关注') }}
            </el-tag>
            <span class="alert-item__rule">
              {{ alert.ruleName || alert.ruleCode }}
            </span>
            <span v-if="alert.stageLabel" class="ele-text-secondary">
              · {{ alert.stageLabel }}阶段
            </span>
          </div>
          <div class="alert-item__meta ele-text-secondary">
            <span v-if="alert.dueAt">
              应完成：{{ formatDateTime(alert.dueAt) }}
            </span>
            <span v-if="alert.overdueMinutes > 0" class="alert-item__overdue">
              已超时 {{ formatDurationMinutes(alert.overdueMinutes) }}
            </span>
            <span>触发于 {{ formatDateTime(alert.triggeredAt) || '--' }}</span>
            <span v-if="alert.escalatedAt">
              升级为严重：{{ formatDateTime(alert.escalatedAt) }}
            </span>
            <span v-if="alert.handlerName">
              由 {{ alert.handlerName }} 跟进中
            </span>
          </div>
        </div>
        <div class="alert-item__actions">
          <el-button
            v-if="!alert.handlerName"
            size="small"
            plain
            v-permission="ALERT_PERMISSION"
            @click="onClaim(alert)"
          >
            我来跟进
          </el-button>
          <el-button
            size="small"
            type="primary"
            plain
            v-permission="ALERT_PERMISSION"
            @click="onResolve(alert)"
          >
            已处理
          </el-button>
          <el-button
            size="small"
            type="info"
            plain
            v-permission="ALERT_PERMISSION"
            @click="onDismiss(alert)"
          >
            忽略
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="historyAlerts.length > 0" class="task-alert-panel__history">
      <el-link
        type="info"
        :underline="false"
        @click="historyOpen = !historyOpen"
      >
        {{ historyOpen ? '收起' : '展开' }}历史预警（{{
          historyAlerts.length
        }}
        条）
      </el-link>
      <el-table
        v-if="historyOpen"
        :data="historyAlerts"
        border
        size="small"
        style="margin-top: 8px"
      >
        <el-table-column label="预警" min-width="150">
          <template #default="{ row }">
            {{ row.ruleName || row.ruleCode }}
          </template>
        </el-table-column>
        <el-table-column label="级别" width="80" align="center">
          <template #default="{ row }">
            <el-tag
              size="small"
              effect="plain"
              :type="row.level === 2 ? 'danger' : 'warning'"
            >
              {{ row.levelLabel || (row.level === 2 ? '严重' : '关注') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="结果" width="110" align="center">
          <template #default="{ row }">
            {{ row.statusLabel || '--' }}
          </template>
        </el-table-column>
        <el-table-column label="处置时间" min-width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.resolvedAt) || '--' }}
          </template>
        </el-table-column>
        <el-table-column label="说明" min-width="180">
          <template #default="{ row }">
            {{ row.resolveRemark || '--' }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { CircleCheck } from '@element-plus/icons-vue';
  import {
    claimTaskAlert,
    dismissTaskAlert,
    listTaskAlerts,
    resolveTaskAlert
  } from '@/api/operation/task-alert';
  import type { TaskAlert } from '@/api/operation/task-alert/model';
  import { formatDateTime } from '@/utils/date-util';
  import { formatDurationMinutes } from '../alert-config';

  const props = defineProps<{ taskId?: number | null }>();
  const emit = defineEmits<{ (e: 'changed'): void }>();

  /** 认领 / 处理 / 忽略共用同一个权限点，调度员要么全能处置要么只读 */
  const ALERT_PERMISSION = 'operation:task:alert-handle';

  const loading = ref(false);
  const alerts = ref<TaskAlert[]>([]);
  const historyOpen = ref(false);

  const activeAlerts = computed(() =>
    alerts.value.filter((a) => a.status === 0)
  );
  const historyAlerts = computed(() =>
    alerts.value.filter((a) => a.status !== 0)
  );

  const reload = async () => {
    if (!props.taskId) {
      alerts.value = [];
      return;
    }
    loading.value = true;
    try {
      alerts.value = await listTaskAlerts(props.taskId);
    } catch {
      // 预警只是辅助信息，拉取失败不打断详情主体，静默降级为空
      alerts.value = [];
    } finally {
      loading.value = false;
    }
  };

  watch(() => props.taskId, reload, { immediate: true });

  const runAction = async (fn: () => Promise<unknown>, okMsg: string) => {
    try {
      await fn();
      EleMessage.success({ message: okMsg, plain: true });
      await reload();
      emit('changed');
    } catch (e: unknown) {
      const msg =
        (e as { message?: string }).message || '操作失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const onClaim = (alert: TaskAlert) =>
    runAction(() => claimTaskAlert(alert.id), '已认领，这条预警由你跟进');

  const onResolve = async (alert: TaskAlert) => {
    let remark = '';
    try {
      const res = await ElMessageBox.prompt(
        '确认这条预警已经跟进完成？可以写一句处理结果，方便日后复盘。',
        '标记已处理',
        {
          confirmButtonText: '确认已处理',
          cancelButtonText: '再想想',
          inputPlaceholder: '例如：已联系承运商，车辆 30 分钟内到场',
          inputValidator: () => true
        }
      );
      remark = res.value?.trim() || '';
    } catch {
      return;
    }
    await runAction(
      () => resolveTaskAlert(alert.id, remark || undefined),
      '已标记处理'
    );
  };

  const onDismiss = async (alert: TaskAlert) => {
    let reason = '';
    try {
      const res = await ElMessageBox.prompt(
        '忽略后这条预警不再提醒，请填写原因便于后续复盘。',
        '忽略预警',
        {
          confirmButtonText: '确认忽略',
          cancelButtonText: '取消',
          inputPlaceholder: '例如：客户已同意延后到货，无需催办',
          inputValidator: (v: string) =>
            (v || '').trim().length > 0 || '请填写忽略原因'
        }
      );
      reason = res.value.trim();
    } catch {
      return;
    }
    await runAction(() => dismissTaskAlert(alert.id, reason), '已忽略');
  };

  defineExpose({ reload });
</script>

<style lang="scss" scoped>
  .task-alert-panel {
    &__empty {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 10px 12px;
      border-radius: 8px;
      background: var(--el-color-success-light-9);
      color: var(--el-text-color-secondary);
      font-size: 13px;
    }

    &__empty-icon {
      color: var(--el-color-success);
      font-size: 15px;
    }

    &__list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    &__history {
      margin-top: 10px;
    }
  }

  .alert-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid var(--el-border-color-lighter);
    /* 左侧色条把级别做成扫一眼就能分辨的形状，而不只靠标签颜色 */
    border-left-width: 3px;

    &--warn {
      border-left-color: var(--el-color-warning);
      background: var(--el-color-warning-light-9);
    }

    &--critical {
      border-left-color: var(--el-color-danger);
      background: var(--el-color-danger-light-9);
    }

    &__main {
      flex: 1 1 auto;
      min-width: 0;
    }

    &__title {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
    }

    &__rule {
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    &__meta {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 4px;
      font-size: 12px;
    }

    &__overdue {
      color: var(--el-color-danger);
      font-weight: 500;
    }

    &__actions {
      flex-shrink: 0;
      display: inline-flex;
      gap: 6px;
    }
  }
</style>
