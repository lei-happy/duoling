<template>
  <ele-page>
    <feedback-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="CustomerVoiceFeedbackTable"
      >
        <template #type="{ row }">
          <el-tag size="small" :disable-transitions="true">
            {{ typeLabel(row.feedback_type) }}
          </el-tag>
        </template>
        <template #status="{ row }">
          <el-tag
            :type="statusTagType(row.status)"
            size="small"
            :disable-transitions="true"
          >
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
        <template #replied="{ row }">
          <el-tag
            :type="row.reply ? 'success' : 'info'"
            size="small"
            :disable-transitions="true"
          >
            {{ row.reply ? '已回复' : '未回复' }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items
            :divider="true"
            type="link"
            :items="[{ title: '处理', onClick: () => openHandle(row) }]"
          />
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import FeedbackSearch from './components/feedback-search.vue';
  import { pageFeedbacks } from '@/api/feedback';
  import type { Feedback, FeedbackParam } from '@/api/feedback/model';

  defineOptions({ name: 'CustomerVoiceFeedback' });

  const { openModal } = useModal();
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const typeLabel = (t?: number) =>
    ({ 0: '建议', 1: '缺陷', 2: '投诉', 3: '其他' })[t ?? -1] || '-';

  const statusLabel = (s?: number) =>
    ({ 0: '待处理', 1: '处理中', 2: '已解决', 3: '已关闭' })[s ?? -1] || '-';

  const statusTagType = (s?: number) =>
    ({ 0: 'info', 1: 'warning', 2: 'success', 3: 'info' })[s ?? -1] || 'info';

  const columns = ref<Columns>([
    { type: 'index', columnKey: 'index', width: 50, align: 'center' },
    {
      prop: 'tenant_code',
      label: '租户',
      minWidth: 140,
      formatter: (row: Feedback) =>
        row.tenant_name || row.tenant_code || '-'
    },
    {
      prop: 'user_name',
      label: '提交人',
      width: 110,
      formatter: (row: Feedback) => row.user_name || '-'
    },
    {
      prop: 'contact_phone',
      label: '手机',
      width: 120,
      formatter: (row: Feedback) => row.contact_phone || '-'
    },
    {
      prop: 'feedback_type',
      label: '类型',
      width: 90,
      align: 'center',
      slot: 'type'
    },
    { prop: 'title', label: '标题', minWidth: 180 },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'reply',
      label: '是否已回复',
      width: 100,
      align: 'center',
      slot: 'replied'
    },
    {
      prop: 'created_at',
      label: '提交时间',
      width: 170,
      align: 'center'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 100,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where }) => {
    return pageFeedbacks({
      ...where,
      page: pages?.page,
      limit: pages?.limit
    });
  };

  const reload = (where?: FeedbackParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  const openHandle = (row: Feedback) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/feedback-handle.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };
</script>
