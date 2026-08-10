<!--
  任务池表格 - 调度工作台的核心列表

  Props:
    - tabKey: 状态池 key（与 workbench-pool-registry 中配置一致，决定列、排序、status、
      子集查询、预警规则、工具栏形态）
    - searchWhere: 父级统一筛选条件（切换阶段卡时保留公共字段）
    - reloadToken: caller 通过修改这个值触发列表重新加载

  Emits:
    - action: 行内动作触发 (row, action)
    - batchAction: 批量动作触发 (rows, action)
    - openDetail: 点击任务单号查看详情 (row)
    - syncStats: 表格数据加载完成后请求父级刷新 KPI（与列表同源、避免只刷表不刷统计）

  设计：
    - 本组件是「渲染壳」：只提供单元格 slot 库与操作列，不含任何按 poolKey 的分支判断，
      所有阶段差异都从注册表读取。
-->
<template>
  <div class="task-pool">
    <ele-card :body-style="{ paddingTop: '8px' }">
      <el-alert
        v-if="listSubset !== 'all'"
        :type="subsetBanner.type"
        :closable="false"
        class="task-pool__alert-banner"
        show-icon
        :title="subsetBanner.title"
      />
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        v-model:selections="selections"
        :default-sort="tableDefaultSort"
        :cache-key="`OperationTaskPool-v2-${pool.key}-${listSubset}`"
        @done="onTableDone"
        @sort-change="onSortChange"
      >
        <template #toolbar>
          <el-button
            v-if="showBatchToolbar"
            type="primary"
            plain
            class="ele-btn-icon"
            :icon="Operation"
            :disabled="selections.length === 0"
            v-permission="primaryAction!.permission"
            @click="onBatch"
          >
            批量{{ primaryAction!.label }} ({{ selections.length }})
          </el-button>
          <el-button
            v-if="pool.toolbar?.refresh"
            :icon="Refresh"
            plain
            class="ele-btn-icon"
            @click="doReload"
          >
            刷新
          </el-button>
        </template>

        <template #waybillCount="{ row }">
          {{ row.waybillCount ?? 0 }}
        </template>

        <template #createdAt="{ row }">
          {{ formatDateTime(row.createdAt) || '--' }}
        </template>

        <template #totalQuantity="{ row }">
          <el-tag
            v-if="pool.quantityOpenCargoDetail && (row.totalQuantity ?? 0) > 0"
            type="primary"
            effect="plain"
            size="small"
            class="tb-qty-tag"
            @click.stop="openTaskCargoDetail(row)"
          >
            {{ row.totalQuantity ?? 0 }}
          </el-tag>
          <span v-else>{{ row.totalQuantity ?? 0 }}</span>
        </template>

        <template #carrierType="{ row }">
          <el-tag
            :type="(CARRIER_TYPE_MAP[row.carrierType]?.type as any) || 'info'"
            size="small"
          >
            {{ CARRIER_TYPE_MAP[row.carrierType]?.label || '--' }}
          </el-tag>
        </template>

        <template #route="{ row }">
          <div class="route-cell cell-ellipsis">
            <span class="cell-ellipsis">{{ row.origin || '--' }}</span>
            <el-icon class="route-cell__arrow"><Right /></el-icon>
            <span class="cell-ellipsis">{{ row.destination || '--' }}</span>
            <el-tag
              v-if="(row.segmentCount || 0) > 1"
              size="small"
              type="info"
              effect="plain"
              class="route-cell__seg"
            >
              {{ row.segmentCount }} 段
            </el-tag>
          </div>
        </template>

        <template #carrierResource="{ row }">
          <div
            v-if="row.carrierType === CARRIER_TYPE.CARRIER"
            class="cell-ellipsis"
          >
            {{ row.carrierName || '--' }}
          </div>
          <div v-else class="cell-ellipsis">
            {{ row.mainDriverName || '--' }}
            <span v-if="row.plateNumber" class="ele-text-secondary">
              / {{ row.plateNumber }}
            </span>
          </div>
        </template>

        <template #carrierName="{ row }">
          <div class="cell-ellipsis">
            <template v-if="row.carrierType === CARRIER_TYPE.CARRIER">
              {{ row.carrierShortName || row.carrierName || '--' }}
            </template>
            <template v-else-if="row.carrierType === CARRIER_TYPE.SELF">
              <span class="ele-text-secondary">自有 ·</span>
              {{ row.mainDriverName || '待派车' }}
            </template>
            <template v-else-if="row.carrierType === CARRIER_TYPE.SOCIAL">
              <span class="ele-text-secondary">社会 ·</span>
              {{ row.mainDriverName || '--' }}
            </template>
            <template v-else>--</template>
          </div>
        </template>

        <template #plateNumber="{ row }">
          <span>
            {{ row.plateNumber || '--' }}
            <span
              v-if="row.trailerPlateNumber"
              class="ele-text-secondary"
              style="margin-left: 4px"
            >
              / {{ row.trailerPlateNumber }}
            </span>
          </span>
        </template>

        <template #status="{ row }">
          <div class="status-cell">
            <el-tag
              :type="(TASK_STATUS_MAP[row.status]?.type as any) || 'info'"
              size="small"
            >
              {{ TASK_STATUS_MAP[row.status]?.label || '--' }}
            </el-tag>
            <span
              v-if="loadProgressText(row)"
              class="ele-text-secondary status-cell__progress"
            >
              {{ loadProgressText(row) }}
            </span>
            <el-tag
              v-if="isAlertRow(row)"
              type="warning"
              size="small"
              effect="plain"
              class="status-cell__overdue"
            >
              预警
            </el-tag>
          </div>
        </template>

        <template #plannedLoadTime="{ row }">
          <span :class="{ 'is-overdue': isAlertColumn('plannedLoadTime', row) }">
            {{ formatDateTime(row.plannedLoadTime) || '--' }}
          </span>
        </template>

        <template #plannedArriveTime="{ row }">
          <span
            :class="{ 'is-overdue': isAlertColumn('plannedArriveTime', row) }"
          >
            {{ formatDateTime(row.plannedArriveTime) || '--' }}
          </span>
        </template>

        <template #actualLoadTime="{ row }">
          {{ formatDateTime(row.actualLoadTime) || '--' }}
        </template>

        <template #stageDuration="{ row }">
          <el-tooltip
            v-if="stageDuration(row).text !== '--'"
            :content="`进入「${pool.label}」：${formatDateTime(row.stageEnteredAt) || '未知'}`"
            placement="top"
            :show-after="350"
          >
            <span :class="{ 'is-overdue': stageDuration(row).overLimit }">
              {{ stageDuration(row).text }}
            </span>
          </el-tooltip>
          <span v-else>--</span>
        </template>

        <!-- 带说明的表头：短词 + 问号提示，避免在 label 里写括号被截断 -->
        <template #tipHeader="{ column }">
          <span class="tip-header">
            <span class="tip-header__text">{{ column.label }}</span>
            <el-tooltip
              :content="columnTip(column)"
              placement="top"
              :show-after="200"
            >
              <el-icon class="tip-header__icon"><QuestionFilled /></el-icon>
            </el-tooltip>
          </span>
        </template>

        <template #action="{ row }">
          <div class="action-cell">
            <btn-items
              divider
              type="link"
              :wrap="false"
              :items="actionItems(row)"
            />
          </div>
        </template>
      </ele-pro-table>
    </ele-card>

    <waybill-cargoes-detail
      v-model:visible="cargoDetailVisible"
      :waybill="cargoDetailWaybill"
    />
  </div>
