<template>
  <ele-page>
    <changelog-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        v-model:selections="selections"
        :highlight-current-row="true"
        cache-key="ChangelogTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '添加更新记录', onClick: () => openEdit() },
              { preset: 'del', onClick: () => remove() }
            ]"
          />
        </template>
        <template #popup="{ row }">
          <el-tag
            :type="row.is_popup === 1 ? 'warning' : 'info'"
            size="small"
            :disable-transitions="true"
          >
            {{ row.is_popup === 1 ? '弹框' : '否' }}
          </el-tag>
        </template>
        <template #status="{ row }">
          <el-tag
            :type="row.status === 1 ? 'success' : 'info'"
            size="small"
            :disable-transitions="true"
          >
            {{ row.status === 1 ? '已发布' : '停用' }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items
            :divider="true"
            type="link"
            :items="[
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
  import { EleMessage, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import ChangelogSearch from './components/changelog-search.vue';
  import { pageChangelogs, removeChangelog } from '@/api/changelog';
  import type { Changelog, ChangelogParam } from '@/api/changelog/model';

  defineOptions({ name: 'ProductChangelog' });

  const { openModal } = useModal();

  /** 表格实例 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 表格列配置 */
  const columns = ref<Columns>([
    { type: 'selection', columnKey: 'selection', width: 50, align: 'center' },
    { type: 'index', columnKey: 'index', width: 50, align: 'center' },
    { prop: 'version', label: '版本号', width: 110 },
    { prop: 'title', label: '更新标题', minWidth: 180 },
    { prop: 'release_date', label: '发布日期', width: 120, align: 'center' },
    { prop: 'sort_order', label: '排序', width: 80, align: 'center' },
    { prop: 'is_popup', label: '弹框提醒', width: 90, align: 'center', slot: 'popup' },
    { prop: 'status', label: '状态', width: 90, align: 'center', slot: 'status' },
    { prop: 'created_at', label: '创建时间', width: 170, align: 'center' },
    {
      columnKey: 'action',
      label: '操作',
      width: 140,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  /** 表格选中数据 */
  const selections = ref<Changelog[]>([]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    return pageChangelogs({
      ...where,
      ...orders,
      page: pages?.page,
      limit: pages?.limit,
      status: where?.status
    });
  };

  /** 刷新表格 */
  const reload = (where?: ChangelogParam, page?: number) => {
    selections.value = [];
    tableRef.value?.reload?.({ where, page });
  };

  /** 打开编辑弹窗 */
  const openEdit = (row?: Changelog) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/changelog-edit.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };

  /** 删除 */
  const remove = (row?: Changelog) => {
    const rows = row == null ? selections.value : [row];
    if (!rows.length) {
      EleMessage.error({ message: '请至少选择一条数据', plain: true });
      return;
    }
    ElMessageBox.confirm(
      `确定要删除选中的 ${rows.length} 条更新记录吗？`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({ message: '请求中..', plain: true });
        Promise.all(rows.map((r) => removeChangelog(r.id!)))
          .then(() => {
            loading.close();
            EleMessage.success({ message: '删除成功', plain: true });
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
