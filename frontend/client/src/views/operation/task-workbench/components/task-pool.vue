<!--
  任务池表格 - 调度工作台的核心列表

  Props:
    - tabKey: 状态池 key（与 workbench-pool-registry 中配置一致，决定列、排序、status 筛选）
    - reloadToken: caller 通过修改这个值触发列表重新加载

  Emits:
    - action: 行内动作触发 (row, action)
    - batchAction: 批量动作触发 (rows, action)
    - openDetail: 点击任务单号查看详情 (row)
    - syncStats: 表格数据加载完成后请求父级刷新 KPI（与列表同源、避免只刷表不刷统计）

  设计：
    - 行内只展示当前状态对应的"主按钮"
    - 部分状态池支持「批量执行该状态主动作」与多选列（由注册表配置）
-->
<template>
  <div class="task-pool">
    <el-alert
      v-if="listSubset !== 'all'"
      :type="subsetBanner.type"
      :closable="false"
      class="task-pool__alert-banner"
      show-icon
      :title="subsetBanner.title"
    />
    <div
      class="task-pool__toolbar"
      :class="{
        'task-pool__toolbar--dispatch':
          pool.toolbarPreset === 'pending-dispatch'
      }"
    >
      <template v-if="pool.toolbarPreset === 'pending-dispatch'">
        <el-input
          v-model="keyword"
          class="task-pool__toolbar-keyword"
          placeholder="任务单号 / 运单号 / 任务名称"
          clearable
          @keyup.enter="doReload"
          @clear="doReload"
        />
        <el-input
          v-model="routeOriginKw"
          placeholder="出发地"
          clearable
          class="task-pool__toolbar-field"
          @keyup.enter="doReload"
        />
        <el-input
          v-model="routeDestKw"
          placeholder="目的地"
          clearable
          class="task-pool__toolbar-field"
          @keyup.enter="doReload"
        />
        <el-date-picker
          v-model="createdRange"
          type="daterange"
          range-separator="至"
          start-placeholder="制单起"
          end-placeholder="制单止"
          value-format="YYYY-MM-DD"
          unlink-panels
          class="task-pool__toolbar-dates"
        />
        <el-button type="primary" :icon="Search" @click="doReload">
          查询
        </el-button>
        <el-button :icon="RefreshLeft" @click="resetDispatchFilters">
          重置
        </el-button>
      </template>
      <template v-else>
        <el-input
          v-model="keyword"
          placeholder="任务单号 / 司机 / 车牌 / 承运商"
          clearable
          style="width: 260px"
          @change="doReload"
        />
      </template>
      <el-button
        v-if="primaryAction && allowBatchPrimary && selections.length > 0"
        :type="primaryAction.buttonType"
        :icon="Operation"
        v-permission="primaryAction.permission"
        @click="onBatch"
      >
        批量{{ primaryAction.label }} ({{ selections.length }})
      </el-button>
      <el-button
        v-if="pool.toolbarPreset !== 'pending-dispatch'"
        :icon="Refresh"
        plain
        @click="doReload"
      >
        刷新
      </el-button>
    </div>

    <ele-pro-table
      ref="tableRef"
      row-key="id"
      :columns="columns"
      :datasource="datasource"
      :pagination="{ pageSize: 20 }"
      :show-overflow-tooltip="true"
      v-model:selections="selections"
      :default-sort="tableDefaultSort"
      :cache-key="`OperationTaskPool-${tabKey}-${listSubset}`"
      @done="onTableDone"
    >
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
        <div v-if="row.carrierType === 2" class="cell-ellipsis">
          {{ row.carrierName || '--' }}
        </div>
        <div v-else class="cell-ellipsis">
          {{ row.mainDriverName || '--' }}
          <span v-if="row.plateNumber" class="ele-text-secondary">
            / {{ row.plateNumber }}
          </span>
        </div>
      </template>

      <template #status="{ row }">
        <div class="status-cell">
          <el-tag
            :type="(TASK_STATUS_MAP[row.status]?.type as any) || 'info'"
            size="small"
          >
            {{ TASK_STATUS_MAP[row.status]?.label || '--' }}
          </el-tag>
          <el-tag
            v-if="isOverdue(row)"
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
        <span :class="{ 'is-overdue': isDispatchOverdue(row) }">
          {{ formatDateTime(row.plannedLoadTime) || '--' }}
        </span>
      </template>

      <template #plannedArriveTime="{ row }">
        <span :class="{ 'is-overdue': isArriveOverdue(row) }">
          {{ formatDateTime(row.plannedArriveTime) || '--' }}
        </span>
      </template>

      <template #actualLoadTime="{ row }">
        {{ formatDateTime(row.actualLoadTime) || '--' }}
      </template>

      <template #action="{ row }">
        <div class="action-cell">
          <el-link
            type="primary"
            :underline="false"
            @click="emit('openDetail', row)"
          >
            详情
          </el-link>
          <template v-if="primaryAction">
            <el-divider direction="vertical" />
            <el-link
              :type="primaryAction.buttonType as any"
              :underline="false"
              v-permission="primaryAction.permission"
              @click="emit('action', row, primaryAction)"
            >
              {{ primaryAction.label }}
            </el-link>
          </template>
          <template v-if="canPlanRoute(row)">
            <el-divider direction="vertical" />
            <el-link
              type="primary"
              :underline="false"
              v-permission="planRouteAction.permission"
              @click="emit('action', row, planRouteAction)"
            >
              规划路线<span
                v-if="(row.segmentCount ?? 0) === 0"
                style="margin-left: 2px"
                >·未规划</span
              >
            </el-link>
          </template>
        </div>
      </template>
    </ele-pro-table>

    <waybill-cargoes-detail
      v-model:visible="cargoDetailVisible"
      :waybill="cargoDetailWaybill"
    />
  </div>
