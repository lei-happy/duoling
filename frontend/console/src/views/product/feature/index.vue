<template>
  <ele-page>
    <feature-search @search="reload" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        v-model:selections="selections"
        :highlight-current-row="true"
        :pagination="false"
        cache-key="ProductFeatureTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '添加功能', onClick: () => openEdit() },
              { preset: 'del', onClick: () => remove() }
            ]"
          />
        </template>
        <template #module="{ row }">
          <dict-data
            v-if="row.module"
            code="product_module"
            type="tag"
            v-model="row.module"
          />
          <span v-else style="color: var(--el-text-color-placeholder)">-</span>
        </template>
        <template #requiredTables="{ row }">
          <template v-if="row.requiredTables?.length">
            <el-tag
              v-for="t in row.requiredTables"
              :key="t"
              size="small"
              type="info"
              :disable-transitions="true"
              style="margin-right: 4px; margin-bottom: 2px"
            >
              {{ t }}
            </el-tag>
          </template>
          <span v-else style="color: var(--el-text-color-placeholder)">-</span>
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
  import FeatureSearch from './components/feature-search.vue';
  import { listFeatures, removeFeature } from '@/api/product';
  import type { ProductFeature } from '@/api/product/model';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'ProductFeature' });

  const { openModal } = useModal();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const columns = ref<Columns>([
    { prop: 'featureName', label: '功能名称', minWidth: 140 },
    { prop: 'featureCode', label: '功能编码', width: 180 },
    {
      prop: 'module',
      label: '所属模块',
      width: 120,
      align: 'center',
      slot: 'module'
    },
    { prop: 'description', label: '描述', minWidth: 180 },
    {
      prop: 'requiredTables',
      label: '关联数据表',
      minWidth: 180,
      slot: 'requiredTables'
    },
    { prop: 'sortOrder', label: '排序', width: 80, align: 'center' },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status',
      formatter: (row: ProductFeature) =>
        row.status === 1 ? '正常' : '停用'
    },
    {
      prop: 'createdAt',
      label: '创建时间',
      width: 170,
      align: 'center',
      formatter: (row: ProductFeature) => formatDateTime(row.createdAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      fixed: 'right',
      width: 160,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const selections = ref<ProductFeature[]>([]);

  const datasource: DatasourceFunction = async ({ where }) => {
    const list = await listFeatures({ ...where });
    return list;
  };

  const reload = (where?: Record<string, any>) => {
    selections.value = [];
    tableRef.value?.reload?.({ where });
  };

  const openEdit = (row?: ProductFeature) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/feature-edit.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };

  const remove = (row?: ProductFeature) => {
    const rows = row == null ? selections.value : [row];
    if (!rows.length) {
      EleMessage.error({ message: '请至少选择一条数据', plain: true });
      return;
    }
    ElMessageBox.confirm(
      `确定要删除"${rows.map((d) => d.featureName).join(', ')}"吗？`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        Promise.all(rows.map((r) => removeFeature(r.id!)))
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