</template>

<script lang="ts" setup>
  import { computed, nextTick, ref, watch } from 'vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    DoneParams
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import type { ButtonItem } from 'ele-admin-plus/es/ele-buttons/types';
  import {
    Operation,
    QuestionFilled,
    Refresh,
    Right
  } from '@element-plus/icons-vue';
  import { pageTasks, listTaskWaybillItems } from '@/api/operation/task';
  import type { Task, TaskParam } from '@/api/operation/task/model';
  import type { Waybill } from '@/api/waybill/model';
  import { formatDateTime } from '@/utils/date-util';
  import { EleMessage } from 'ele-admin-plus';
  import {
    CARRIER_TYPE,
    CARRIER_TYPE_MAP,
    TASK_STATUS,
    TASK_STATUS_MAP
  } from '../../task/status-config';
  import {
    TASK_ACTION_CONFIGS,
    buildTaskListActionItems
  } from '../../task/task-actions';
  import type { TaskActionConfig } from '../../task/task-actions';
  import { usePermission } from '@/utils/use-permission';
  import WaybillCargoesDetail from '../../waybill/components/waybill-cargoes-detail.vue';
  import { buildWaybillShapeForTaskCargoDetail } from '../task-cargo-detail-adapter';
  import {
    WORKBENCH_POOLS,
    buildColumnTipMap,
    buildWorkbenchTableColumns,
    getWorkbenchPool,
    isSortableProp,
    resolveWorkbenchPoolKey
  } from '../workbench-pool-registry';
  import type {
    WorkbenchColumnId,
    WorkbenchListSubset
  } from '../workbench-pool-registry';

  const props = defineProps<{
    /** 状态池 key（列、排序、筛选用 status 均来自注册表） */
    tabKey: string;
    /** 父级统一筛选条件（切换阶段卡时不丢失） */
    searchWhere?: Partial<TaskParam>;
    /** 通过修改此值触发外部强制刷新 */
    reloadToken?: number;
    /** KPI 子集：全部 / 正常(常) / 预警(警) */
    listSubset?: WorkbenchListSubset;
  }>();

  const emit = defineEmits<{
    (e: 'action', row: Task, action: TaskActionConfig): void;
    (e: 'batchAction', rows: Task[], action: TaskActionConfig): void;
    (e: 'openDetail', row: Task): void;
    (e: 'syncStats'): void;
    (e: 'autoSwitchPool', poolKey: string): void;
  }>();

  const { hasPermission } = usePermission();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Task[]>([]);

  const cargoDetailVisible = ref(false);
  const cargoDetailWaybill = ref<Waybill | null>(null);

  const pool = computed(
    () => getWorkbenchPool(props.tabKey) ?? WORKBENCH_POOLS[0]!
  );

  const listSubset = computed(() => props.listSubset ?? 'all');

  /** 本池是否支持服务端「常 / 警」子集筛选 */
  const supportsSubset = computed(() => typeof pool.value.subsetQuery === 'function');

  const subsetBanner = computed(() => {
    if (listSubset.value === 'all') {
      return { type: 'info' as const, title: '' };
    }
    if (!supportsSubset.value) {
      return {
        type: 'info' as const,
        title: `「${pool.value.label}」阶段的独立预警规则还在建设中，当前列表与「全部」一致，数量可参考上方卡片。`
      };
    }
    return listSubset.value === 'alert'
      ? {
          type: 'warning' as const,
          title: `当前列表：仅展示「${pool.value.label}」阶段的预警任务`
        }
      : {
          type: 'success' as const,
          title: `当前列表：仅展示「${pool.value.label}」阶段未触发预警的任务`
        };
  });

  const columns = computed(() => buildWorkbenchTableColumns(pool.value));

  const tableDefaultSort = computed(() => pool.value.defaultSort);

  /** 池级"主按钮"：用于工具栏批量按钮的文案与权限点；每行的主按钮按 row.status 再算一次 */
  const primaryAction = computed(() =>
    pool.value.primaryActionKey
      ? TASK_ACTION_CONFIGS[pool.value.primaryActionKey]
      : null
  );

  const showBatchToolbar = computed(() =>
    Boolean(primaryAction.value && pool.value.toolbar?.batchPrimary)
  );

  /**
   * 操作列：与任务单台账共用同一套候选与槽位算法（详见开发手册
   * 「17.列表操作列按钮规范」）——按 row.status 取动作，可见 ≤2 平铺，
   * ≥3 收敛成「首项 + 悬停更多」。
   */
  const actionItems = (row: Task): ButtonItem[] =>
    buildTaskListActionItems(row, {
      hasPermission,
      onDetail: () => emit('openDetail', row),
      onAction: (act) => emit('action', row, act)
    });

  /** 表头问号提示：按列的 prop / columnKey 反查本池配置 */
  const columnTips = computed(() => buildColumnTipMap(pool.value));

  const columnTip = (column: { property?: string; columnKey?: string }) =>
    columnTips.value[column?.property ?? ''] ??
    columnTips.value[column?.columnKey ?? ''] ??
    '';

  const isAlertRow = (row: Task): boolean =>
    pool.value.alertRule?.(row) ?? false;

  const isAlertColumn = (col: WorkbenchColumnId, row: Task): boolean =>
    pool.value.alertColumn === col && isAlertRow(row);

  /** 本阶段停留时长；超过池配置的阈值则标红 */
  const stageDuration = (row: Task): { text: string; overLimit: boolean } => {
    if (!row.stageEnteredAt) return { text: '--', overLimit: false };
    const enteredAt = Date.parse(row.stageEnteredAt);
    if (Number.isNaN(enteredAt)) return { text: '--', overLimit: false };
    const minutes = Math.max(0, Math.floor((Date.now() - enteredAt) / 60000));
    const limit = pool.value.stageAlertHours;
    const overLimit = limit != null && minutes >= limit * 60;
    if (minutes < 60) return { text: `${minutes} 分钟`, overLimit };
    const hours = Math.floor(minutes / 60);
    if (hours < 24) {
      const rest = minutes % 60;
      return { text: rest ? `${hours} 小时 ${rest} 分` : `${hours} 小时`, overLimit };
    }
    const days = Math.floor(hours / 24);
    const restHours = hours % 24;
    return {
      text: restHours ? `${days} 天 ${restHours} 小时` : `${days} 天`,
      overLimit
    };
  };

  /** 表头排序：透传给服务端（字段在白名单内才生效） */
  const sortState = ref<{ sortField?: string; sortOrder?: 'asc' | 'desc' }>({});

  const onSortChange = (payload: {
    prop?: string;
    order?: 'ascending' | 'descending' | null;
  }) => {
    if (!payload?.prop || !payload.order || !isSortableProp(payload.prop)) {
      sortState.value = {};
    } else {
      sortState.value = {
        sortField: payload.prop,
        sortOrder: payload.order === 'ascending' ? 'asc' : 'desc'
      };
    }
    doReload();
  };

  const activeSort = computed(() => {
    if (sortState.value.sortField) return sortState.value;
    const { prop, order } = pool.value.defaultSort;
    if (!isSortableProp(prop)) return {};
    return {
      sortField: prop,
      sortOrder: order === 'ascending' ? ('asc' as const) : ('desc' as const)
    };
  });

  const filterParamsWithoutKeyword = (): Omit<
    Partial<TaskParam>,
    'keyword'
  > => {
    const { keyword: _k, ...rest } = props.searchWhere ?? {};
    return rest;
  };

  const fetchPage = (
    params: Partial<TaskParam>
  ): Promise<{ list: Task[]; count: number }> =>
    pageTasks(params as TaskParam).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));

  const maybeAutoSwitchPool = (list: Task[], keyword?: string) => {
    if (!keyword?.trim() || list.length === 0) return;
    const targetPool = resolveWorkbenchPoolKey(list[0]!.status);
    if (targetPool && targetPool !== pool.value.key) {
      emit('autoSwitchPool', targetPool);
    }
  };

  /** 状态 Tag 后缀进度文本：已装/已卸 X/Y */
  const loadProgressText = (row: Task): string => {
    const total = row.totalQuantity ?? 0;
    if (!total) return '';
    if (row.status === TASK_STATUS.DISPATCHED) {
      const loaded = row.loadedQuantity ?? 0;
      if (loaded > 0) return `已装 ${loaded}/${total}`;
    } else if (row.status === TASK_STATUS.ON_WAY) {
      const unloaded = row.unloadedQuantity ?? 0;
      if (unloaded > 0) return `已卸 ${unloaded}/${total}`;
    }
    return '';
  };

  const datasource: DatasourceFunction = ({ pages }) => {
    const search = props.searchWhere ?? {};
    const keyword = search.keyword?.trim();
    // 任务单号/计划号搜索：仅按 keyword 查，不受阶段/日期等限制
    if (keyword) {
      return fetchPage({ ...pages, keyword, ...activeSort.value }).then((res) => {
        maybeAutoSwitchPool(res.list, keyword);
        return res;
      });
    }

    const subset =
      listSubset.value !== 'all' && pool.value.subsetQuery
        ? pool.value.subsetQuery(listSubset.value)
        : {};

    return fetchPage({
      ...pages,
      status: pool.value.status,
      ...subset,
      ...filterParamsWithoutKeyword(),
      ...activeSort.value
    });
  };

  const doReload = () => {
    nextTick(() => tableRef.value?.reload?.({ page: 1 }));
  };

  /** 工具栏刷新 / 工具栏「刷新」等任意数据重载完成后，同步刷新工作台统计卡片 */
  const onTableDone = (_result: DoneParams<Task>, parent?: Task) => {
    if (parent != null) return;
    emit('syncStats');
  };

  watch(
    () => props.listSubset,
    () => {
      selections.value = [];
      doReload();
    }
  );

  watch(
    () => props.tabKey,
    () => {
      selections.value = [];
      sortState.value = {};
      doReload();
    }
  );

  watch(
    () => props.searchWhere,
    () => {
      selections.value = [];
      doReload();
    },
    { deep: true }
  );

  watch(
    () => props.reloadToken,
    () => doReload()
  );

  const onBatch = () => {
    if (!primaryAction.value || selections.value.length === 0) return;
    emit('batchAction', selections.value, primaryAction.value);
  };

  const openTaskCargoDetail = async (row: Task) => {
    if (!row.id || (row.totalQuantity ?? 0) <= 0) return;
    try {
      const items = await listTaskWaybillItems(row.id);
      cargoDetailWaybill.value = buildWaybillShapeForTaskCargoDetail(
        row,
        items
      );
      cargoDetailVisible.value = true;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '加载挂接明细失败';
      EleMessage.error({ message: msg, plain: true });
    }
  };
