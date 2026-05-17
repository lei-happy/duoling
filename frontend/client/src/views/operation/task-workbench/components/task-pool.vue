<!--
  任务池表格 - 调度工作台的核心列表

  Props:
    - status: 当前 Tab 对应的 status（可以是单值或数组）
    - primaryActionKey: 该 Tab 行内的主动作（如 'dispatch' / 'confirm-load' / ...）
    - reloadToken: caller 通过修改这个值触发列表重新加载

  Emits:
    - action: 行内动作触发 (row, action)
    - batchAction: 批量动作触发 (rows, action)
    - openDetail: 点击任务单号查看详情 (row)

  设计：
    - 行内只展示当前状态对应的"主按钮"
    - 顶部支持"批量执行该状态主动作"
-->
<template>
  <div class="task-pool">
    <div class="task-pool__toolbar">
      <el-input
        v-model="keyword"
        placeholder="任务单号 / 司机 / 车牌 / 承运商"
        clearable
        style="width: 260px"
        @change="doReload"
      />
      <el-button
        v-if="primaryAction && selections.length > 0"
        :type="primaryAction.buttonType"
        :icon="Operation"
        v-permission="primaryAction.permission"
        @click="onBatch"
      >
        批量{{ primaryAction.label }} ({{ selections.length }})
      </el-button>
      <el-button :icon="Refresh" plain @click="doReload">刷新</el-button>
    </div>

    <ele-pro-table
      ref="tableRef"
      row-key="id"
      :columns="columns"
      :datasource="datasource"
      :pagination="{ pageSize: 20 }"
      :show-overflow-tooltip="true"
      v-model:selections="selections"
      :default-sort="{ prop: 'plannedLoadTime', order: 'ascending' }"
      :cache-key="`OperationTaskPool-${tabKey}`"
    >
      <template #carrierType="{ row }">
        <el-tag
          :type="(CARRIER_TYPE_MAP[row.carrierType]?.type as any) || 'info'"
          size="small"
        >
          {{ CARRIER_TYPE_MAP[row.carrierType]?.label || '--' }}
        </el-tag>
      </template>

      <template #route="{ row }">
        <div class="route-cell">
          <span>{{ row.origin || '--' }}</span>
          <el-icon style="margin: 0 6px"><Right /></el-icon>
          <span>{{ row.destination || '--' }}</span>
          <el-tag
            v-if="(row.segmentCount || 0) > 1"
            size="small"
            type="info"
            effect="plain"
            style="margin-left: 6px"
          >
            {{ row.segmentCount }} 段
          </el-tag>
        </div>
      </template>

      <template #carrierResource="{ row }">
        <div v-if="row.carrierType === 2">
          {{ row.carrierName || '--' }}
        </div>
        <div v-else>
          {{ row.mainDriverName || '--' }}
          <span v-if="row.plateNumber" class="ele-text-secondary">
            / {{ row.plateNumber }}
          </span>
        </div>
      </template>

      <template #status="{ row }">
        <el-tag
          :type="(TASK_STATUS_MAP[row.status]?.type as any) || 'info'"
          size="small"
        >
          {{ TASK_STATUS_MAP[row.status]?.label || '--' }}
        </el-tag>
        <el-tag
          v-if="isOverdue(row)"
          type="danger"
          size="small"
          effect="plain"
          style="margin-left: 4px"
        >
          逾期
        </el-tag>
      </template>

      <template #plannedLoadTime="{ row }">
        <span :class="{ 'is-overdue': isOverdue(row) }">
          {{ formatDateTime(row.plannedLoadTime) || '--' }}
        </span>
      </template>

      <template #action="{ row }">
        <el-link type="primary" :underline="false" @click="emit('openDetail', row)">
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
      </template>
    </ele-pro-table>
  </div>
</template>

