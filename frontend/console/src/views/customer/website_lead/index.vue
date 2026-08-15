<template>
  <ele-page>
    <lead-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="CustomerWebsiteLeadTable"
      >
        <template #stage="{ row }">
          <span v-if="row.stage_band">
            {{ row.stage_band }} · {{ row.stage_name }}
          </span>
          <span v-else class="lead-muted">未做自测</span>
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
        <template #action="{ row }">
          <btn-items
            :divider="true"
            type="link"
            :items="[{ title: '跟进', onClick: () => openFollow(row) }]"
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
  import LeadSearch from './components/lead-search.vue';
  import { pageWebsiteLeads } from '@/api/website-lead';
  import type { WebsiteLead, WebsiteLeadParam } from '@/api/website-lead/model';
  import { fleetLabel, statusLabel, statusTagType } from './constants';

  defineOptions({ name: 'CustomerWebsiteLead' });

  const { openModal } = useModal();
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const columns = ref<Columns>([
    { type: 'index', columnKey: 'index', width: 50, align: 'center' },
    { prop: 'company_name', label: '企业名称', minWidth: 180 },
    { prop: 'contact_person', label: '联系人', width: 100 },
    { prop: 'contact_phone', label: '手机号', width: 120 },
    {
      prop: 'fleet_size',
      label: '车队规模',
      width: 110,
      formatter: (row: WebsiteLead) => fleetLabel(row.fleet_size)
    },
    {
      prop: 'stage_band',
      label: '测评档位',
      width: 150,
      slot: 'stage'
    },
    {
      prop: 'total_score',
      label: '总分',
      width: 80,
      align: 'center',
      formatter: (row: WebsiteLead) =>
        row.total_score == null ? '-' : `${row.total_score}/80`
    },
    {
      prop: 'pain_point',
      label: '最头疼的事',
      minWidth: 200,
      formatter: (row: WebsiteLead) => row.pain_point || '-'
    },
    {
      prop: 'status',
      label: '跟进状态',
      width: 100,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'handler_name',
      label: '跟进人',
      width: 100,
      formatter: (row: WebsiteLead) => row.handler_name || '-'
    },
    {
      prop: 'created_at',
      label: '留资时间',
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
    return pageWebsiteLeads({
      ...where,
      page: pages?.page,
      limit: pages?.limit
    });
  };

  const reload = (where?: WebsiteLeadParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  const openFollow = (row: WebsiteLead) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/lead-follow.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };
</script>

<style scoped>
  .lead-muted {
    color: var(--el-text-color-placeholder);
  }
</style>
