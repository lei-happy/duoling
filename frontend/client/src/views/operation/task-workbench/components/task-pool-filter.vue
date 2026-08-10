<!--
  调度工作台 - 筛选栏（按阶段池动态渲染）

  字段不再是全阶段并集：由 `WorkbenchPool.filterFields` 声明本阶段关心哪些条件，
  字段本身的标签 / 控件类型 / 栅格 / 取参逻辑都在 workbench-filter-registry 里描述。

  布局按固定槽位渲染（详见 registry 头部注释）：共有字段锚定第一行前三格，池专属
  字段顺延，时间维度 + 日期区间 + 按钮独占末行，切阶段不会让控件换位置。

  切换阶段时：公共字段（单号、出发地、目的地）保留已填值，池专属字段清空，
  **时间维度与时间范围一律保留**——时间维度曾随阶段自动改写，导致同一张 KPI 卡
  在切换阶段前后数字对不上（详见 workbench-time-filter.ts）。

  时间默认不限：工作台是「待办全集」视角，默认加时间窗会把最该处理的滞留任务藏起来。
-->
<template>
  <ele-card search-form class="wb-filter-card">
    <el-form
      class="wb-filter"
      label-width="0"
      @keyup.enter="emitSearch"
      @submit.prevent=""
    >
      <el-row :gutter="10" class="wb-filter__row">
        <el-col
          v-for="field in visibleFields"
          :key="field.id"
          :lg="field.col.lg"
          :md="field.col.md"
          :sm="field.col.sm"
          :xs="field.col.xs"
        >
          <floating-label
            v-if="field.kind === 'input'"
            v-model.trim="form[field.id as FilterTextKey]"
            :label="field.label"
            type="input"
            clearable
          />
          <floating-label
            v-else-if="field.kind === 'select'"
            v-model="form[field.id as FilterNumberKey]"
            :label="field.label"
            type="select"
            clearable
          >
            <el-option
              v-for="o in field.options"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </floating-label>
          <floating-label
            v-else
            v-model="form[field.id as FilterNumberKey]"
            :label="field.label"
            type="select"
            filterable
            remote
            clearable
            :remote-method="(kw: string) => runRemoteSearch(field, kw)"
          >
            <el-option
              v-for="o in remoteOptions[field.id] || []"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </floating-label>
        </el-col>

        <el-col
          :lg="TIME_FIELD_COL.lg"
          :md="TIME_FIELD_COL.md"
          :sm="TIME_FIELD_COL.sm"
          :xs="TIME_FIELD_COL.xs"
        >
          <floating-label
            v-model="timeField"
            label="时间类型"
            type="select"
            :clearable="false"
          >
            <el-option
              v-for="o in TASK_TIME_FIELD_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            >
              <span>{{ o.label }}</span>
              <span v-if="o.nodeScoped" class="wb-filter__opt-hint">
                仅已走到该节点
              </span>
            </el-option>
          </floating-label>
        </el-col>
        <el-col
          :lg="TIME_RANGE_COL.lg"
          :md="TIME_RANGE_COL.md"
          :sm="TIME_RANGE_COL.sm"
          :xs="TIME_RANGE_COL.xs"
        >
          <floating-label
            v-model="timeRange"
            :label="timeRangeLabel"
            type="date"
            date-type="daterange"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            unlink-panels
            start-placeholder="开始"
            end-placeholder="结束"
            :shortcuts="TIME_RANGE_SHORTCUTS"
          />
        </el-col>
        <el-col
          :lg="ACTIONS_COL.lg"
          :md="ACTIONS_COL.md"
          :sm="ACTIONS_COL.sm"
          :xs="ACTIONS_COL.xs"
          class="wb-filter__col-actions"
        >
          <el-form-item label-width="0px">
            <btn-items
              :wrap="false"
              :items="[
                { preset: 'search', onClick: () => emitSearch() },
                { preset: 'reset', onClick: () => onReset() }
              ]"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <div v-if="nodeScopedHint" class="wb-filter__hint">
        <el-icon><InfoFilled /></el-icon>
        <span>{{ nodeScopedHint }}</span>
        <el-link
          type="primary"
          :underline="false"
          class="wb-filter__hint-action"
          @click="useStableTimeField"
        >
          改回「进入当前阶段」
        </el-link>
      </div>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref, watch } from 'vue';
  import { InfoFilled } from '@element-plus/icons-vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import type { TaskParam, TaskTimeField } from '@/api/operation/task/model';
  import {
    DEFAULT_TASK_TIME_FIELD,
    TASK_TIME_FIELD_OPTIONS,
    TIME_RANGE_SHORTCUTS,
    isNodeScopedTimeField,
    timeFieldLabel
  } from '../workbench-time-filter';
  import { getWorkbenchPool, WORKBENCH_POOLS } from '../workbench-pool-registry';
  import {
    ACTIONS_COL,
    TIME_FIELD_COL,
    TIME_RANGE_COL,
    buildFilterFormDefaults,
    resetNonStickyFields,
    resolveVisibleFilterFields
  } from '../workbench-filter-registry';
  import type {
    RemoteOption,
    WorkbenchFilterField,
    WorkbenchFilterForm
  } from '../workbench-filter-registry';

  const props = withDefaults(
    defineProps<{
      /** 当前阶段卡 key，决定渲染哪些筛选字段与默认时间维度 */
      poolKey?: string;
      /** 路由带入的任务单号，初始化筛选栏 */
      initialKeyword?: string;
    }>(),
    { poolKey: 'pending-assign', initialKeyword: '' }
  );

  const emit = defineEmits<{
    (e: 'search', where: Partial<TaskParam>): void;
    (e: 'reset', where: Partial<TaskParam>): void;
  }>();

  type FilterTextKey = {
    [K in keyof WorkbenchFilterForm]: WorkbenchFilterForm[K] extends string
      ? K
      : never;
  }[keyof WorkbenchFilterForm];

  type FilterNumberKey = Exclude<keyof WorkbenchFilterForm, FilterTextKey>;

  const pool = computed(
    () => getWorkbenchPool(props.poolKey) ?? WORKBENCH_POOLS[0]!
  );

  const form = reactive<WorkbenchFilterForm>(buildFilterFormDefaults());
  const timeField = ref<TaskTimeField>(DEFAULT_TASK_TIME_FIELD);
  /** 默认不限时间：工作台要能看到所有待办，尤其是停留最久的那批 */
  const timeRange = ref<[string, string] | null>(null);

  const remoteOptions = reactive<Record<string, RemoteOption[]>>({});

  /** 本池字段按全局槽位次序排列（共有字段锚定在前，timeRange 由模板固定渲染在末行） */
  const visibleFields = computed<WorkbenchFilterField[]>(() =>
    resolveVisibleFilterFields(pool.value.filterFields, form)
  );

  const timeRangeLabel = computed(
    () => `请选择${timeFieldLabel(timeField.value)}（默认不限）`
  );

  /** 选了节点维度且真的在筛时间时，说明清楚为什么别的阶段数字会变少 */
  const nodeScopedHint = computed(() => {
    if (!isNodeScopedTimeField(timeField.value)) return '';
    const range = timeRange.value;
    if (!Array.isArray(range) || !range[0] || !range[1]) return '';
    return `当前按「${timeFieldLabel(timeField.value)}」筛选，只统计已经走到这一步的任务，还没走到的阶段会显示为 0。`;
  });

  const useStableTimeField = () => {
    timeField.value = DEFAULT_TASK_TIME_FIELD;
    emitSearch();
  };

  const runRemoteSearch = async (field: WorkbenchFilterField, kw: string) => {
    if (!field.search) return;
    try {
      remoteOptions[field.id] = await field.search(kw);
    } catch {
      remoteOptions[field.id] = [];
    }
  };

  const buildWhere = (): Partial<TaskParam> => {
    const payload: Partial<TaskParam> = {};
    for (const field of visibleFields.value) {
      Object.assign(payload, field.toParam(form));
    }
    const range = timeRange.value;
    if (Array.isArray(range) && range.length === 2 && range[0] && range[1]) {
      payload.timeField = timeField.value;
      payload.timeStart = range[0];
      payload.timeEnd = range[1];
    }
    return payload;
  };

  const lastEmitted = ref('');

  const emitSearch = () => {
    const where = buildWhere();
    lastEmitted.value = JSON.stringify(where);
    emit('search', where);
  };

  const onReset = () => {
    Object.assign(form, buildFilterFormDefaults());
    timeField.value = DEFAULT_TASK_TIME_FIELD;
    timeRange.value = null;
    const where = buildWhere();
    lastEmitted.value = JSON.stringify(where);
    emit('reset', where);
  };

  /**
   * 切换阶段：只清空本阶段不再使用的池专属字段，时间维度与范围保持用户的选择。
   * 仅在最终查询条件真的变化时才重新发起搜索，避免与列表自身的切池刷新重复请求。
   */
  watch(
    () => pool.value.key,
    () => {
      Object.assign(
        form,
        resetNonStickyFields(form, pool.value.filterFields)
      );
      const where = buildWhere();
      const next = JSON.stringify(where);
      if (next !== lastEmitted.value) {
        lastEmitted.value = next;
        emit('search', where);
      }
    }
  );

  /** 承运方式切走「承运商」时，已选承运商失效 */
  watch(
    () => form.carrierType,
    (v) => {
      if (v !== 2) form.carrierId = void 0;
    }
  );

  onMounted(() => {
    const kw = props.initialKeyword?.trim();
    if (kw) form.keyword = kw;
    emitSearch();
  });
</script>

<style scoped>
  .wb-filter__row {
    row-gap: 12px;
  }

  .wb-filter__hint {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 10px;
    font-size: 13px;
    line-height: 1.5;
    color: var(--el-text-color-secondary);
  }

  .wb-filter__hint .el-icon {
    color: var(--el-color-warning);
  }

  .wb-filter__hint-action {
    font-size: 13px;
  }

  .wb-filter__col-actions :deep(.el-form-item) {
    margin-bottom: 0;
    display: flex;
    justify-content: flex-start;
  }

  .wb-filter__col-actions :deep(.el-form-item__content) {
    justify-content: flex-start;
    flex-wrap: nowrap;
  }
</style>

<style>
  .wb-filter-card.wb-filter-card {
    padding-bottom: 6px;
  }

  .wb-filter .floating-label-wrapper.is-date-picker {
    min-height: 40px;
  }

  .wb-filter__opt-hint {
    margin-left: 8px;
    font-size: 12px;
    color: var(--el-text-color-placeholder);
  }
</style>
