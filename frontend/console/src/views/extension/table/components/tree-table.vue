<template>
  <div>
    <ele-pro-table
      ref="tableRef"
      row-key="menuKey"
      :columns="columns"
      :datasource="datasource"
      :lazy="true"
      :show-overflow-tooltip="true"
      :load="tableLoad"
      :pagination="{ pageSize: 5, pageSizes: [5, 10, 20] }"
      :export-config="{ fileName: '菜单数据', datasource: exportSource }"
      :print-config="{ datasource: exportSource }"
      @done="handleDone"
    >
      <template #action="{ row }">
        <el-link
          type="primary"
          underline="never"
          @click="reloadChild(row, $event)"
        >
          刷新我的子级
        </el-link>
        <el-divider v-if="row.parentId" direction="vertical" />
        <el-link
          v-if="row.parentId"
          type="primary"
          underline="never"
          @click="reloadParent(row)"
        >
          刷新我父级的子级
        </el-link>
      </template>
    </ele-pro-table>
  </div>
</template>

<script lang="ts" setup>
  import { ref, nextTick } from 'vue';
  import { EleMessage, toTree } from 'ele-admin-plus';
  import dayjs from 'dayjs';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns,
    DataItem,
    DoneFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { pageMenus, listMenus } from '@/api/system/menu';

  /** 表格实例 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

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
      prop: 'updateTime',
      label: '更新时间',
      width: 220,
      align: 'center'
    },
    {
      width: 280,
      columnKey: 'action',
      label: '操作',
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = async ({ pages, where, parent }) => {
    const now = Date.now();
    if (parent == null) {
      const res = await pageMenus({ ...where, ...pages, parentId: 0 });
      return {
        count: res?.count,
        list: res?.list?.map?.((d) => {
          return {
            ...d,
            updateTime: dayjs(now).format('YYYY-MM-DD HH:mm:ss.SSS'),
            menuKey: `${d.menuId}-${now}`
          };
        })
      };
    }
    const data = await listMenus({ ...where, parentId: parent.menuId });
    parent._oldChildrenLength = parent.children?.length || 0;
    return data.map((d) => {
      return {
        ...d,
        updateTime: dayjs(now).format('YYYY-MM-DD HH:mm:ss.SSS'),
        menuKey: `${d.menuId}-${now}`,
        _parentTableResolve: parent._tableResolve,
        parent
      };
    });
  };

  /** 表格数据加载完成事件 */
  const handleDone: DoneFunction<DataItem> = ({ response }, parent) => {
    // 解决懒加载下子级无法清空
    if (parent && !response.length && parent._oldChildrenLength) {
      nextTick(() => {
        //console.log(parent);
        parent.hasChildren = false;
        parent.menuKey = `${parent.menuId}-${Date.now()}`;
      });
    }
  };

  /** 重写树表格懒加载方法 */
  const tableLoad = (row: any, _treeNode: any, resolve: any) => {
    row._tableResolve = resolve;
    tableRef.value?.reload?.(void 0, row, resolve);
  };

  /** 刷新节点的子级数据 */
  const reloadChild = (row: any, e: MouseEvent) => {
    EleMessage.success({
      message: '已刷新, 可查看控制台发出的请求',
      plain: true
    });
    if (row._tableResolve) {
      tableRef.value?.reload?.(void 0, row, row._tableResolve);
      return;
    }
    const target = e.currentTarget as HTMLElement;
    const $tr = target?.parentElement?.parentElement?.parentElement;
    const $icon = $tr?.querySelector?.('.el-table__expand-icon') as any;
    $icon && $icon.click();
  };

  /** 刷新父级节点的子级数据 */
  const reloadParent = (row: any) => {
    EleMessage.success({
      message: '已刷新, 可查看控制台发出的请求',
      plain: true
    });
    if (row._parentTableResolve) {
      tableRef.value?.reload?.(void 0, row.parent, row._parentTableResolve);
    }
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