<script lang="ts" setup>
  import { computed, nextTick, ref, watch } from 'vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { Operation, Refresh, Right } from '@element-plus/icons-vue';
  import { pageTasks } from '@/api/operation/task';
  import type { Task } from '@/api/operation/task/model';
  import { formatDateTime } from '@/utils/date-util';
  import { CARRIER_TYPE_MAP, TASK_STATUS_MAP } from '../../task/status-config';
  import {
    TASK_ACTION_CONFIGS,
    shouldShowPlanRoute
  } from '../../task/task-actions';
  import type { TaskActionConfig, TaskActionKey } from '../../task/task-actions';

  const props = defineProps<{
    /** Tab 标识（用于缓存 key） */
    tabKey: string;
    /** 当前 Tab 的 status，单值或多值（多值用 OR） */
    status: number | number[];
    /** 当前 Tab 对应的主动作 key */
    primaryActionKey: TaskActionKey | null;
    /** 通过修改此值触发外部强制刷新 */
    reloadToken?: number;
  }>();

  const emit = defineEmits<{
    (e: 'action', row: Task, action: TaskActionConfig): void;
    (e: 'batchAction', rows: Task[], action: TaskActionConfig): void;
    (e: 'openDetail', row: Task): void;
  }>();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Task[]>([]);
  const keyword = ref('');

  const primaryAction = computed(() =>
    props.primaryActionKey ? TASK_ACTION_CONFIGS[props.primaryActionKey] : null
  );

  const planRouteAction = TASK_ACTION_CONFIGS['plan-route'];

  /** 行内是否展示"规划路线"次按钮（避免与主按钮重复或对终态任务展示） */
  const canPlanRoute = (row: Task): boolean => {
    if (props.primaryActionKey === 'plan-route') return false;
    return shouldShowPlanRoute(row);
  };

  const columns = computed<Columns>(() => [
    { type: 'selection', width: 48, align: 'center' },
    { prop: 'taskNo', label: '任务单号', minWidth: 160 },
    {
      prop: 'carrierType',
      label: '承运方式',
      width: 96,
      align: 'center',
      slot: 'carrierType'
    },
    {
      columnKey: 'route',
      label: '运输线路',
      minWidth: 240,
      slot: 'route'
    },
    {
      columnKey: 'carrierResource',
      label: '司机/车牌/承运商',
      minWidth: 180,
      slot: 'carrierResource'
    },
    {
      prop: 'totalQuantity',
      label: '台数',
      width: 70,
      align: 'center'
    },
    {
      prop: 'plannedLoadTime',
      label: '计划装车',
      width: 160,
      align: 'center',
      slot: 'plannedLoadTime'
    },
    {
      prop: 'status',
      label: '状态',
      width: 110,
      align: 'center',
      slot: 'status'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 240,
      align: 'center',
      fixed: 'right',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages }) => {
    const statusArr = Array.isArray(props.status) ? props.status : [props.status];
    // 后端 page 接口当前只支持单值 status；多值时分别拉取后合并
    if (statusArr.length === 1) {
      return pageTasks({
        ...pages,
        keyword: keyword.value || undefined,
        status: statusArr[0]
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
          keyword: keyword.value || undefined,
          status: s
        })
      )
    ).then((results) => {
      const merged: Task[] = [];
      let count = 0;
      results.forEach((res) => {
        merged.push(...(res?.list ?? []));
        count += res?.count ?? 0;
      });
      // 按计划装车时间升序
      merged.sort((a, b) => {
        const ta = a.plannedLoadTime ? Date.parse(a.plannedLoadTime) : 0;
        const tb = b.plannedLoadTime ? Date.parse(b.plannedLoadTime) : 0;
        return ta - tb;
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

  watch(() => props.reloadToken, () => doReload());
  watch(
    () => [props.status, props.primaryActionKey] as const,
    () => doReload()
  );

  const onBatch = () => {
    if (!primaryAction.value || selections.value.length === 0) return;
    emit('batchAction', selections.value, primaryAction.value);
  };

  const isOverdue = (row: Task): boolean => {
    const now = Date.now();
    if (row.status === 0 && row.plannedLoadTime) {
      return Date.parse(row.plannedLoadTime) < now;
    }
    if ((row.status === 2 || row.status === 3) && row.plannedArriveTime) {
      return Date.parse(row.plannedArriveTime) < now;
    }
    return false;
  };
</script>

<style lang="scss" scoped>
  .task-pool {
    &__toolbar {
      display: flex;
      gap: 8px;
      align-items: center;
      margin-bottom: 8px;
    }
  }
  .route-cell {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }
  .is-overdue {
    color: var(--el-color-danger);
    font-weight: 500;
  }
</style>
