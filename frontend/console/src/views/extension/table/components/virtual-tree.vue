<template>
  <div>
    <ele-pro-table
      :height="378"
      :virtual="true"
      row-key="menuId"
      :columns="columns"
      :datasource="datasource"
      :lazy="true"
      :pagination="false"
      :show-overflow-tooltip="true"
      :export-config="{ fileName: '菜单数据', datasource: exportSource }"
      :print-config="{ datasource: exportSource }"
    />
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { toTree } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { listMenus } from '@/api/system/menu';

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      type: 'index',
      columnKey: 'index',
      width: 50,
      align: 'center'
    },
    {
      prop: 'title',
      label: '菜单名称',
      minWidth: 160
    },
    {
      prop: 'path',
      label: '路由地址',
      minWidth: 180
    },
    {
      prop: 'sortNumber',
      label: '排序',
      width: 100,
      align: 'center'
    },
    {
      prop: 'createTime',
      label: '创建时间',
      width: 220,
      align: 'center'
    }
  ]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ where, parent }) => {
    return listMenus({ ...where, parentId: parent?.menuId || 0 });
  };

  /** 导出和打印全部数据的数据源 */
  const exportSource: DatasourceFunction = async ({ where }) => {
    const data = await listMenus({ ...where });
    return toTree({
      data,
      idField: 'menuId',
      parentIdField: 'parentId'
    });
  };
</script>
