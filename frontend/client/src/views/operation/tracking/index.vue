<!--
  在途监控

  口径：展示「在途(status=3)」任务（已出发尚未到达）。原实现调用已废弃的
  ``/business/order/tracking`` 接口（旧 Order 模型，后端已无该路由 → 401）；
  现重指向运营任务接口 ``pageTasks({ status: 3 })``，并复用调度工作台的
  「确认到达」弹窗（按卸车记录聚合驱动 task 3→4），不再调用废弃的 updateOrderStatus。
-->
<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="OperationTrackingTable-v2"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="任务单号 / 计划号"
                clearable
                @change="reload"
              />
            </el-form-item>
            <el-form-item>
              <el-button :icon="Refresh" plain @click="reload">刷新</el-button>
            </el-form-item>
          </el-form>
        </template>

        <template #carrierResource="{ row }">
          <div v-if="row.carrierType === 2">{{ row.carrierName || '--' }}</div>
          <div v-else>
            {{ row.mainDriverName || '--' }}
            <span v-if="row.plateNumber" class="ele-text-secondary">
              / {{ row.plateNumber }}
            </span>
          </div>
        </template>

        <template #route="{ row }">
          <route-cell
            :nodes="row.routeNodes"
            :origin="row.origin"
            :destination="row.destination"
            :segment-count="row.segmentCount"
          />
        </template>

        <template #plannedArriveTime="{ row }">
          <span :class="{ 'is-overdue': isArriveOverdue(row) }">
            {{ formatDateTime(row.plannedArriveTime) || '--' }}
          </span>
        </template>

        <template #actualLoadTime="{ row }">
          {{ formatDateTime(row.actualLoadTime) || '--' }}
        </template>

        <template #status="{ row }">
          <el-tag
            :type="(TASK_STATUS_MAP[row.status]?.type as any) || 'warning'"
            size="small"
          >
            {{ TASK_STATUS_MAP[row.status]?.label || '在途' }}
          </el-tag>
          <el-tag
            v-if="isArriveOverdue(row)"
            type="danger"
            size="small"
            effect="plain"
            style="margin-left: 4px"
          >
            预警
          </el-tag>
        </template>

        <template #action="{ row }">
          <el-link
            type="success"
            :underline="false"
            v-permission="'operation:task:confirm-arrive'"
            @click="handleArrive(row)"
          >
            确认到达
          </el-link>
        </template>
      </ele-pro-table>
    </ele-card>

    <action-confirm-arrive
      v-model:visible="arriveVisible"
      :tasks="arriveTargets"
      @done="onArriveDone"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { Refresh } from '@element-plus/icons-vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { pageTasks } from '@/api/operation/task';
  import type { Task, TaskParam } from '@/api/operation/task/model';
  import { formatDateTime } from '@/utils/date-util';
  import { TASK_STATUS_MAP } from '../task/status-config';
  import ActionConfirmArrive from '../task-workbench/components/action-confirm-arrive.vue';
  import RouteCell from '../task-workbench/components/route-cell.vue';

  defineOptions({ name: 'OperationTracking' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const where = reactive<{ keyword: string }>({ keyword: '' });

  const arriveVisible = ref(false);
  const arriveTargets = ref<Task[]>([]);

  const columns = ref<Columns>([
    { type: 'index', columnKey: 'index', width: 50, align: 'center' },
    { prop: 'taskNo', label: '任务单号', width: 168 },
    {
      prop: 'carrierType',
      columnKey: 'carrierResource',
      label: '承运资源',
      width: 180,
      slot: 'carrierResource'
    },
    {
      prop: 'origin',
      columnKey: 'route',
      label: '运输线路',
      minWidth: 320,
      showOverflowTooltip: false,
      slot: 'route'
    },
    { prop: 'totalQuantity', label: '台数', width: 92, align: 'center' },
    {
      prop: 'actualLoadTime',
      label: '实际装车',
      width: 168,
      align: 'center',
      slot: 'actualLoadTime'
    },
    {
      prop: 'plannedArriveTime',
      label: '计划到货',
      width: 168,
      align: 'center',
      slot: 'plannedArriveTime'
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
      width: 100,
      align: 'center',
      fixed: 'right',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit }) => {
    const params: Partial<TaskParam> = {
      page,
      limit,
      status: 3,
      ...(where.keyword.trim() ? { keyword: where.keyword.trim() } : {})
    };
    const res = await pageTasks(params as TaskParam);
    return { list: res?.list ?? [], count: res?.count ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.({ page: 1 });
  };

  const isArriveOverdue = (row: Task): boolean => {
    if (!row.plannedArriveTime) return false;
    return Date.parse(row.plannedArriveTime) < Date.now();
  };

  const handleArrive = (row: Task) => {
    arriveTargets.value = [row];
    arriveVisible.value = true;
  };

  const onArriveDone = () => {
    reload();
  };
</script>

<style lang="scss" scoped>
  .is-overdue {
    color: var(--el-color-danger);
    font-weight: 500;
  }
</style>
