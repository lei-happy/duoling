<template>
  <ele-page>
    <log-search :where="defaultWhere" @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        :where="defaultWhere"
        cache-key="OpenPlatformLogsTable"
      >
        <template #channel="{ row }">
          <el-tag
            size="small"
            :type="row.channel === 'api' ? 'primary' : 'success'"
            :disable-transitions="true"
          >
            {{ channelText(row.channel) }}
          </el-tag>
        </template>
        <template #status="{ row }">
          <el-tag
            size="small"
            :type="callStatusTagType(row.status)"
            :disable-transitions="true"
          >
            {{ callStatusText(row.status) }}
          </el-tag>
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import LogSearch from './components/log-search.vue';
  import { pageCallLogs } from '@/api/open-platform';
  import type { CallLogParam } from '@/api/open-platform/model';
  import { callStatusTagType, callStatusText, channelText } from '../constants';

  defineOptions({ name: 'OpenPlatformLogs' });

  const defaultWhere = reactive<CallLogParam>({
    capability_code: '',
    channel: '',
    status: ''
  });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const columns = ref<Columns>([
    { prop: 'created_at', label: '调用时间', width: 170, align: 'center' },
    { prop: 'capability_code', label: '能力', minWidth: 160 },
    {
      prop: 'channel',
      label: '通道',
      width: 100,
      align: 'center',
      slot: 'channel'
    },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'latency_ms',
      label: '耗时',
      width: 100,
      align: 'center',
      formatter: (row) =>
        row.latency_ms != null ? `${row.latency_ms} ms` : '—'
    },
    {
      prop: 'client_ip',
      label: '来源 IP',
      width: 140,
      align: 'center',
      formatter: (row) => row.client_ip || '—'
    },
    {
      prop: 'result_summary',
      label: '结果摘要',
      minWidth: 200,
      formatter: (row) => row.result_summary || '—'
    },
    {
      prop: 'request_id',
      label: '请求编号',
      minWidth: 180,
      formatter: (row) => row.request_id || '—'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where }) => {
    return pageCallLogs({ ...where, ...pages } as CallLogParam);
  };

  const reload = (where?: CallLogParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };
</script>