</script>

<style lang="scss" scoped>
  .task-pool {
    &__alert-banner {
      margin-bottom: 10px;
    }
  }

  .tb-qty-tag {
    cursor: pointer;
    user-select: none;
  }

  .tb-qty-tag:hover {
    opacity: 0.88;
  }

  .cell-ellipsis {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .route-cell {
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    min-width: 0;
    gap: 0;

    > .cell-ellipsis {
      flex: 1 1 0;
    }

    &__arrow {
      flex-shrink: 0;
      margin: 0 6px;
    }
    &__seg {
      flex-shrink: 0;
      margin-left: 6px;
    }
  }

  .action-cell {
    display: inline-flex;
    align-items: center;
    flex-wrap: nowrap;
    white-space: nowrap;
  }

  .tip-header {
    display: inline-flex;
    align-items: center;
    gap: 3px;

    &__text {
      overflow: hidden;
      text-overflow: ellipsis;
    }

    &__icon {
      flex-shrink: 0;
      font-size: 13px;
      color: var(--el-text-color-placeholder);
      cursor: help;

      &:hover {
        color: var(--el-color-primary);
      }
    }
  }

  .status-cell {
    display: inline-flex;
    align-items: center;
    flex-wrap: nowrap;
    white-space: nowrap;

    &__progress {
      margin-left: 4px;
      font-size: 12px;
    }

    &__overdue {
      margin-left: 4px;
    }
  }

  .is-overdue {
    color: var(--el-color-danger);
    font-weight: 500;
  }

  /* 列表单元格单行展示，悬停由表格 tooltip 展示全文 */
  .task-pool :deep(.el-table .cell) {
    white-space: nowrap;
    overflow: hidden;
  }
</style>
