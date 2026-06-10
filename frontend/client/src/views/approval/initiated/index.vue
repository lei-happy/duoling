<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <div class="approval-toolbar">
        <el-input
          v-model="keyword"
          clearable
          placeholder="搜索单号 / 事项"
          style="width: 220px"
          @keyup.enter="reload(1)"
          @clear="reload(1)"
        />
        <el-select
          v-model="status"
          clearable
          placeholder="状态"
          style="width: 130px"
          @change="reload(1)"
        >
          <el-option :value="0" label="审批中" />
          <el-option :value="1" label="已通过" />
          <el-option :value="2" label="已拒绝" />
          <el-option :value="3" label="已撤回" />
        </el-select>
        <el-button type="primary" @click="reload(1)">查询</el-button>
      </div>
      <ele-pro-table
        ref="tableRef"
        row-key="instanceId"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        cache-key="ApprovalInitiatedTable"
      >
        <template #status="{ row }">
          <el-tag size="small" :type="statusTag(row.status)">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <el-link type="primary" :underline="false" @click="openDetail(row)">
            查看
          </el-link>
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
  import { onActivated, onMounted, ref } from 'vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import ApprovalDetailDrawer from '../components/approval-detail-drawer.vue';
  import { listInitiated } from '@/api/approval';
  import type { ApprovalListItem } from '@/api/approval/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    instanceStatusLabel as statusLabel,
    instanceStatusTag as statusTag,
    bizTypeLabel
  } from '../constants';

  defineOptions({ name: 'ApprovalInitiated' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const keyword = ref('');
  const status = ref<number | undefined>(undefined);

  const detailVisible = ref(false);
  const detailId = ref<number | undefined>(undefined);

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

  const datasource: DatasourceFunction = async ({ pages }) => {
    const res = await listInitiated({
      keyword: keyword.value || undefined,
      status: status.value,
      ...pages
    });
    return { list: res?.list ?? [], count: res?.count ?? 0 };
  };

  const reload = (page?: number) => {
    tableRef.value?.reload?.(page ? { page } : undefined);
  };

  const openDetail = (row: ApprovalListItem) => {
    detailId.value = row.instanceId;
    detailVisible.value = true;
  };

  onMounted(() => reload());
  onActivated(() => reload());
</script>

<style lang="scss" scoped>
  .approval-toolbar {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
  }
</style>