</template>

<script lang="ts" setup>
  import { computed, nextTick, onMounted, ref, watch } from 'vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    DoneParams
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    Operation,
    Refresh,
    RefreshLeft,
    Right,
    Search
  } from '@element-plus/icons-vue';
  import { pageTasks, listTaskWaybillItems } from '@/api/operation/task';
  import type { Task, TaskParam } from '@/api/operation/task/model';
  import type { Waybill } from '@/api/waybill/model';
  import { formatDateTime } from '@/utils/date-util';
  import { EleMessage } from 'ele-admin-plus';
  import { CARRIER_TYPE_MAP, TASK_STATUS_MAP } from '../../task/status-config';
  import {
    TASK_ACTION_CONFIGS,
    shouldShowPlanRoute
  } from '../../task/task-actions';
  import type { TaskActionConfig } from '../../task/task-actions';
  import WaybillCargoesDetail from '../../waybill/components/waybill-cargoes-detail.vue';
  import { buildWaybillShapeForTaskCargoDetail } from '../task-cargo-detail-adapter';
  import {
    WORKBENCH_POOLS,
    buildWorkbenchTableColumns,
    getWorkbenchPool
  } from '../workbench-pool-registry';

  type WorkbenchListSubset = 'all' | 'normal' | 'alert';

  const props = defineProps<{
    /** 状态池 key（列、排序、筛选用 status 均来自注册表） */
    tabKey: string;
    /** 通过修改此值触发外部强制刷新 */
    reloadToken?: number;
    /**
     * KPI 子集：全部 / 正常(常) / 预警(警)。
     * 待分配、待派车、在途中已接服务端筛选；其余阶段子集筛选能力建设中。
     */
    listSubset?: WorkbenchListSubset;
  }>();

  const emit = defineEmits<{
    (e: 'action', row: Task, action: TaskActionConfig): void;
    (e: 'batchAction', rows: Task[], action: TaskActionConfig): void;
    (e: 'openDetail', row: Task): void;
    (e: 'syncStats'): void;
  }>();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Task[]>([]);
  const keyword = ref('');
  const routeOriginKw = ref('');
  const routeDestKw = ref('');
  const createdRange = ref<[string, string] | null>(null);

  const cargoDetailVisible = ref(false);
  const cargoDetailWaybill = ref<Waybill | null>(null);

  const pool = computed(
    () => getWorkbenchPool(props.tabKey) ?? WORKBENCH_POOLS[0]!
  );

  const SERVER_SUBSET_POOL_KEYS = [
    'pending-assign',
    'pending-dispatch',
    'on-way'
  ] as const;
  type ServerSubsetPoolKey = (typeof SERVER_SUBSET_POOL_KEYS)[number];

  const supportsServerSubset = computed(() =>
    SERVER_SUBSET_POOL_KEYS.includes(pool.value.key as ServerSubsetPoolKey)
  );

  const listSubset = computed(() => props.listSubset ?? 'all');

  const wantServerAlert = computed(
    () => listSubset.value === 'alert' && supportsServerSubset.value
  );

  const wantServerNormal = computed(
    () => listSubset.value === 'normal' && supportsServerSubset.value
  );

  const subsetBanner = computed(() => {
    if (listSubset.value === 'all') {
      return { type: 'info' as const, title: '' };
    }
    if (listSubset.value === 'alert') {
      if (supportsServerSubset.value) {
        return {
          type: 'warning' as const,
          title: '当前列表：仅展示本阶段「预警」任务（已接入的命中规则）'
        };
      }
      return {
        type: 'info' as const,
        title:
          '本阶段「预警」独立筛选能力建设中；当前列表与「全部」一致，预警数见上方卡片。'
      };
    }
    if (supportsServerSubset.value) {
      return {
        type: 'success' as const,
        title:
          '当前列表：仅展示本阶段「正常」任务（未触发已接入的计划类预警规则）'
      };
    }
    return {
      type: 'info' as const,
      title:
        '本阶段「正常」独立筛选能力建设中；当前列表与「全部」一致，可参考上方「常」数量。'
    };
  });

  const columns = computed(() => buildWorkbenchTableColumns(pool.value));

  const tableDefaultSort = computed(() => pool.value.defaultSort);

  const allowBatchPrimary = computed(
    () => pool.value.allowBatchPrimary !== false
  );

  const primaryAction = computed(() =>
    pool.value.primaryActionKey
      ? TASK_ACTION_CONFIGS[pool.value.primaryActionKey]
      : null
  );

  const planRouteAction = TASK_ACTION_CONFIGS['plan-route'];

  const listExtraParams = (): Partial<TaskParam> => {
    if (pool.value.toolbarPreset !== 'pending-dispatch') return {};
    const r = createdRange.value;
    return {
      originKeyword: routeOriginKw.value?.trim() || undefined,
      destinationKeyword: routeDestKw.value?.trim() || undefined,
      createdAtStart: r?.[0] || undefined,
      createdAtEnd: r?.[1] || undefined
    };
  };

  const resetDispatchFilters = () => {
    keyword.value = '';
    routeOriginKw.value = '';
    routeDestKw.value = '';
    createdRange.value = null;
    doReload();
  };

  /** 行内是否展示"规划路线"次按钮（避免与主按钮重复或对终态任务展示） */
  const canPlanRoute = (row: Task): boolean => {
    if (pool.value.primaryActionKey === 'plan-route') return false;
    return shouldShowPlanRoute(row);
  };

  const datasource: DatasourceFunction = ({ pages }) => {
    const st = pool.value.status;
    const statusArr = Array.isArray(st) ? st : [st];
    const extra = listExtraParams();
    const kw = keyword.value || undefined;

    if (statusArr.length === 1) {
      const s0 = statusArr[0]!;
      const overdue = wantServerAlert.value && (s0 === -1 || s0 === 0);
      const normalF = wantServerNormal.value && (s0 === -1 || s0 === 0);
      return pageTasks({
        ...pages,
        keyword: kw,
        status: s0,
        ...(overdue ? { onlyOverdue: true } : {}),
        ...(normalF ? { onlyNormal: true } : {}),
        ...extra
      }).then((res) => ({
        list: res?.list ?? [],
        count: res?.count ?? 0
      }));
    }

    if (wantServerAlert.value && pool.value.key === 'on-way') {
      return pageTasks({
        ...pages,
        keyword: kw,
        inTransitOverdue: true,
        ...extra
      }).then((res) => ({
        list: res?.list ?? [],
        count: res?.count ?? 0
      }));
    }

    if (wantServerNormal.value && pool.value.key === 'on-way') {
      return pageTasks({
        ...pages,
        keyword: kw,
        inTransitOnlyNormal: true,
        ...extra
      }).then((res) => ({
        list: res?.list ?? [],
        count: res?.count ?? 0
      }));
    }

    return Promise.all(
      statusArr.map((s) =>
        pageTasks({
          page: 1,
          limit: 100,
          keyword: kw,
          status: s,
          ...extra
        })
      )
    ).then((results) => {
      const merged: Task[] = [];
      let count = 0;
      results.forEach((res) => {
        merged.push(...(res?.list ?? []));
        count += res?.count ?? 0;
      });
      const { prop, order } = pool.value.defaultSort;
      const dir = order === 'ascending' ? 1 : -1;
      merged.sort((a, b) => {
        if (prop === 'taskNo') {
          const na = a.taskNo ?? '';
          const nb = b.taskNo ?? '';
          return na.localeCompare(nb, undefined, { numeric: true }) * dir;
        }
        const va = (a as Record<string, unknown>)[prop];
        const vb = (b as Record<string, unknown>)[prop];
        const ta = va ? Date.parse(String(va)) : 0;
        const tb = vb ? Date.parse(String(vb)) : 0;
        return (ta - tb) * dir;
      });
      const start = ((pages.page || 1) - 1) * (pages.limit || 20);
      return {
        list: merged.slice(start, start + (pages.limit || 20)),
        count
      };
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
    (next, prev) => {
      if (prev !== undefined && next !== prev) {
        keyword.value = '';
        routeOriginKw.value = '';
        routeDestKw.value = '';
        createdRange.value = null;
        selections.value = [];
      }
      doReload();
    }
  );

  watch(
    () => props.reloadToken,
    () => doReload()
  );

  onMounted(() => {
    nextTick(() => doReload());
  });

  const onBatch = () => {
    if (!primaryAction.value || selections.value.length === 0) return;
    emit('batchAction', selections.value, primaryAction.value);
  };

  /** 待派车 / 待分配：计划装车已过 */
  const isDispatchOverdue = (row: Task): boolean => {
    if (!row.plannedLoadTime) return false;
    const overdue = Date.parse(row.plannedLoadTime) < Date.now();
    if (row.status === -1 || row.status === 0) return overdue;
    return false;
  };

  /** 在途：计划到货已过 */
  const isArriveOverdue = (row: Task): boolean => {
    if ((row.status !== 2 && row.status !== 3) || !row.plannedArriveTime) {
      return false;
    }
    return Date.parse(row.plannedArriveTime) < Date.now();
  };

  const isOverdue = (row: Task): boolean =>
    isDispatchOverdue(row) || isArriveOverdue(row);

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

    &__toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin-bottom: 8px;

      &--dispatch {
        row-gap: 10px;
      }
    }

    &__toolbar-keyword {
      width: min(240px, 100%);
      min-width: 180px;
    }

    &__toolbar-field {
      width: 140px;
    }

    &__toolbar-dates {
      width: 260px;
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

  .status-cell {
    display: inline-flex;
    align-items: center;
    flex-wrap: nowrap;
    white-space: nowrap;

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
