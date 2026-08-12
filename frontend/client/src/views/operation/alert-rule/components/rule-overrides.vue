<!--
  预警规则 · 覆盖规则

  默认阈值管全公司，这一屏管例外：某个客户要得更急、某条长途线路本来就该给更多时间、
  社会运力要盯得更紧。命中多条时后端按「越具体越优先」选一条生效，
  所以这里把适用范围直接摆在卡片上。
-->
<template>
  <div class="rule-overrides">
    <div class="rule-overrides__bar">
      <el-select
        v-model="filterRuleCode"
        placeholder="全部预警类型"
        clearable
        class="rule-overrides__filter"
        @change="reload"
      >
        <el-option
          v-for="item in catalog"
          :key="item.ruleCode"
          :value="item.ruleCode"
          :label="item.ruleName"
        />
      </el-select>
      <el-button
        type="primary"
        :icon="Plus"
        v-permission="'operation:alert-rule:add'"
        @click="openEdit()"
      >
        新增覆盖规则
      </el-button>
    </div>

    <div v-loading="loading" class="rule-overrides__list">
      <article
        v-for="row in rows"
        :key="row.id"
        class="override-card"
        :class="{ 'is-off': row.status !== 1 }"
      >
        <header class="override-card__head">
          <div class="override-card__identity">
            <h3 class="override-card__title">
              {{ row.ruleName?.trim() || ruleName(row) }}
            </h3>
            <p
              v-if="
                row.ruleName?.trim() &&
                row.ruleName.trim() !== catalogOf(row.ruleCode)?.ruleName
              "
              class="override-card__type"
            >
              {{ ruleName(row) }}
            </p>
          </div>
          <span
            class="override-card__status"
            :class="row.status === 1 ? 'is-on' : 'is-off'"
          >
            {{ row.status === 1 ? '生效中' : '已停用' }}
          </span>
        </header>

        <div class="override-card__scope">
          <span class="override-card__scope-label">适用范围</span>
          <span>{{ row.scopeSummary || '全部任务' }}</span>
        </div>

        <template v-if="kindOf(row) === 'deadline'">
          <threshold-track
            v-if="row.planEnabled !== false"
            compact
            kind="deadline"
            :warn-ahead-minutes="row.warnAheadMinutes"
            :critical-after-minutes="row.criticalAfterMinutes"
          />
          <threshold-track
            v-if="row.requiredEnabled !== false"
            compact
            kind="deadline"
            :warn-ahead-minutes="row.warnAheadRequiredMinutes"
            :critical-after-minutes="row.criticalAfterRequiredMinutes"
          />
        </template>
        <threshold-track
          v-else-if="kindOf(row) !== 'execution'"
          compact
          :kind="kindOf(row)"
          :warn-ahead-minutes="row.warnAheadMinutes"
          :critical-after-minutes="row.criticalAfterMinutes"
          :anchor-offset-minutes="row.anchorOffsetMinutes"
          :stagnant-hours="row.stagnantHours"
        />
        <p v-else class="override-card__instant">命中即提醒，没有时间阈值</p>

        <footer class="override-card__foot">
          <span class="override-card__threshold">{{ thresholdText(row) }}</span>
          <div class="override-card__actions">
            <button
              type="button"
              class="override-card__action"
              v-permission="'operation:alert-rule:edit'"
              @click="openEdit(row)"
            >
              编辑
            </button>
            <button
              type="button"
              class="override-card__action is-danger"
              v-permission="'operation:alert-rule:delete'"
              @click="remove(row)"
            >
              删除
            </button>
          </div>
        </footer>
      </article>

      <div v-if="!loading && rows.length === 0" class="rule-overrides__empty">
        <div class="rule-overrides__empty-track" aria-hidden="true">
          <span class="is-ok"></span>
          <span class="is-warn"></span>
          <span class="is-crit"></span>
        </div>
        <p class="rule-overrides__empty-title">还没有覆盖规则</p>
        <p class="rule-overrides__empty-desc">
          全部任务都按「默认阈值」提醒。某个客户要得更严、某条长途该多给时间时，再单独加一条。
        </p>
        <el-button
          type="primary"
          :icon="Plus"
          v-permission="'operation:alert-rule:add'"
          @click="openEdit()"
        >
          新增覆盖规则
        </el-button>
      </div>
    </div>

    <div v-if="total > pageSize" class="rule-overrides__pager">
      <el-pagination
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="page"
        @current-change="onPageChange"
      />
    </div>

    <rule-edit
      v-model:visible="editVisible"
      :data="editData"
      :catalog="catalog"
      @done="reload"
    />
  </div>
</template>

