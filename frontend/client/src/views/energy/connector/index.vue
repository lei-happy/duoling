<template>
  <ele-page>
    <connector-search
      :suppliers="suppliers"
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
        cache-key="EnergyConnectorTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'add',
                title: '新增接入',
                permission: 'energy:connector:add',
                onClick: () => openAdd()
              }
            ]"
          />
        </template>
        <template #connectorCode="{ row }">
          {{ labelOf(CONNECTOR_CODES, row.connectorCode) }}
        </template>
        <template #lastSyncTime="{ row }">
          {{ formatDateTime(row.lastSyncTime) }}
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
    <input
      ref="fileRef"
      type="file"
      accept=".xlsx,.xls,.csv"
      class="hidden-file"
      @change="onFilePicked"
    />
    <connector-edit
      v-model:visible="visible"
      :suppliers="suppliers"
      :accounts="accounts"
      @done="reload"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { Refresh, Upload } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    importConnector,
    pageConnectors,
    pullConnector
  } from '@/api/energy';
  import { formatDateTime } from '@/utils/date-util';
  import { CONNECTOR_CODES, asPage, labelOf } from '../_shared/options';
  import { buildActionColumnItems } from '../_shared/action-column';
  import { useEnergyLookups } from '../_shared/use-lookups';
  import ConnectorSearch from './components/connector-search.vue';
  import ConnectorEdit from './components/connector-edit.vue';
  import type { ConnectorSearchParam } from './components/connector-search.vue';

  defineOptions({ name: 'EnergyConnector' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const fileRef = ref<HTMLInputElement | null>(null);
  const importRow = ref<Record<string, any> | null>(null);
  const { suppliers, accounts, loadSuppliers, loadAccounts } = useEnergyLookups();
  const where = reactive<ConnectorSearchParam>({});
  const visible = ref(false);

  const columns = ref<Columns>([
    { prop: 'connectorName', label: '名称', minWidth: 180 },
    {
      prop: 'connectorCode',
      label: '类型',
      width: 140,
      slot: 'connectorCode'
    },
    { prop: 'syncMode', label: '同步方式', width: 110, align: 'center' },
    {
      prop: 'lastSyncTime',
      label: '最近同步',
      minWidth: 170,
      slot: 'lastSyncTime'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 180,
      minWidth: 180,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = async ({ pages, where: tableWhere }) => {
    return asPage(await pageConnectors({ ...(tableWhere || where), ...pages }));
  };

  const reload = (next?: ConnectorSearchParam, page?: number) => {
    if (next) Object.assign(where, next);
    tableRef.value?.reload?.({ where: { ...where }, page });
  };

  const openAdd = async () => {
    await Promise.all([loadSuppliers(), loadAccounts()]);
    visible.value = true;
  };

  const actionItems = (row: any): ButtonItem[] => {
    const visibleItems: ButtonDropdownItem[] = [];
    if (row.connectorCode === 'excel') {
      visibleItems.push({
        title: '导入 Excel',
        icon: Upload,
        permission: 'energy:connector:sync',
        onClick: () => pickFile(row)
      });
    }
    visibleItems.push({
      title: '立即同步',
      icon: Refresh,
      permission: 'energy:connector:sync',
      onClick: () => doPull(row)
    });
    return buildActionColumnItems(visibleItems);
  };

  const pickFile = (row: any) => {
    importRow.value = row;
    if (fileRef.value) {
      fileRef.value.value = '';
      fileRef.value.click();
    }
  };

  const onFilePicked = async (e: Event) => {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (!file || !importRow.value) return;
    try {
      const res: any = await importConnector(importRow.value.id, file);
      EleMessage.success({
        message: `已导入 ${res.imported ?? 0} 笔，重复 ${res.duplicated ?? 0} 笔`,
        plain: true
      });
      reload();
    } catch (err: any) {
      EleMessage.error({
        message: err.message || '导入失败，请检查文件后重试',
        plain: true
      });
    }
  };

  const doPull = async (row: any) => {
    try {
      await pullConnector(row.id);
      EleMessage.success({ message: '已发起同步', plain: true });
      reload();
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '同步失败，请稍后重试',
        plain: true
      });
    }
  };

  onMounted(() => {
    loadSuppliers();
  });
</script>

<style scoped>
  .hidden-file {
    display: none;
  }
</style>
