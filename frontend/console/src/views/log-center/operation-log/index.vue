<template>
  <ele-page>
    <operation-log-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="LogCenterOperationLogTable"
      >
        <template #status="{ row }">
          <el-tag
            v-if="row.status === 1"
            size="small"
            type="success"
            :disable-transitions="true"
          >
            成功
          </el-tag>
          <el-tag
            v-else-if="row.status === 0"
            size="small"
            type="danger"
            :disable-transitions="true"
          >
            失败
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :items="[{ preset: 'detail', onClick: () => openDetail(row) }]"
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
  import OperationLogSearch from './components/operation-log-search.vue';
  import { pageTenantOperationLogs } from '@/api/log-center';
  import type {
    TenantOperationLog,
    TenantOperationLogParam
  } from '@/api/log-center/model';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'LogCenterOperationLog' });

  const tenantDisplayName = (row: TenantOperationLog) => {
    const name = row.tenantShortName?.trim();
    if (name) return name;
    return row.tenantCode?.trim() || '-';
  };

  const operatorDisplayName = (row: TenantOperationLog) => {
    const name = row.realName?.trim();
    if (name) return name;
    return row.username?.trim() || '-';
  };

  const { openModal } = useModal();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const columns = ref<Columns>([
    {
      prop: 'tenantCode',
      label: '租户',
      minWidth: 120,
      formatter: (row) => tenantDisplayName(row)
    },
    {
      prop: 'username',
      label: '操作用户',
      minWidth: 110,
      formatter: (row) => operatorDisplayName(row)
    },
    {
      prop: 'module',
      label: '操作模块',
      minWidth: 110
    },
    {
      prop: 'action',
      label: '操作类型',
      minWidth: 100
    },
    {
      prop: 'description',
      label: '操作描述',
      minWidth: 120
    },
    {
      prop: 'requestUrl',
      label: '请求地址',
      minWidth: 160
    },
    {
      prop: 'requestMethod',
      label: '请求方式',
      width: 100,
      align: 'center'
    },
    {
      prop: 'status',
      label: '状态',
      sortable: 'custom',
      width: 90,
      align: 'center',
      slot: 'status',
      filters: [
        { text: '成功', value: '1' },
        { text: '失败', value: '0' }
      ],
      filterMultiple: false,
      formatter: (row) => (row.status === 1 ? '成功' : '失败')
    },
    {
      prop: 'elapsedTime',
      label: '耗时',
      sortable: 'custom',
      width: 90,
      formatter: (row) =>
        row.elapsedTime != null ? `${row.elapsedTime}ms` : '-',
      align: 'center'
    },
    {
      prop: 'createdAt',
      label: '操作时间',
      sortable: 'custom',
      align: 'center',
      width: 170,
      formatter: (row) => formatDateTime(row.createdAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 90,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = ({
    pages,
    where,
    orders,
    filters
  }) => {
    return pageTenantOperationLogs({
      ...where,
      ...orders,
      ...filters,
      ...pages
    });
  };

  const reload = (where?: TenantOperationLogParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  const openDetail = (row: TenantOperationLog) => {
    openModal({
      props: { title: '操作日志详情', width: 720 },
      asyncComponent: () =>
        import('./components/operation-log-detail.vue'),
      componentProps: { data: row }
    });
  };
</script>