<script lang="ts" setup>
  import { onMounted, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { Plus } from '@element-plus/icons-vue';
  import {
    getTaskAlertCatalog,
    pageTaskAlertRules,
    removeTaskAlertRule
  } from '@/api/operation/task-alert';
  import type {
    TaskAlertRule,
    TaskAlertRuleCatalogItem
  } from '@/api/operation/task-alert/model';
  import { alertStageLabel, summarizeThreshold } from '../../task/alert-config';
  import RuleEdit from './rule-edit.vue';
  import ThresholdTrack from './threshold-track.vue';

  const loading = ref(false);
  const rows = ref<TaskAlertRule[]>([]);
  const catalog = ref<TaskAlertRuleCatalogItem[]>([]);
  const filterRuleCode = ref<string | undefined>(undefined);
  const page = ref(1);
  const pageSize = 20;
  const total = ref(0);

  const editVisible = ref(false);
  const editData = ref<TaskAlertRule | null>(null);

  const catalogOf = (code: string) =>
    catalog.value.find((c) => c.ruleCode === code);

  const kindOf = (row: TaskAlertRule) =>
    catalogOf(row.ruleCode)?.kind ?? 'deadline';

  const ruleName = (row: TaskAlertRule) => {
    const name =
      catalogOf(row.ruleCode)?.ruleName || row.ruleName || row.ruleCode;
    return row.stage != null
      ? `${name}（${alertStageLabel(row.stage)}）`
      : name;
  };

  const thresholdText = (row: TaskAlertRule): string => {
    const kind = kindOf(row);
    const text = summarizeThreshold({
      kind,
      warnAheadMinutes: row.warnAheadMinutes,
      criticalAfterMinutes: row.criticalAfterMinutes,
      warnAheadRequiredMinutes: row.warnAheadRequiredMinutes,
      criticalAfterRequiredMinutes: row.criticalAfterRequiredMinutes,
      anchorOffsetMinutes: row.anchorOffsetMinutes,
      stagnantHours: row.stagnantHours,
      planEnabled: row.planEnabled,
      requiredEnabled: row.requiredEnabled
    });
    return text;
  };

  const reload = async () => {
    loading.value = true;
    try {
      const res = await pageTaskAlertRules({
        page: page.value,
        limit: pageSize,
        ruleCode: filterRuleCode.value,
        // 默认阈值那批在「默认阈值」页维护，这里只要带适用范围的覆盖规则
        isDefault: false
      });
      rows.value = res?.list ?? [];
      total.value = res?.count ?? 0;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '加载失败，请刷新重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const onPageChange = (p: number) => {
    page.value = p;
    reload();
  };

  const openEdit = (row?: TaskAlertRule) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const remove = async (row: TaskAlertRule) => {
    try {
      await ElMessageBox.confirm(
        `删除后「${ruleName(row)}」的这条例外不再生效，相关任务会回到默认阈值。`,
        '删除覆盖规则',
        { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    try {
      await removeTaskAlertRule(row.id!);
      EleMessage.success({ message: '已删除', plain: true });
      await reload();
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '删除失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    }
  };

  onMounted(async () => {
    try {
      catalog.value = await getTaskAlertCatalog();
    } catch {
      catalog.value = [];
    }
    await reload();
  });

  defineExpose({ reload });
</script>

<style lang="scss" scoped>
  .rule-overrides {
    &__bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }

    &__filter {
      width: 220px;
    }

    &__list {
      display: flex;
      flex-direction: column;
      gap: 10px;
      min-height: 120px;
    }

    &__empty {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 48px 16px 40px;
      text-align: center;
    }

    &__empty-track {
      display: flex;
      width: 160px;
      height: 8px;
      border-radius: 999px;
      overflow: hidden;
      margin-bottom: 16px;

      span {
        flex: 1;
      }

      .is-ok {
        flex: 1.4;
        background: color-mix(
          in srgb,
          var(--el-color-success) 22%,
          var(--el-fill-color)
        );
      }

      .is-warn {
        background: color-mix(
          in srgb,
          var(--el-color-warning) 28%,
          var(--el-fill-color)
        );
      }

      .is-crit {
        flex: 0.7;
        background: color-mix(
          in srgb,
          var(--el-color-danger) 26%,
          var(--el-fill-color)
        );
      }
    }

    &__empty-title {
      margin: 0 0 6px;
      font-size: 15px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    &__empty-desc {
      margin: 0 0 16px;
      max-width: 360px;
      font-size: 13px;
      line-height: 1.6;
      color: var(--el-text-color-secondary);
    }

    &__pager {
      display: flex;
      justify-content: flex-end;
      margin-top: 12px;
    }
  }

  .override-card {
    padding: 14px 16px 12px;
    border-radius: 12px;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-bg-color);
    transition: opacity 200ms ease;

    &.is-off {
      opacity: 0.62;
    }

    &__head {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 8px;
    }

    &__identity {
      flex: 1 1 auto;
      min-width: 0;
    }

    &__title {
      margin: 0;
      font-size: 15px;
      font-weight: 600;
      letter-spacing: -0.01em;
      line-height: 1.3;
      color: var(--el-text-color-primary);
    }

    &__type {
      margin: 3px 0 0;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }

    &__status {
      flex-shrink: 0;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.02em;

      &.is-on {
        background: var(--el-color-success-light-9);
        color: var(--el-color-success);
      }

      &.is-off {
        background: var(--el-fill-color);
        color: var(--el-text-color-secondary);
      }
    }

    &__scope {
      display: flex;
      align-items: baseline;
      gap: 8px;
      margin-bottom: 10px;
      font-size: 13px;
      color: var(--el-text-color-primary);
      line-height: 1.5;
    }

    &__scope-label {
      flex-shrink: 0;
      font-size: 12px;
      color: var(--el-text-color-placeholder);
    }

    &__instant {
      margin: 0 0 8px;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }

    &__foot {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-top: 4px;
    }

    &__threshold {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      line-height: 1.5;
    }

    &__actions {
      display: inline-flex;
      gap: 12px;
      flex-shrink: 0;
    }

    &__action {
      margin: 0;
      padding: 0;
      border: none;
      background: none;
      color: var(--el-color-primary);
      font-size: 13px;
      cursor: pointer;
      transition:
        opacity 140ms ease,
        transform 100ms ease-out;

      &:hover {
        opacity: 0.8;
      }

      &:active {
        transform: scale(0.97);
      }

      &:focus-visible {
        outline: 2px solid var(--el-color-primary);
        outline-offset: 2px;
        border-radius: 4px;
      }

      &.is-danger {
        color: var(--el-color-danger);
      }
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .override-card,
    .override-card__action {
      transition: none;
    }
  }
</style>
