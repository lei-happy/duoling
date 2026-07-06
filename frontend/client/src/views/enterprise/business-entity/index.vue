<template>
  <ele-page>
    <business-entity-search @search="reload" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        sticky
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="SystemBusinessEntityTable"
      >
        <template #toolbar>
          <btn-items :items="[{ preset: 'add', onClick: () => openEdit() }]" />
        </template>
        <template #isDefault="{ row }">
          <el-tag
            v-if="row.isDefault === 1"
            size="small"
            type="success"
            :disable-transitions="true"
          >
            默认
          </el-tag>
          <span v-else>—</span>
        </template>
        <template #status="{ row }">
          <el-tag
            size="small"
            :type="row.status === 1 ? 'primary' : 'info'"
            :disable-transitions="true"
          >
            {{ row.status === 1 ? '正常' : '停用' }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :items="[
              { preset: 'edit', onClick: () => openEdit(row) },
              {
                text: '设为默认',
                hidden: row.isDefault === 1 || row.status !== 1,
                onClick: () => setDefault(row)
              },
              {
                text: row.status === 1 ? '停用' : '启用',
                onClick: () => toggleStatus(row)
              },
              { preset: 'del', onClick: () => remove(row) }
            ]"
          />
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import BusinessEntitySearch from './components/business-entity-search.vue';
  import {
    pageBusinessEntities,
    removeBusinessEntity,
    setDefaultBusinessEntity,
    toggleBusinessEntityStatus
  } from '@/api/system/business-entity';
  import type {
    BusinessEntity,
    BusinessEntityParam
  } from '@/api/system/business-entity/model';

  defineOptions({ name: 'SystemBusinessEntity' });

  const { openModal } = useModal();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const columns = ref<Columns>([
    { prop: 'entityName', label: '主体名称', minWidth: 180 },
    { prop: 'entityCode', label: '主体编码', width: 120, align: 'center' },
    {
      prop: 'shortName',
      label: '简称',
      minWidth: 120,
      formatter: (row) => row.shortName || '—'
    },
    {
      prop: 'legalPerson',
      label: '法定代表人',
      minWidth: 110,
      align: 'center',
      formatter: (row) => row.legalPerson || '—'
    },
    {
      prop: 'contactPhone',
      label: '联系电话',
      minWidth: 130,
      align: 'center',
      formatter: (row) => row.contactPhone || '—'
    },
    {
      prop: 'isDefault',
      label: '默认',
      width: 80,
      align: 'center',
      slot: 'isDefault'
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status'
    },
    { prop: 'sortOrder', label: '排序号', width: 90, align: 'center' },
    { prop: 'createdAt', label: '创建时间', width: 170, align: 'center' },
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

  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    return pageBusinessEntities({ ...where, ...orders, ...pages });
  };

  const reload = (where?: BusinessEntityParam) => {
    tableRef.value?.reload?.({ where });
  };

  const openEdit = (row?: BusinessEntity | null) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/business-entity-edit.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };

  const setDefault = (row: BusinessEntity) => {
    const loading = EleMessage.loading({ message: '请求中..', plain: true });
    setDefaultBusinessEntity(row.id as number)
      .then(() => {
        loading.close();
        EleMessage.success({ message: '已设为默认主体', plain: true });
        reload();
      })
      .catch((e) => {
        loading.close();
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const toggleStatus = (row: BusinessEntity) => {
    const next = row.status === 1 ? 0 : 1;
    const loading = EleMessage.loading({ message: '请求中..', plain: true });
    toggleBusinessEntityStatus(row.id as number, next)
      .then(() => {
        loading.close();
        EleMessage.success({
          message: next === 1 ? '已启用' : '已停用',
          plain: true
        });
        reload();
      })
      .catch((e) => {
        loading.close();
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const remove = (row: BusinessEntity) => {
    ElMessageBox.confirm(`确定要删除“${row.entityName}”吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeBusinessEntity(row.id as number)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reload();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };
</script>
