<template>
  <ele-page>
    <task-search @search="(w) => reload(w, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        v-model:selections="selections"
        :default-sort="{ prop: 'createdAt', order: 'descending' }"
        cache-key="OperationTaskTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '新增任务单', onClick: () => openEdit() }
            ]"
          />
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
        </template>

        <template #prepaidAmount="{ row }">
          <span style="font-variant-numeric: tabular-nums">
            {{ formatAmount(row.prepaidAmount) }}
          </span>
        </template>

        <template #action="{ row }">
          <el-link type="primary" :underline="false" @click="openDetail(row)">
            详情
          </el-link>
          <template v-if="canEdit(row)">
            <el-divider direction="vertical" />
            <el-link type="primary" :underline="false" @click="openEdit(row)">
              编辑
            </el-link>
          </template>
          <template v-if="canCancel(row)">
            <el-divider direction="vertical" />
            <el-link type="warning" :underline="false" @click="cancelRow(row)">
              取消
            </el-link>
          </template>
          <template v-if="canDelete(row)">
            <el-divider direction="vertical" />
            <el-link type="danger" :underline="false" @click="remove(row)">
              删除
            </el-link>
          </template>
        </template>
      </ele-pro-table>
    </ele-card>

    <task-edit v-model:visible="editVisible" :data="editData" @done="reload" />
    <task-detail
      v-model:visible="detailVisible"
      :task-id="detailTaskId"
      @done="reload"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, ref, nextTick } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { Right } from '@element-plus/icons-vue';
  import TaskEdit from './components/task-edit.vue';
  import TaskDetail from './components/task-detail.vue';
  import TaskSearch from './components/task-search.vue';
  import { pageTasks, removeTask, cancelTask } from '@/api/operation/task';
  import type { Task, TaskParam } from '@/api/operation/task/model';
  import { formatDateTime } from '@/utils/date-util';
  import { CARRIER_TYPE_MAP, TASK_STATUS_MAP } from './status-config';

  defineOptions({ name: 'OperationTask' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Task[]>([]);
  const editVisible = ref(false);
  const editData = ref<Task | null>(null);
  const detailVisible = ref(false);
  const detailTaskId = ref<number | null>(null);

  const formatAmount = (v?: number | null) => {
    if (v === null || v === undefined) return '--';
    return Number(v).toFixed(2);
  };

  const columns = computed<Columns>(() => [
    { prop: 'taskNo', label: '任务单号', minWidth: 160 },
    { prop: 'taskName', label: '任务名称', minWidth: 140 },
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
      minWidth: 260,
      slot: 'route'
    },
    {
      columnKey: 'carrierResource',
      label: '司机/车牌/承运商',
      minWidth: 200,
      slot: 'carrierResource'
    },
    {
      prop: 'totalQuantity',
      label: '台数',
      width: 80,
      align: 'center'
    },
    {
      prop: 'waybillCount',
      label: '运单数',
      width: 80,
      align: 'center'
    },
    {
      prop: 'plannedLoadTime',
      label: '计划装车',
      width: 150,
      align: 'center',
      formatter: (row) => formatDateTime(row.plannedLoadTime) || '--'
    },
    {
      prop: 'prepaidAmount',
      label: '已预付',
      width: 100,
      align: 'right',
      slot: 'prepaidAmount'
    },
    {
      prop: 'status',
      label: '状态',
      width: 88,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'createdAt',
      label: '创建时间',
      width: 160,
      align: 'center',
      formatter: (row) => formatDateTime(row.createdAt) || '--'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 200,
      align: 'center',
      fixed: 'right',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where }) => {
    return pageTasks({
      ...(where as TaskParam | undefined),
      ...pages
    }).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));
  };

  const reload = (where?: TaskParam, page?: number) => {
    const t = tableRef.value;
    if (!t) return;
    const hasWhere = where !== undefined;
    const hasPage = page !== undefined;
    if (!hasWhere && !hasPage) {
      nextTick(() => t.reload?.());
      return;
    }
    const opt: { where?: TaskParam; page?: number } = {};
    if (hasWhere) opt.where = where;
    if (hasPage) opt.page = page;
    t.reload?.(opt);
  };

  const canEdit = (row: Task) =>
    row.status !== undefined && (row.status === 0 || row.status === 1);
  const canCancel = (row: Task) =>
    row.status !== undefined && [0, 1, 2].includes(row.status);
  const canDelete = (row: Task) =>
    row.status !== undefined && (row.status === 0 || row.status === 9);

  const openEdit = (row?: Task) => {
    editData.value = row ? { ...row } : null;
    editVisible.value = true;
  };

  const openDetail = (row: Task) => {
    detailTaskId.value = row.id ?? null;
    detailVisible.value = true;
  };

  const cancelRow = async (row: Task) => {
    if (!row.id) return;
    try {
      const { value: reason } = await ElMessageBox.prompt(
        '请输入取消原因（可选）',
        '取消任务单',
        {
          confirmButtonText: '确定',
          cancelButtonText: '不取消',
          inputPlaceholder: '取消原因'
        }
      );
      await cancelTask(row.id, reason || undefined);
      EleMessage.success({ message: '已取消任务单', plain: true });
      reload();
    } catch (err: unknown) {
      const e = err as { message?: string } | string | undefined;
      if (e === 'cancel') return;
      const msg = (typeof e === 'object' && e?.message) || '取消失败';
      if (msg !== 'cancel') {
        EleMessage.error({ message: msg, plain: true });
      }
    }
  };

  const remove = async (row: Task) => {
    if (!row.id) return;
    try {
      await ElMessageBox.confirm(
        `确定要删除任务单「${row.taskNo}」吗？`,
        '提示',
        { type: 'warning' }
      );
      await removeTask(row.id);
      EleMessage.success({ message: '删除成功', plain: true });
      reload();
    } catch (err: unknown) {
      const e = err as { message?: string } | string | undefined;
      if (e === 'cancel') return;
      const msg = (typeof e === 'object' && e?.message) || '';
      if (msg) EleMessage.error({ message: msg, plain: true });
    }
  };
</script>

<style lang="scss" scoped>
  .route-cell {
    display: flex;
    align-items: center;
    gap: 4px;
    flex-wrap: wrap;
  }
</style>
