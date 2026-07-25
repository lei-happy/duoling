<template>
  <ele-page>
    <initiated-search @search="onSearch" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="instanceId"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="ApprovalInitiatedTable"
      >
        <template #status="{ row }">
          <el-tag size="small" :type="statusTag(row.status)">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :items="[{ title: '查看', onClick: () => openDetail(row) }]"
          />
        </template>
      </ele-pro-table>
    </ele-card>

    <approval-detail-drawer
      v-model:visible="detailVisible"
      :instance-id="detailId"
      @changed="reload()"
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
  import InitiatedSearch from '../components/initiated-search.vue';
  import ApprovalDetailDrawer from '../components/approval-detail-drawer.vue';
  import { listInitiated } from '@/api/approval';
  import type {
    ApprovalListItem,
    ApprovalListParam
  } from '@/api/approval/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    instanceStatusLabel as statusLabel,
    instanceStatusTag as statusTag,
    bizTypeLabel
  } from '../constants';

  defineOptions({ name: 'ApprovalInitiated' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const where = reactive<Pick<ApprovalListParam, 'keyword' | 'status'>>({
    keyword: '',
    status: void 0
  });

  const detailVisible = ref(false);
  const detailId = ref<number | undefined>(undefined);

  const onSearch = (payload: Pick<ApprovalListParam, 'keyword' | 'status'>) => {
    where.keyword = payload.keyword ?? '';
    where.status = payload.status;
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
    {
      prop: 'status',
      label: '状态',
      width: 100,
      align: 'center',
      slot: 'status'
    },
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
      width: 90,
      align: 'center',
      slot: 'action',
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit, pages }) => {
    const p = page ?? (Number(pages?.page) || 1);
    const l = limit ?? (Number(pages?.limit) || 10);
    const res = await listInitiated({
      keyword: where.keyword || undefined,
      status: where.status,
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

  onActivated(() => reload());
</script>
