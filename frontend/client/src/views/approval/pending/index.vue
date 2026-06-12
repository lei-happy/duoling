<template>
  <ele-page>
    <pending-search @search="onSearch" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="instanceId"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="ApprovalPendingTable"
      >
        <template #status="{ row }">
          <el-tag size="small" :type="statusTag(row.status)">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items divider type="link" :items="actionItems(row)" />
        </template>
      </ele-pro-table>
    </ele-card>

    <approval-detail-drawer
      v-model:visible="detailVisible"
      :instance-id="detailId"
      @changed="reload()"
    />

    <approval-action-modal
      v-model:visible="actionVisible"
      :mode="actionMode"
      :task-id="actionTaskId"
      @done="reload()"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { onActivated, reactive, ref } from 'vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import PendingSearch from '../components/pending-search.vue';
  import ApprovalDetailDrawer from '../components/approval-detail-drawer.vue';
  import ApprovalActionModal from '../components/approval-action-modal.vue';
  import { listPending } from '@/api/approval';
  import type { ApprovalListItem, ApprovalListParam } from '@/api/approval/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    instanceStatusLabel as statusLabel,
    instanceStatusTag as statusTag,
    bizTypeLabel
  } from '../constants';

  defineOptions({ name: 'ApprovalPending' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const where = reactive<Pick<ApprovalListParam, 'keyword'>>({
    keyword: ''
  });

  const detailVisible = ref(false);
  const detailId = ref<number | undefined>(undefined);

  const actionVisible = ref(false);
  const actionMode = ref<'agree' | 'reject'>('agree');
  const actionTaskId = ref<number | undefined>(undefined);

  const onSearch = (payload: Pick<ApprovalListParam, 'keyword'>) => {
    where.keyword = payload.keyword ?? '';
    tableRef.value?.reload?.({ page: 1 });
  };

  const columns = ref<Columns>([
    { prop: 'title', label: '审批事项', minWidth: 160 },
    {
      prop: 'bizType',
      label: '类型',
      width: 150,
      formatter: (row) => bizTypeLabel(row.bizType)
    },
    { prop: 'instanceNo', label: '单号', width: 150 },
    { prop: 'initiatorName', label: '发起人', width: 110 },
    {
      prop: 'submittedAt',
      label: '提交时间',
      width: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.submittedAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 180,
      align: 'center',
      slot: 'action',
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit, pages }) => {
    const p = page ?? (Number(pages?.page) || 1);
    const l = limit ?? (Number(pages?.limit) || 10);
    const res = await listPending({
      keyword: where.keyword || undefined,
      page: p,
      limit: l
    });
    return { list: res?.list ?? [], count: res?.count ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openDetail = (row: ApprovalListItem) => {
    detailId.value = row.instanceId;
    detailVisible.value = true;
  };

  const openAction = (mode: 'agree' | 'reject', row: ApprovalListItem) => {
    actionMode.value = mode;
    actionTaskId.value = row.taskId;
    actionVisible.value = true;
  };

  const actionItems = (row: ApprovalListItem) => [
    { title: '查看', onClick: () => openDetail(row) },
    { title: '同意', onClick: () => openAction('agree', row) },
    { title: '驳回', danger: true, onClick: () => openAction('reject', row) }
  ];

  onActivated(() => reload());
</script>
