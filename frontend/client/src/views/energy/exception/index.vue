<template>
  <ele-page>
    <exception-search
      :stats="stats"
      @search="(where) => reload(where, 1)"
    />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="EnergyExceptionTable"
      >
        <template #exceptionType="{ row }">
          {{ EXCEPTION_TYPES[row.exceptionType] || row.exceptionType }}
        </template>
        <template #status="{ row }">
          <el-tag
            :type="row.status === 'pending' ? 'warning' : row.status === 'processed' ? 'success' : 'info'"
            size="small"
            :disable-transitions="true"
          >
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :wrap="false"
            :items="actionItems(row)"
          />
        </template>
      </ele-pro-table>
    </ele-card>
    <exception-resolve
      v-model:visible="visible"
      :data="resolveData"
      :next-status="nextStatus"
      @done="onResolved"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { CircleCheck, CircleClose } from '@element-plus/icons-vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { exceptionStats, pageExceptions } from '@/api/energy';
  import { EXCEPTION_TYPES, asPage } from '../_shared/options';
  import { buildActionColumnItems } from '../_shared/action-column';
  import ExceptionSearch from './components/exception-search.vue';
  import ExceptionResolve from './components/exception-resolve.vue';
  import type { ExceptionSearchParam } from './components/exception-search.vue';

  defineOptions({ name: 'EnergyException' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const where = reactive<ExceptionSearchParam>({});
  const stats = ref<Record<string, number>>({});
  const visible = ref(false);
  const resolveData = ref<Record<string, any> | null>(null);
  const nextStatus = ref('processed');

  const columns = ref<Columns>([
    {
      prop: 'exceptionType',
      label: '类型',
      width: 160,
      slot: 'exceptionType'
    },
    { prop: 'riskLevel', label: '等级', width: 90, align: 'center' },
    { prop: 'exceptionMessage', label: '说明', minWidth: 280 },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 160,
      minWidth: 160,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const statusLabel = (status?: string) => {
    if (status === 'pending') return '待处理';
    if (status === 'processed') return '已处理';
    if (status === 'ignored') return '已忽略';
    return status || '-';
  };

  const loadStats = async () => {
    try {
      stats.value = (await exceptionStats()) || {};
    } catch {
      stats.value = {};
    }
  };

  const datasource: DatasourceFunction = async ({ pages, where: tableWhere }) => {
    return asPage(
      await pageExceptions({ ...(tableWhere || where), ...pages })
    );
  };

  const reload = (next?: ExceptionSearchParam, page?: number) => {
    if (next) Object.assign(where, next);
    tableRef.value?.reload?.({ where: { ...where }, page });
    loadStats();
  };

  const actionItems = (row: any): ButtonItem[] => {
    if (row.status !== 'pending') return [];
    const visibleItems: ButtonDropdownItem[] = [
      {
        title: '已核实',
        icon: CircleCheck,
        permission: 'energy:exception:process',
        onClick: () => openResolve(row, 'processed')
      },
      {
        title: '忽略',
        icon: CircleClose,
        permission: 'energy:exception:process',
        onClick: () => openResolve(row, 'ignored')
      }
    ];
    return buildActionColumnItems(visibleItems);
  };

  const openResolve = (row: any, status: string) => {
    resolveData.value = row;
    nextStatus.value = status;
    visible.value = true;
  };

  const onResolved = () => {
    reload();
  };

  onMounted(() => {
    loadStats();
  });
</script>
