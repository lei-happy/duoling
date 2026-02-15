<template>
  <ele-page>
    <menu-search @search="reload" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        sticky
        ref="tableRef"
        row-key="menuId"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :export-config="{ fileName: '菜单数据' }"
        :default-expand-all="false"
        :pagination="false"
        cache-key="SystemMenuTable"
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
  import MenuIcon from '@/components/IconSelect/components/menu-icon.vue';
  import MenuSearch from './components/menu-search.vue';
  import { listMenus, removeMenu } from '@/api/system/menu';
  import type { Menu, MenuParam } from '@/api/system/menu/model';

  defineOptions({ name: 'SystemMenu' });

  const { openModal } = useModal();

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
      slot: 'title',
      minWidth: 160
    },
    {
      prop: 'path',
      label: '路由地址',
      minWidth: 160
    },
    {
      prop: 'sortNumber',
      label: '排序',
      width: 100,
      align: 'center'
    },
    {
      prop: 'hide',
      label: '可见',
      width: 100,
      align: 'center',
      formatter: (row) => ['是', '否'][row.hide]
    },
    {
      prop: 'menuType',
      label: '类型',
      width: 100,
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

  /** 表格数据源 */
  const datasource: DatasourceFunction = async ({ where }) => {
    const data = await listMenus({ ...where });
    return toTree({
      data,
      idField: 'menuId',
      parentIdField: 'parentId'
    });
  };

  /** 刷新表格 */
  const reload = (where?: MenuParam) => {
    tableRef.value?.reload?.({ where });
  };

  /** 打开编辑弹窗 */
  const openEdit = (row?: Menu | null, id?: number) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/menu-edit.vue'),
      componentProps: { data: row, parentId: id, onDone: () => reload() }
    });
  };

  /** 删除单个 */
  const remove = (row: Menu) => {
    if (row.children?.length) {
      EleMessage.error({ message: '请先删除子节点', plain: true });
      return;
    }
    ElMessageBox.confirm(`确定要删除“${row.title}”吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeMenu(row.menuId)
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

  /** 展开全部 */
  const handleExpandAll = () => {
    tableRef.value?.toggleRowExpansionAll?.(true);
  };

  /** 折叠全部 */
  const handleFoldAll = () => {
    tableRef.value?.toggleRowExpansionAll?.(false);
  };

  /** 判断是否是目录 */
  const isDirectory = (d: Menu) => {
    return !!d.children?.length && !d.component;
  };
</script>
