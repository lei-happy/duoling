<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        v-model:selections="selections"
        :highlight-current-row="true"
        cache-key="ProductVersionTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '添加版本', onClick: () => openEdit() },
              { preset: 'del', onClick: () => remove() }
            ]"
          />
        </template>
        <template #status="{ row }">
          <el-tag
            :type="row.status === 1 ? 'success' : 'info'"
            size="small"
            :disable-transitions="true"
          >
            {{ row.status === 1 ? '正常' : '停用' }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items
            :divider="true"
            type="link"
            :items="[
              { preset: 'edit', onClick: () => openEdit(row) },
              { title: '配置功能', onClick: () => openFeatureAssign(row) },
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
  import { listVersions, removeVersion } from '@/api/product';
  import type { ProductVersion } from '@/api/product/model';

  defineOptions({ name: 'ProductVersion' });

  const { openModal } = useModal();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const columns = ref<Columns>([
    { type: 'selection', columnKey: 'selection', width: 50, align: 'center' },
    { type: 'index', columnKey: 'index', width: 50, align: 'center' },
    { prop: 'versionCode', label: '版本编码', width: 120 },
    { prop: 'versionName', label: '版本名称', minWidth: 140 },
    { prop: 'description', label: '描述', minWidth: 180 },
    { prop: 'maxUsers', label: '最大用户数', width: 110, align: 'center' },
    { prop: 'maxVehicles', label: '最大车辆数', width: 110, align: 'center' },
    { prop: 'price', label: '价格', width: 100, align: 'center' },
    { prop: 'sortOrder', label: '排序', width: 80, align: 'center' },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status',
      formatter: (row: ProductVersion) =>
        row.status === 1 ? '正常' : '停用'
    },
    { prop: 'createdAt', label: '创建时间', width: 170, align: 'center' },
    {
      columnKey: 'action',
      label: '操作',
      width: 200,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const selections = ref<ProductVersion[]>([]);

  const datasource: DatasourceFunction = ({ pages }) => {
    return listVersions({
      page: pages?.page,
      page_size: pages?.limit
    });
  };

  const reload = (page?: number) => {
    selections.value = [];
    tableRef.value?.reload?.({ page });
  };

  const openEdit = (row?: ProductVersion) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/version-edit.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };

  const openFeatureAssign = (row: ProductVersion) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/feature-assign.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };

  const remove = (row?: ProductVersion) => {
    const rows = row == null ? selections.value : [row];
    if (!rows.length) {
      EleMessage.error({ message: '请至少选择一条数据', plain: true });
      return;
    }
    ElMessageBox.confirm(
      `确定要删除"${rows.map((d) => d.versionName).join(', ')}"吗？`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        Promise.all(rows.map((r) => removeVersion(r.id!)))
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
