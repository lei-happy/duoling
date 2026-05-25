<template>
  <ele-page>
    <approval-search @search="(where) => onSearch(where)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <el-tabs v-model="activeStatus" class="approval-tabs" @tab-change="onTabChange">
        <el-tab-pane name="1">
          <template #label>
            <span>
              待审核
              <el-badge v-if="pendingCount" :value="pendingCount" class="approval-badge" />
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="已通过" name="2" />
        <el-tab-pane label="已驳回" name="3" />
        <el-tab-pane label="全部" name="all" />
      </el-tabs>

      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :default-sort="{ prop: 'createdAt', order: 'descending' }"
        cache-key="SocialCapacityApprovalTable"
      >
        <template #approvalStatus="{ row }">
          <el-tag size="small" :type="approvalTagType(row.approvalStatus)">
            {{ approvalLabel(row.approvalStatus) }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items divider type="link" :items="actionItems(row)" />
        </template>
      </ele-pro-table>
    </ele-card>

    <social-capacity-detail
      v-model:visible="detailVisible"
      :social-capacity-id="detailId"
    >
      <template #footer="{ detail }">
        <el-button @click="detailVisible = false">关闭</el-button>
        <template v-if="detail && detail.approvalStatus === 1">
          <el-button type="success" @click="actFromDetail('approve', detail)">
            通过
          </el-button>
          <el-button type="danger" @click="actFromDetail('reject', detail)">
            驳回
          </el-button>
        </template>
      </template>
    </social-capacity-detail>

    <approval-action
      v-model:visible="actionVisible"
      :mode="actionMode"
      :row="actionRow"
      @done="onActionDone"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import ApprovalSearch from './components/approval-search.vue';
  import ApprovalAction from './components/approval-action.vue';
  import SocialCapacityDetail from '../list/components/social-capacity-detail.vue';
  import {
    pageApprovals,
    approvalStats
  } from '@/api/capacity/social-capacity/approval';
  import type {
    SocialCapacityListItem,
    SocialCapacityDetail as SCDetail
  } from '@/api/capacity/social-capacity/list/model';
  import type { SocialCapacityApprovalParam } from '@/api/capacity/social-capacity/approval/model';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'CapacitySocialApproval' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const activeStatus = ref<'1' | '2' | '3' | 'all'>('1');
  const searchWhere = ref<SocialCapacityApprovalParam>({});
  const pendingCount = ref(0);

  const detailVisible = ref(false);
  const detailId = ref<number | undefined>(undefined);

  const actionVisible = ref(false);
  const actionMode = ref<'approve' | 'reject'>('approve');
  const actionRow = ref<SocialCapacityListItem | null>(null);

  const approvalLabel = (s?: number) =>
    s === 0
      ? '草稿'
      : s === 1
        ? '待审核'
        : s === 2
          ? '已通过'
          : s === 3
            ? '已驳回'
            : '—';
  const approvalTagType = (
    s?: number
  ): 'info' | 'primary' | 'success' | 'danger' =>
    s === 1 ? 'primary' : s === 2 ? 'success' : s === 3 ? 'danger' : 'info';

  const columns = ref<Columns>([
    { prop: 'socialCode', label: '编号', minWidth: 130 },
    { prop: 'driverName', label: '姓名', minWidth: 90 },
    { prop: 'driverPhone', label: '手机号', minWidth: 120 },
    { prop: 'plateNumber', label: '车牌号', minWidth: 110 },
    { prop: 'vehicleTypeLabel', label: '车辆类型', minWidth: 100 },
    { prop: 'source', label: '来源', minWidth: 100 },
    {
      prop: 'approvalStatus',
      label: '审核状态',
      width: 100,
      align: 'center',
      slot: 'approvalStatus'
    },
    {
      prop: 'updatedAt',
      label: '提交时间',
      width: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.updatedAt)
    },
    {
      prop: 'createdAt',
      label: '创建时间',
      sortable: 'custom',
      width: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.createdAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 200,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const normalizeSortOrders = (
    orders: Record<string, string | undefined> | undefined
  ) => {
    if (!orders?.sort && !orders?.order) return {};
    const sort = orders.sort;
    let order = orders.order;
    if (typeof order === 'string') {
      const lo = order.toLowerCase();
      if (lo === 'descending') order = 'desc';
      else if (lo === 'ascending') order = 'asc';
    }
    const out: Record<string, string> = {};
    if (sort) out.sort = sort;
    if (order) out.order = order;
    return out;
  };

  const datasource: DatasourceFunction = async ({ pages, where, orders }) => {
    const filter: SocialCapacityApprovalParam = {
      ...searchWhere.value,
      ...(where as Partial<SocialCapacityApprovalParam>),
      ...normalizeSortOrders(orders as Record<string, string | undefined>),
      ...pages
    };
    if (activeStatus.value !== 'all') {
      filter.approvalStatus = Number(activeStatus.value);
    } else {
      filter.approvalStatus = undefined;
    }
    const res = await pageApprovals(filter);
    const raw = res as { list?: SocialCapacityListItem[]; count?: number; total?: number };
    return {
      list: raw?.list ?? [],
      count: raw?.count ?? raw?.total ?? 0
    };
  };

  const reload = (page = 1) => {
    tableRef.value?.reload?.({ page });
  };

  const onSearch = (where?: SocialCapacityApprovalParam) => {
    searchWhere.value = where ?? {};
    reload(1);
  };

  const onTabChange = () => reload(1);

  const refreshStats = async () => {
    try {
      const stats = await approvalStats();
      pendingCount.value = stats?.pendingCount ?? 0;
    } catch {
      pendingCount.value = 0;
    }
  };

  const openDetail = (row: SocialCapacityListItem) => {
    if (!row.id) return;
    detailId.value = row.id;
    detailVisible.value = true;
  };

  const openAction = (mode: 'approve' | 'reject', row: SocialCapacityListItem) => {
    actionMode.value = mode;
    actionRow.value = row;
    actionVisible.value = true;
  };

  const actFromDetail = (
    mode: 'approve' | 'reject',
    detail: SCDetail | null | undefined
  ) => {
    if (!detail) return;
    openAction(mode, detail as SocialCapacityListItem);
  };

  const onActionDone = () => {
    detailVisible.value = false;
    refreshStats();
    reload();
  };

  const actionItems = (row: SocialCapacityListItem) => {
    const items: any[] = [{ title: '查看', onClick: () => openDetail(row) }];
    if (row.approvalStatus === 1) {
      items.push({
        title: '通过',
        onClick: () => openAction('approve', row)
      });
      items.push({
        title: '驳回',
        danger: true,
        onClick: () => openAction('reject', row)
      });
    }
    return items;
  };

  onMounted(() => {
    refreshStats();
  });
</script>

<style scoped>
  .approval-tabs {
    margin: 0 0 4px;
  }
  .approval-badge :deep(.el-badge__content) {
    transform: scale(0.85);
  }
</style>
