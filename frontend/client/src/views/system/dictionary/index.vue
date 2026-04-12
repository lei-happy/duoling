<template>
  <ele-page flex-table="auto" hide-footer :multi-card="false">
    <ele-card flex-table="auto" :body-style="{ padding: 0 }">
      <ele-split-panel
        flex-table="auto"
        :space="0"
        :size="258"
        allow-collapse
        :collapse-btn-offset="2"
        v-model:collapse="collapse"
        :custom-style="{ borderWidth: '0 1px 0 0' }"
      >
        <template #sideHeader>
          <el-input
            class="ele-fluid"
            clearable
            :maxlength="20"
            v-model="keywords"
            placeholder="输入字典名称搜索"
            :prefix-icon="SearchOutlined"
          />
        </template>
        <ele-loading
          :loading="loading"
          :style="{ flex: '1 1 60px', padding: '12px 0', overflow: 'auto' }"
        >
          <el-tree
            ref="treeRef"
            :data="data"
            highlight-current
            node-key="dictId"
            :props="{ label: 'dictName' }"
            :expand-on-click-node="false"
            :default-expand-all="true"
            :filter-node-method="filterNode"
            :current-node-key="current?.dictId"
            :style="{
              '--ele-tree-item-height': '34px',
              padding: '0 calc(var(--ele-tree-item-radius) * 3)'
            }"
            @node-click="handleNodeClick"
          >
            <template #default="{ node }">
              <div
                class="el-tree-node__label"
                :title="node.label"
                style="overflow: visible"
              >
                <el-icon
                  :style="{
                    margin:
                      '0 4px 0 calc(-10px - var(--ele-tree-item-radius) / 2)',
                    verticalAlign: '-2px'
                  }"
                >
                  <BookOutlined />
                </el-icon>
                <span>{{ node.label }}</span>
              </div>
            </template>
          </el-tree>
        </ele-loading>
        <template #bodyHeader>
          <dict-data-search
            :dictId="current?.dictId"
            @search="(where) => reload(where, 1)"
          />
        </template>
        <template #body>
          <ele-pro-table
            ref="tableRef"
            row-key="dictDataId"
            :columns="columns"
            :datasource="datasource"
            :show-overflow-tooltip="true"
            :highlight-current-row="true"
            :export-config="{ fileName: '字典数据', datasource: exportSource }"
            :print-config="{ datasource: exportSource }"
            :load-on-created="false"
            cache-key="SystemDictionaryTable"
          >
            <template #toolbar>
              <btn-items
                :items="[
                  {
                    preset: 'add',
                    onClick: () => openEdit(),
                    props: { disabled: !current }
                  }
                ]"
              />
            </template>
            <template #action="{ row }">
              <btn-items
                divider
                type="link"
                :items="[
                  { preset: 'edit', onClick: () => openEdit(row) },
                  { preset: 'del', onClick: () => remove(row) }
                ]"
              />
            </template>
          </ele-pro-table>
        </template>
      </ele-split-panel>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import type { ElTree } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { SearchOutlined, BookOutlined } from '@/components/icons';
  import { useMobile } from '@/utils/use-mobile';
  import DictDataSearch from './components/dict-data-search.vue';
  import { listDictionaries } from '@/api/system/dictionary';
  import type { Dictionary } from '@/api/system/dictionary/model';
  import {
    pageDictionaryData,
    removeDictionaryData,
    listDictionaryData
  } from '@/api/system/dictionary-data';
  import type {
    DictionaryData,
    DictionaryDataParam
  } from '@/api/system/dictionary-data/model';

  defineOptions({ name: 'SystemDictionary' });

  const { openModal } = useModal();
  const { mobile } = useMobile();

  /** 分割面板是否折叠 */
  const collapse = ref(mobile.value);

  /** 树组件 */
  const treeRef = ref<InstanceType<typeof ElTree> | null>(null);

  /** 加载状态 */
  const loading = ref(true);

  /** 树数据 */
  const data = ref<Dictionary[]>([]);

  /** 树选中数据 */
  const current = ref<Dictionary | null>(null);

  /** 树搜索关键字 */
  const keywords = ref('');

  /** 查询 */
  const query = () => {
    loading.value = true;
    listDictionaries()
      .then((list) => {
        loading.value = false;
        data.value = list ?? [];
        handleNodeClick(data.value[0]);
      })
      .catch((e) => {
        loading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  /** 选择数据 */
  const handleNodeClick = (row?: Dictionary) => {
    if (row && row.dictId) {
      current.value = row;
    } else {
      current.value = null;
    }
    reload({}, 1);
    if (current.value != null && mobile.value) {
      collapse.value = true;
    }
  };

  /** 树过滤方法 */
  const filterNode = (value: string, data: Dictionary) => {
    if (value) {
      return !!(data.dictName && data.dictName.includes(value));
    }
    return true;
  };

  /** 树过滤 */
  watch(keywords, (value) => {
    treeRef.value?.filter?.(value);
  });

  /** 表格组件 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      prop: 'dictDataName',
      label: '字典数据名',
      sortable: 'custom',
      minWidth: 120
    },
    {
      prop: 'dictDataCode',
      label: '字典数据值',
      sortable: 'custom',
      minWidth: 120
    },
    {
      prop: 'sortNumber',
      label: '排序号',
      sortable: 'custom',
      width: 100,
      align: 'center'
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
      width: 156,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    return pageDictionaryData({
      ...where,
      ...orders,
      ...pages,
      dictId: current.value?.dictId
    });
  };

  /** 刷新表格 */
  const reload = (where?: DictionaryDataParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  /** 打开编辑弹窗 */
  const openEdit = (row?: DictionaryData) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/dict-data-edit.vue'),
      componentProps: {
        data: row,
        dictId: current.value?.dictId,
        dictCode: current.value?.dictCode,
        onDone: () => reload()
      }
    });
  };

  /** 删除（单行） */
  const remove = (row: DictionaryData) => {
    if (row.dictDataId == null) {
      return;
    }
    ElMessageBox.confirm(
      `确定要删除"${row.dictDataName}"吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeDictionaryData(row.dictDataId)
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
    return listDictionaryData({
      ...where,
      ...orders,
      dictId: current.value?.dictId
    });
  };

  /** 查询树数据 */
  query();
</script>
<style scoped>
.ele-card-body {
  :deep(.ele-card-body) {
    padding: 8px 0 8px 0 !important;
  }
}
</style>
