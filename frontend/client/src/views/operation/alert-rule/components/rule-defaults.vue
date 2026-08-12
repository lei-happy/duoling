<!--
  预警规则 · 默认阈值

  这一屏管的是「全公司统一的那把尺子」。每种预警类型都自带一套系统默认值，
  开箱即用；这里改的是租户级覆盖值，改完下一轮预警计算就生效。

  关掉开关 = 这种预警对本公司整体停用（后端把「默认那一行停用」当作类型级开关）。
-->
<template>
  <div class="rule-defaults" v-loading="loading">
    <div class="rule-defaults__seg" role="tablist" aria-label="规则分类">
      <button
        v-for="group in groups"
        :key="group.key"
        type="button"
        role="tab"
        class="rule-defaults__seg-btn"
        :class="[`is-${group.key}`, { 'is-active': activeGroup === group.key }]"
        :aria-selected="activeGroup === group.key"
        @click="activeGroup = group.key"
      >
        {{ group.title }}
        <span class="rule-defaults__seg-count">{{ group.rows.length }}</span>
        <span
          v-if="group.rows.some((r) => r.dirty)"
          class="rule-defaults__seg-dot"
          aria-label="有未保存的修改"
        ></span>
      </button>
    </div>
    <p v-if="activeMeta" class="rule-defaults__hint">{{ activeMeta.hint }}</p>

    <div class="rule-defaults__list">
      <rule-card
        v-for="row in activeRows"
        :key="row.key"
        :row="row"
        @change="markDirty(row)"
        @toggle="saveToggle(row)"
        @reset="resetRow(row)"
        @save="saveRow(row)"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref, watch } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import {
    addTaskAlertRule,
    getTaskAlertCatalog,
    listTaskAlertRuleDefaults,
    removeTaskAlertRule,
    updateTaskAlertRule
  } from '@/api/operation/task-alert';
  import type {
    TaskAlertRule,
    TaskAlertRuleCatalogItem
  } from '@/api/operation/task-alert/model';
  import {
    ALERT_KIND_GROUPS,
    alertStageLabel,
    clocksFromTimeBasis,
    deriveTimeBasis
  } from '../../task/alert-config';
  import RuleCard from './rule-card.vue';
  import type { DefaultRuleRow } from './rule-card.vue';

  const loading = ref(false);
  const rows = ref<DefaultRuleRow[]>([]);
  const activeGroup = ref(ALERT_KIND_GROUPS[0].key);

  const groups = computed(() =>
    ALERT_KIND_GROUPS.map((g) => ({
      ...g,
      rows: rows.value.filter((r) => (g.kinds as string[]).includes(r.kind))
    })).filter((g) => g.rows.length > 0)
  );

  const activeMeta = computed(
    () =>
      groups.value.find((g) => g.key === activeGroup.value) ?? groups.value[0]
  );

  const activeRows = computed(() => activeMeta.value?.rows ?? []);

  watch(groups, (list) => {
    if (!list.some((g) => g.key === activeGroup.value) && list[0]) {
      activeGroup.value = list[0].key;
    }
  });

  const markDirty = (row: DefaultRuleRow) => {
    row.dirty = true;
  };

  const buildRows = (
    catalog: TaskAlertRuleCatalogItem[],
    defaults: TaskAlertRule[]
  ): DefaultRuleRow[] => {
    const byKey = new Map<string, TaskAlertRule>();
    for (const d of defaults) {
      byKey.set(`${d.ruleCode}:${d.stage ?? ''}`, d);
    }
    const out: DefaultRuleRow[] = [];
    for (const item of catalog) {
      // 滞留类每个阶段一把尺子：在途拖 48 小时正常，待发车拖 6 小时就该催了
      const stages = item.stageScoped ? item.stages : [null];
      for (const stage of stages) {
        const key = `${item.ruleCode}:${stage ?? ''}`;
        const saved = byKey.get(key);
        const builtInStagnant =
          stage != null
            ? item.defaults.stagnantHours?.[String(stage)]
            : undefined;
        out.push({
          key,
          ruleCode: item.ruleCode,
          ruleName: item.ruleName,
          kind: item.kind,
          description: item.description,
          stage,
          supportsTimeBasis: item.supportsTimeBasis,
          ruleId: saved?.id,
          enabled: saved ? saved.status === 1 : true,
          timeBasis: saved?.timeBasis ?? item.defaults.timeBasis,
          planEnabled:
            saved?.planEnabled ??
            item.defaults.planEnabled ??
            clocksFromTimeBasis(saved?.timeBasis ?? item.defaults.timeBasis)
              .planEnabled,
          requiredEnabled:
            saved?.requiredEnabled ??
            item.defaults.requiredEnabled ??
            clocksFromTimeBasis(saved?.timeBasis ?? item.defaults.timeBasis)
              .requiredEnabled,
          anchorOffsetMinutes:
            saved?.anchorOffsetMinutes ??
            item.defaults.anchorOffsetMinutes ??
            undefined,
          warnAheadMinutes:
            saved?.warnAheadMinutes ?? item.defaults.warnAheadMinutes ?? 0,
          // 滞留类的内置默认是「再拖一倍时长转严重」，这里展开成具体分钟数，
          // 否则输入框里的 0 会被读成「一到点就算严重」，与实际行为相反
          criticalAfterMinutes:
            saved?.criticalAfterMinutes ??
            (item.kind === 'stagnant'
              ? (builtInStagnant ?? 0) * 60
              : (item.defaults.criticalAfterMinutes ?? 0)),
          warnAheadRequiredMinutes:
            saved?.warnAheadRequiredMinutes ??
            item.defaults.warnAheadRequiredMinutes ??
            item.defaults.warnAheadMinutes ??
            0,
          criticalAfterRequiredMinutes:
            saved?.criticalAfterRequiredMinutes ??
            item.defaults.criticalAfterRequiredMinutes ??
            item.defaults.criticalAfterMinutes ??
            0,
          stagnantHours: saved?.stagnantHours ?? builtInStagnant ?? undefined,
          builtIn: item.defaults,
          dirty: false,
          saving: false
        });
      }
    }
    return out;
  };

  const reload = async () => {
    loading.value = true;
    try {
      const [catalog, defaults] = await Promise.all([
        getTaskAlertCatalog(),
        listTaskAlertRuleDefaults()
      ]);
      rows.value = buildRows(catalog, defaults);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '加载失败，请刷新重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const toPayload = (row: DefaultRuleRow): TaskAlertRule => ({
    ruleCode: row.ruleCode,
    ruleName: row.ruleName,
    stage: row.stage,
    timeBasis: deriveTimeBasis(row.planEnabled, row.requiredEnabled),
    planEnabled: row.planEnabled,
    requiredEnabled: row.requiredEnabled,
    anchorOffsetMinutes:
      row.kind === 'anchor' ? (row.anchorOffsetMinutes ?? null) : null,
    warnAheadMinutes:
      row.kind === 'stagnant' ? null : (row.warnAheadMinutes ?? 0),
    criticalAfterMinutes:
      row.kind === 'execution' ? null : (row.criticalAfterMinutes ?? 0),
    warnAheadRequiredMinutes: row.supportsTimeBasis
      ? (row.warnAheadRequiredMinutes ?? 0)
      : null,
    criticalAfterRequiredMinutes: row.supportsTimeBasis
      ? (row.criticalAfterRequiredMinutes ?? 0)
      : null,
    stagnantHours: row.kind === 'stagnant' ? (row.stagnantHours ?? null) : null,
    priority: 0,
    status: row.enabled ? 1 : 0
  });

  const rowLabel = (row: DefaultRuleRow) =>
    row.kind === 'stagnant' && row.stage != null
      ? `${alertStageLabel(row.stage)}滞留`
      : row.ruleName;

  const applyBuiltIn = (row: DefaultRuleRow) => {
    const b = row.builtIn;
    const builtInStagnant =
      row.stage != null ? b.stagnantHours?.[String(row.stage)] : undefined;
    row.ruleId = undefined;
    row.enabled = true;
    row.timeBasis = b.timeBasis;
    row.planEnabled = b.planEnabled ?? true;
    row.requiredEnabled = b.requiredEnabled ?? true;
    row.anchorOffsetMinutes = b.anchorOffsetMinutes ?? undefined;
    row.warnAheadMinutes = b.warnAheadMinutes ?? 0;
    row.criticalAfterMinutes =
      row.kind === 'stagnant'
        ? (builtInStagnant ?? 0) * 60
        : (b.criticalAfterMinutes ?? 0);
    row.warnAheadRequiredMinutes =
      b.warnAheadRequiredMinutes ?? b.warnAheadMinutes ?? 0;
    row.criticalAfterRequiredMinutes =
      b.criticalAfterRequiredMinutes ?? b.criticalAfterMinutes ?? 0;
    row.stagnantHours = builtInStagnant;
    row.dirty = false;
  };

  const persistRow = async (row: DefaultRuleRow): Promise<boolean> => {
    if (row.saving) return false;
    row.saving = true;
    try {
      const payload = toPayload(row);
      if (row.ruleId) {
        await updateTaskAlertRule(row.ruleId, payload);
      } else {
        const created = await addTaskAlertRule(payload);
        row.ruleId = created?.id;
      }
      row.dirty = false;
      return true;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '保存失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
      return false;
    } finally {
      row.saving = false;
    }
  };

  const saveToggle = async (row: DefaultRuleRow) => {
    if (row.saving) return;
    const enabled = row.enabled;
    const ok = await persistRow(row);
    if (!ok) {
      row.enabled = !enabled;
      return;
    }
    EleMessage.success({
      message: enabled
        ? `「${rowLabel(row)}」已启用，下一轮预警计算即生效`
        : `「${rowLabel(row)}」已停用，全公司不再提醒`,
      plain: true
    });
  };

  const saveRow = async (row: DefaultRuleRow) => {
    if (row.saving) return;
    const ok = await persistRow(row);
    if (!ok) return;
    EleMessage.success({
      message: `「${rowLabel(row)}」已保存，下一轮预警计算即按新阈值执行`,
      plain: true
    });
  };

  const resetRow = async (row: DefaultRuleRow) => {
    try {
      await ElMessageBox.confirm(
        `恢复后「${rowLabel(row)}」将改用系统默认阈值，本公司的自定义设置会被清除。`,
        '恢复系统默认',
        {
          type: 'warning',
          confirmButtonText: '恢复默认',
          cancelButtonText: '取消'
        }
      );
    } catch {
      return;
    }
    try {
      await removeTaskAlertRule(row.ruleId!);
      applyBuiltIn(row);
      EleMessage.success({ message: '已恢复系统默认', plain: true });
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '操作失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    }
  };

  onMounted(reload);

  defineExpose({ reload });
</script>

<style lang="scss" scoped>
  .rule-defaults {
    padding-bottom: 8px;

    &__seg {
      display: inline-flex;
      padding: 3px;
      border-radius: 10px;
      background: var(--el-fill-color);
    }

    &__seg-btn {
      position: relative;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin: 0;
      padding: 6px 14px;
      border: none;
      border-radius: 8px;
      background: transparent;
      color: var(--el-text-color-regular);
      font-size: 13px;
      font-weight: 500;
      line-height: 1.3;
      cursor: pointer;
      transition:
        background 140ms ease,
        color 140ms ease,
        box-shadow 140ms ease,
        transform 100ms ease-out;

      &.is-active {
        box-shadow: none;
        font-weight: 600;

        .rule-defaults__seg-count {
          color: inherit;
          opacity: 0.72;
        }
      }

      &.is-sla.is-active {
        background: color-mix(
          in srgb,
          var(--el-color-primary) 16%,
          var(--el-bg-color)
        );
        color: var(--el-color-primary);
      }

      &.is-stagnant.is-active {
        background: color-mix(
          in srgb,
          var(--el-color-warning) 18%,
          var(--el-bg-color)
        );
        color: var(--el-color-warning);
      }

      &.is-execution.is-active {
        background: color-mix(
          in srgb,
          var(--el-color-danger) 16%,
          var(--el-bg-color)
        );
        color: var(--el-color-danger);
      }

      &:hover:not(.is-active) {
        color: var(--el-text-color-primary);
      }

      &:active {
        transform: scale(0.97);
      }

      &:focus-visible {
        outline: 2px solid var(--el-color-primary);
        outline-offset: 1px;
      }
    }

    &__seg-count {
      font-variant-numeric: tabular-nums;
      font-size: 12px;
      color: var(--el-text-color-placeholder);
    }

    &__seg-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--el-color-primary);
    }

    &__hint {
      margin: 10px 0 14px;
      font-size: 13px;
      line-height: 1.6;
      color: var(--el-text-color-secondary);
    }

    &__list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .rule-defaults__seg-btn {
      transition: none;
    }
  }
</style>
