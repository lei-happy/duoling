<template>
  <ele-page>
    <feature-search @search="onSearch" />
    <ele-card :body-style="{ paddingTop: '0px' }">
      <el-tabs
        v-model="activeModule"
        type="card"
        @tab-change="onTabChange"
        class="feature-module-tabs"
      >
        <el-tab-pane label="全部" name="" />
        <el-tab-pane
          v-for="item in moduleDicts"
          :key="item.dictDataCode"
          :label="item.dictDataName"
          :name="item.dictDataCode"
        />
      </el-tabs>
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        v-model:selections="selections"
        :highlight-current-row="true"
        cache-key="ProductFeatureTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '添加功能', onClick: () => openEdit() },
              { preset: 'del', onClick: () => remove() },
              { title: '全链路体检', icon: 'success-filled', onClick: () => doHealthCheck() }
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
        <template #assignedVersions="{ row }">
          <template v-if="row.assignedVersions?.length">
            <el-tag
              v-for="v in row.assignedVersions"
              :key="v.id"
              size="small"
              type="success"
              :disable-transitions="true"
              style="margin-right: 4px; margin-bottom: 2px"
            >
              {{ v.name }}
            </el-tag>
          </template>
          <el-tag
            v-else
            size="small"
            type="warning"
            :disable-transitions="true"
          >
            未关联
          </el-tag>
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
  import { ElMessageBox, ElNotification } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import FeatureSearch from './components/feature-search.vue';
  import {
    pageFeatures,
    removeFeature,
    checkFeatureHealth
  } from '@/api/product';
  import {
    DICT_CODE_PRODUCT_MODULE,
    type ProductFeature
  } from '@/api/product/model';
  import { useDictData } from '@/utils/use-dict-data';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'ProductFeature' });

  const { openModal } = useModal();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const [moduleDicts] = useDictData([DICT_CODE_PRODUCT_MODULE]);

  const activeModule = ref<string>('');
  const searchWhere = ref<Record<string, any>>({});

  const columns = ref<Columns>([
    { type: 'index', columnKey: 'index', width: 50, align: 'center' },
    { prop: 'featureName', label: '功能名称', minWidth: 140 },
    { prop: 'featureCode', label: '功能编码', width: 200 },
    {
      prop: 'module',
      label: '所属模块',
      width: 120,
      align: 'center',
      slot: 'module'
    },
    { prop: 'description', label: '描述', minWidth: 160 },
    {
      prop: 'requiredTables',
      label: '关联数据表',
      minWidth: 160,
      slot: 'requiredTables'
    },
    {
      prop: 'assignedVersions',
      label: '关联版本',
      minWidth: 180,
      slot: 'assignedVersions'
    },
    { prop: 'sortOrder', label: '排序', width: 70, align: 'center' },
    {
      prop: 'status',
      label: '状态',
      width: 80,
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
      width: 140,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const selections = ref<ProductFeature[]>([]);

  const datasource: DatasourceFunction = async ({ pages, where }) => {
    const params: Record<string, any> = {
      page: pages?.page ?? 1,
      pageSize: pages?.limit ?? 20,
      ...(where ?? searchWhere.value)
    };
    if (activeModule.value) {
      params.module = activeModule.value;
    } else {
      delete params.module;
    }
    return await pageFeatures(params as any);
  };

  const onSearch = (where?: Record<string, any>) => {
    searchWhere.value = where ?? {};
    selections.value = [];
    tableRef.value?.reload?.({ where: searchWhere.value, page: 1 });
  };

  const onTabChange = () => {
    selections.value = [];
    tableRef.value?.reload?.({ where: searchWhere.value, page: 1 });
  };

  const reload = () => {
    selections.value = [];
    tableRef.value?.reload?.({ where: searchWhere.value });
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

  const doHealthCheck = async () => {
    const loading = EleMessage.loading({ message: '检查中..', plain: true });
    try {
      const r = await checkFeatureHealth();
      loading.close();
      const orphanCount = r.orphanFeatureCodes.length;
      const unboundCount = r.unboundFeatureCodes.length;
      if (orphanCount === 0 && unboundCount === 0) {
        ElNotification.success({
          title: '体检通过',
          message: '所有菜单 feature_code 与功能清单一致，且全部功能已绑定到至少一个版本。',
          duration: 4000
        });
        return;
      }
      const msgs: string[] = [];
      if (orphanCount > 0) {
        msgs.push(
          `脏 feature_code（菜单引用但未在功能清单中定义，共 ${orphanCount} 个）：\n` +
            r.orphanFeatureCodes.join('，')
        );
      }
      if (unboundCount > 0) {
        msgs.push(
          `未绑定版本（功能清单中存在但未关联到任何版本，共 ${unboundCount} 个）：\n` +
            r.unboundFeatureCodes.join('，')
        );
      }
      ElMessageBox.alert(msgs.join('\n\n'), '全链路体检结果', {
        type: orphanCount > 0 ? 'error' : 'warning',
        confirmButtonText: '知道了',
        customStyle: { whiteSpace: 'pre-wrap' }
      }).catch(() => {});
    } catch (e: any) {
      loading.close();
      EleMessage.error({ message: e.message, plain: true });
    }
  };
</script>

<style scoped>
  .feature-module-tabs :deep(.el-tabs__header) {
    margin-bottom: 8px;
  }
</style>
