<template>
  <ele-page>
    <client-menu-search @search="reload" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        sticky
        ref="tableRef"
        row-key="menuId"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :tools="proTableToolsWithExport"
        :export-config="{ fileName: '客户端菜单数据' }"
        :default-expand-all="false"
        :pagination="false"
        cache-key="SystemClientMenuTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', onClick: () => openEdit() },
              { preset: 'expand', onClick: () => handleExpandAll() },
              { preset: 'fold', onClick: () => handleFoldAll() }
            ]"
          />
        </template>
        <template #title="{ row }">
          <menu-icon
            v-if="row.icon"
            :icon="row.icon"
            :component-props="{ size: 15 }"
            :component-style="{ marginRight: '4px', verticalAlign: '-2px' }"
            :img-style="{ marginRight: '2px', verticalAlign: '-5px' }"
          />
          <span>{{ row.title }}</span>
        </template>
        <template #menuType="{ row }">
          <el-tag
            v-if="isExternalLink(row.path)"
            size="small"
            type="danger"
            :disable-transitions="true"
          >
            外链
          </el-tag>
          <el-tag
            v-else-if="isExternalLink(row.component)"
            size="small"
            type="warning"
            :disable-transitions="true"
          >
            内嵌
          </el-tag>
          <el-tag
            v-else-if="isDirectory(row)"
            size="small"
            :disable-transitions="true"
          >
            目录
          </el-tag>
          <el-tag
            v-else-if="row.menuType === 0"
            size="small"
            type="success"
            :disable-transitions="true"
          >
            菜单
          </el-tag>
          <el-tag
            v-else-if="row.menuType === 1"
            size="small"
            type="info"
            :disable-transitions="true"
          >
            按钮
          </el-tag>
        </template>
        <template #featureCode="{ row }">
          <el-tag
            v-if="row.featureCode"
            size="small"
            type="warning"
            :disable-transitions="true"
          >
            {{ row.featureCode }}
          </el-tag>
          <span v-else style="color: var(--el-text-color-placeholder)">-</span>
        </template>
        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :items="[
              { preset: 'add', onClick: () => openEdit(null, row.menuId) },
              { preset: 'edit', onClick: () => openEdit(row) },
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
  import { EleMessage, useModal, isExternalLink, toTree } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { proTableToolsWithExport } from '@/config/pro-table-tool-presets';
  import MenuIcon from '@/components/IconSelect/components/menu-icon.vue';
  import ClientMenuSearch from './components/client-menu-search.vue';
  import {
    listClientMenus,
    removeClientMenu
  } from '@/api/system/client-menu';
  import type {
    ClientMenu,
    ClientMenuParam
  } from '@/api/system/client-menu/model';

  defineOptions({ name: 'SystemClientMenu' });

  const { openModal } = useModal();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

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
      slot: 'title',
      minWidth: 180
    },
    {
      prop: 'path',
      label: '路由地址',
      minWidth: 160
    },
    {
      prop: 'component',
      label: '组件路径',
      minWidth: 160
    },
    {
      prop: 'featureCode',
      label: '功能编码',
      width: 160,
      align: 'center',
      slot: 'featureCode'
    },
    {
      prop: 'sortNumber',
      label: '排序',
      width: 80,
      align: 'center'
    },
    {
      prop: 'menuType',
      label: '类型',
      width: 80,
      align: 'center',
      slot: 'menuType',
      formatter: (row) =>
        ['菜单', '按钮', '外链', '内嵌', '目录'][
          isExternalLink(row.path)
            ? 2
            : isExternalLink(row.component)
              ? 3
              : isDirectory(row)
                ? 4
                : row.menuType
        ]
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 220,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const datasource: DatasourceFunction = async ({ where }) => {
    const data = await listClientMenus({ ...where });
    return toTree({
      data,
      idField: 'menuId',
      parentIdField: 'parentId'
    });
  };

  const reload = (where?: ClientMenuParam) => {
    tableRef.value?.reload?.({ where });
  };

  const openEdit = (row?: ClientMenu | null, id?: number) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/client-menu-edit.vue'),
      componentProps: { data: row, parentId: id, onDone: () => reload() }
    });
  };

  const remove = (row: ClientMenu) => {
    if (row.children?.length) {
      EleMessage.error({ message: '请先删除子节点', plain: true });
      return;
    }
    ElMessageBox.confirm(`确定要删除"${row.title}"吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeClientMenu(row.menuId)
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

  const handleExpandAll = () => {
    tableRef.value?.toggleRowExpansionAll?.(true);
  };

  const handleFoldAll = () => {
    tableRef.value?.toggleRowExpansionAll?.(false);
  };

  const isDirectory = (d: ClientMenu) => {
    return !!d.children?.length && !d.component;
  };
</script>
