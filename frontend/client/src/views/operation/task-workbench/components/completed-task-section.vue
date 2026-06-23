<!--
  已完成任务区域 - 调度工作台下方

  概念：
  - 活跃池（待分配~待签收）在上方 KPI/task-pool 处理；本区域承载「终态」任务的查看入口。
  - 3 个 Tab：已签收(5) / 已关闭(7) / 已取消(9)，计数来自工作台 KPI 统计。

  逆向（严格按《02.运单与任务单状态机联动设计.md》§4.5.1）：
  - 仅「已签收(5)」可逆——通过 item 级「撤销签收」(item 3→2) 反向聚合驱动 task 5→4；
    入口由 task-actions 的 revert-sign 动作（dialog=revert-sign）提供。
  - 「已关闭(7)/已取消(9)」为终态，本区域仅提供「详情」查看，不暴露任何逆向入口。
-->
<template>
  <ele-card
    class="completed-section"
    :body-style="{ paddingTop: '8px' }"
    header="已完成任务"
  >
    <ele-pro-table
      ref="tableRef"
      row-key="id"
      :columns="columns"
      :datasource="datasource"
      :pagination="{ pageSize: 10 }"
      :show-overflow-tooltip="true"
      :cache-key="`OperationCompletedTaskPool-${activeTab}`"
    >
      <template #toolbar>
        <el-radio-group v-model="activeTab" @change="onTabChange">
          <el-radio-button
            v-for="t in TABS"
            :key="t.key"
            :label="t.key"
          >
            {{ t.label }}（{{ tabCount(t.key) }}）
          </el-radio-button>
        </el-radio-group>
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

      <template #actualArriveTime="{ row }">
        {{ formatDateTime(row.actualArriveTime) || '--' }}
      </template>

      <template #createdAt="{ row }">
        {{ formatDateTime(row.createdAt) || '--' }}
      </template>

      <template #status="{ row }">
        <el-tag
          :type="(TASK_STATUS_MAP[row.status]?.type as any) || 'info'"
          size="small"
        >
          {{ TASK_STATUS_MAP[row.status]?.label || '--' }}
        </el-tag>
      </template>

      <template #action="{ row }">
        <div class="action-cell">
          <el-link
            type="primary"
            :underline="false"
            @click="emit('open-detail', row)"
          >
            详情
          </el-link>
          <!-- 仅「已签收」可逆：展示主动作（关闭任务）+ 更多（撤销签收） -->
          <template v-if="activeTab === 'signed'">
            <template v-if="getRowPrimary(row)">
              <el-divider direction="vertical" />
              <el-link
                :type="getRowPrimary(row)!.buttonType as any"
                :underline="false"
                v-permission="getRowPrimary(row)!.permission"
                @click="emit('action', row, getRowPrimary(row)!)"
              >
                {{ getRowPrimary(row)!.label }}
              </el-link>
            </template>
            <template v-if="getRowMore(row).length">
              <el-divider direction="vertical" />
              <el-dropdown trigger="click">
                <el-link type="info" :underline="false">
                  更多<el-icon style="margin-left: 2px"><ArrowDown /></el-icon>
                </el-link>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      v-for="act in getRowMore(row)"
                      :key="act.key"
                      v-permission="act.permission"
                      @click="emit('action', row, act)"
                    >
                      {{ act.label }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </template>
        </div>
      </template>
    </ele-pro-table>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, nextTick, ref, watch } from 'vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { ArrowDown, Right } from '@element-plus/icons-vue';
  import { pageTasks } from '@/api/operation/task';
  import type {
    Task,
    TaskParam,
    TaskWorkbenchStats
  } from '@/api/operation/task/model';
  import { formatDateTime } from '@/utils/date-util';
  import { CARRIER_TYPE_MAP, TASK_STATUS_MAP } from '../../task/status-config';
  import { getTaskRowActions } from '../../task/task-actions';
  import type { TaskActionConfig } from '../../task/task-actions';

  type CompletedTabKey = 'signed' | 'closed' | 'cancelled';

  const props = defineProps<{
    /** 工作台 KPI 统计，用于 Tab 计数徽标 */
    stats?: TaskWorkbenchStats | null;
    /** 父级强制刷新令牌（动作完成后递增以重载本表） */
    reloadToken?: number;
    /** 父级统一筛选条件（与上方列表同源，去除 status/子集） */
    searchWhere?: Partial<TaskParam>;
  }>();

  const emit = defineEmits<{
    (e: 'action', row: Task, action: TaskActionConfig): void;
    (e: 'open-detail', row: Task): void;
  }>();

  const TABS: Array<{ key: CompletedTabKey; label: string; status: number }> = [
    { key: 'signed', label: '已签收', status: 5 },
    { key: 'closed', label: '已关闭', status: 7 },
    { key: 'cancelled', label: '已取消', status: 9 }
  ];

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const activeTab = ref<CompletedTabKey>('signed');

  const currentStatus = computed(
    () => TABS.find((t) => t.key === activeTab.value)?.status ?? 5
  );

  const tabCount = (key: CompletedTabKey): number => {
    const totals = props.stats?.totals;
    if (!totals) return 0;
    if (key === 'signed') return totals.signed ?? 0;
    if (key === 'closed') return totals.closed ?? 0;
    return totals.cancelled ?? 0;
  };

  const columns = computed<Columns>(() => {
    const cols: Record<string, unknown>[] = [
      { type: 'index', columnKey: 'index', width: 50, align: 'center' },
      { prop: 'taskNo', label: '任务单号', minWidth: 160 },
      {
        prop: 'carrierType',
        label: '承运方式',
        width: 96,
        align: 'center',
        slot: 'carrierType'
      },
      { columnKey: 'route', label: '运输线路', minWidth: 220, slot: 'route' },
      {
        columnKey: 'carrierResource',
        label: '司机 / 车牌 / 承运商',
        minWidth: 170,
        slot: 'carrierResource'
      },
      { prop: 'totalQuantity', label: '台数', width: 70, align: 'center' },
      {
        prop: 'actualArriveTime',
        label: '实际到货',
        width: 168,
        align: 'center',
        slot: 'actualArriveTime'
      },
      {
        prop: 'createdAt',
        label: '制单时间',
        width: 168,
        align: 'center',
        slot: 'createdAt'
      },
      {
        prop: 'status',
        label: '状态',
        width: 100,
        align: 'center',
        slot: 'status'
      },
      {
        columnKey: 'action',
        label: '操作',
        width: 180,
        align: 'center',
        fixed: 'right',
        slot: 'action'
      }
    ];
    return cols as Columns;
  });

  const getRowPrimary = (row: Task): TaskActionConfig | null =>
    getTaskRowActions(row).primary;

  const getRowMore = (row: Task): TaskActionConfig[] =>
    getTaskRowActions(row).more;

  const filterParamsWithoutKeyword = (): Omit<Partial<TaskParam>, 'keyword'> => {
    const { keyword: _k, status: _s, ...rest } = props.searchWhere ?? {};
    return rest;
  };

  const datasource: DatasourceFunction = ({ pages }) => {
    const search = props.searchWhere ?? {};
    const keyword = search.keyword?.trim();
    const params: Partial<TaskParam> = {
      ...pages,
      status: currentStatus.value,
      ...filterParamsWithoutKeyword(),
      ...(keyword ? { keyword } : {})
    };
    return pageTasks(params as TaskParam).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));
  };

  const doReload = () => {
    nextTick(() => tableRef.value?.reload?.({ page: 1 }));
  };

  const onTabChange = () => {
    doReload();
  };

  watch(
    () => props.reloadToken,
    () => doReload()
  );

  watch(
    () => props.searchWhere,
    () => doReload(),
    { deep: true }
  );
</script>

<style lang="scss" scoped>
  .completed-section {
    margin-top: 12px;
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

    > .cell-ellipsis {
      flex: 1 1 0;
    }

    &__arrow {
      flex-shrink: 0;
      margin: 0 6px;
    }
  }

  .action-cell {
    display: inline-flex;
    align-items: center;
    flex-wrap: nowrap;
    white-space: nowrap;
  }
</style>
