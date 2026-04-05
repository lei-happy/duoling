<template>
  <ele-page>
    <role-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="roleId"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :export-config="{ fileName: '角色数据', datasource: exportSource }"
        :print-config="{ datasource: exportSource }"
        cache-key="SystemRoleTable"
      >
        <template #toolbar>
          <btn-items
            :items="[{ preset: 'add', onClick: () => openEdit() }]"
          />
        </template>
        <template #action="{ row }">
          <btn-items
            :divider="true"
            type="link"
            :items="[
              { preset: 'edit', onClick: () => openEdit(row) },
              {
                title: '分配权限',
                icon: AppstoreAddOutlined,
                onClick: () => openAuth(row)
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
  import { AppstoreAddOutlined } from '@/components/icons';
  import RoleSearch from './components/role-search.vue';
  import { pageRoles, removeRole, listRoles } from '@/api/system/role';
  import type { Role, RoleParam } from '@/api/system/role/model';

  defineOptions({ name: 'SystemRole' });

  const { openModal } = useModal();

  /** 表格实例 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      prop: 'roleName',
      label: '角色名称',
      minWidth: 120
    },
    {
      prop: 'roleCode',
      label: '角色标识',
      minWidth: 120
    },
    {
      prop: 'comments',
      label: '角色描述',
      minWidth: 140
    },
    {
      prop: 'createTime',
      label: '创建时间',
      sortable: 'custom',
      width: 180,
      align: 'center'
    },
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

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    return pageRoles({ ...where, ...orders, ...pages });
  };

  /** 搜索 */
  const reload = (where?: RoleParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  /** 打开编辑弹窗 */
  const openEdit = (row?: Role) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/role-edit.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };

  /** 打开权限分配弹窗 */
  const openAuth = (row?: Role) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/role-auth.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };

  /** 删除单行 */
  const remove = (row: Role) => {
    ElMessageBox.confirm(
      `确定要删除“${row.roleName}”吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeRole(row.roleId)
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

  /** 导出和打印全部数据的数据源 */
  const exportSource: DatasourceFunction = ({ where, orders }) => {
    return listRoles({ ...where, ...orders });
  };
</script>
