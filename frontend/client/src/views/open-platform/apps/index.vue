<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        sticky
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        cache-key="OpenPlatformAppsTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'add',
                title: '新建应用',
                permission: PERM_CREATE,
                onClick: () => openEdit()
              }
            ]"
          />
        </template>
        <template #status="{ row }">
          <el-tag
            size="small"
            :type="statusTagType(row.status)"
            :disable-transitions="true"
          >
            {{ statusText(row.status) }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items divider type="link" :items="actionItems(row)" />
        </template>
      </ele-pro-table>
    </ele-card>
    <app-detail ref="detailRef" />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import AppDetail from './components/app-detail.vue';
  import { listApps, updateApp } from '@/api/open-platform';
  import type { OpenApp } from '@/api/open-platform/model';
  import { statusTagType, statusText } from '../constants';

  defineOptions({ name: 'OpenPlatformApps' });

  const PERM_CREATE = 'open-platform:app:create';
  const PERM_EDIT = 'open-platform:app:edit';

  const { openModal } = useModal();
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const detailRef = ref<InstanceType<typeof AppDetail> | null>(null);

  const columns = ref<Columns>([
    { prop: 'name', label: '应用名称', minWidth: 160 },
    {
      prop: 'description',
      label: '用途备注',
      minWidth: 200,
      formatter: (row) => row.description || '—'
    },
    {
      prop: 'credential_count',
      label: '有效密钥',
      width: 100,
      align: 'center',
      formatter: (row) => `${row.credential_count ?? 0} 把`
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status'
    },
    { prop: 'created_at', label: '创建时间', width: 170, align: 'center' },
    {
      columnKey: 'action',
      label: '操作',
      width: 240,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const actionItems = (row: OpenApp) => [
    { title: '管理接入', onClick: () => detailRef.value?.open(row) },
    { preset: 'edit', permission: PERM_EDIT, onClick: () => openEdit(row) },
    {
      title: row.status === 'enabled' ? '停用' : '启用',
      permission: PERM_EDIT,
      onClick: () => toggleStatus(row)
    }
  ];

  const datasource: DatasourceFunction = async () => {
    const list = await listApps();
    return { list, count: list.length };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openEdit = (row?: OpenApp | null) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/app-edit.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };

  const toggleStatus = (row: OpenApp) => {
    const next = row.status === 'enabled' ? 'disabled' : 'enabled';
    const loading = EleMessage.loading({
      message: next === 'enabled' ? '正在启用，请稍候…' : '正在停用，请稍候…',
      plain: true
    });
    updateApp(row.id as number, { name: row.name as string, status: next })
      .then(() => {
        loading.close();
        EleMessage.success({
          message: next === 'enabled' ? '已启用' : '已停用',
          plain: true
        });
        reload();
      })
      .catch((e) => {
        loading.close();
        EleMessage.error({
          message: e.message || '操作失败，请稍后重试',
          plain: true
        });
      });
  };
</script>
