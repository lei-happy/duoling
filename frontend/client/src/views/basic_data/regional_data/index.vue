<template>
  <ele-page hide-footer :multi-card="false" flex-table="auto">
    <ele-card :body-style="{ padding: 0 }" flex-table="auto">
      <ele-split-panel
        :space="0"
        :size="258"
        allow-collapse
        :collapse-btn-offset="2"
        v-model:collapse="collapse"
        :custom-style="{ borderWidth: '0 1px 0 0' }"
        flex-table="auto"
      >
        <template #sideHeader>
          <el-input
            clearable
            :maxlength="20"
            v-model="keywords"
            placeholder="输入地区名称搜索"
            :prefix-icon="SearchOutlined"
          />
        </template>
        <ele-loading
          :loading="treeLoading"
          :spinner-style="{ background: 'none' }"
          :style="{ flex: '1 1 60px', overflow: 'auto' }"
        >
          <el-tree
            ref="treeRef"
            :data="navTree"
            highlight-current
            node-key="code"
            :props="{ label: 'name', children: 'children' }"
            :expand-on-click-node="false"
            :default-expand-all="false"
            :filter-node-method="filterNode"
            :style="{
              '--ele-tree-item-height': '34px',
              '--ele-tree-expand-margin':
                '0 2px 0 calc(8px - var(--ele-tree-item-radius))',
              padding: '12px calc(var(--ele-tree-item-radius) * 3)'
            }"
            @node-click="handleNodeClick"
          >
            <template #default="{ node, data }">
              <span
                class="el-tree-node__label"
                :title="`${node.label} (${data.childCount ?? 0})`"
              >
                <el-icon style="margin-right: 4px; vertical-align: -2px">
                  <EnvironmentOutlined />
                </el-icon>
                <span>{{ node.label }}</span>
                <span style="color: #999; font-size: 12px">
                  &nbsp;({{ data.childCount ?? 0 }})
                </span>
              </span>
            </template>
          </el-tree>
        </ele-loading>

        <template #bodyHeader>
          <region-search
            :parent-code="currentNode?.code"
            @search="(where) => reload(where)"
          />
        </template>
        <template #body>
          <ele-pro-table
            ref="tableRef"
            row-key="regionId"
            :columns="columns"
            :datasource="datasource"
            :show-overflow-tooltip="true"
            :highlight-current-row="true"
            :load-on-created="false"
            cache-key="BasicDataRegionTable"
          >
            <template #toolbar>
              <btn-items
                :items="[
                  {
                    preset: 'add',
                    vIf: () => canAdd,
                    onClick: () => openEdit()
                  }
                ]"
              />
            </template>
            <template #source="{ row }">
              <el-tag v-if="row.source === 0" type="primary" size="small">
                系统
              </el-tag>
              <el-tag v-else type="success" size="small">自定义</el-tag>
            </template>
            <template #status="{ row }">
              <el-tag
                :type="row.status === 1 ? 'success' : 'danger'"
                size="small"
              >
                {{ row.status === 1 ? '正常' : '停用' }}
              </el-tag>
            </template>
            <template #action="{ row }">
              <btn-items
                v-if="row.source === 1"
                divider
                type="link"
                :items="[
                  { preset: 'edit', onClick: () => openEdit(row) },
                  { preset: 'del', onClick: () => remove(row) }
                ]"
              />
              <span v-else style="color: #999; font-size: 12px">系统内置</span>
            </template>
          </ele-pro-table>
        </template>
      </ele-split-panel>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, computed, watch, nextTick } from 'vue';
  import type { ElTree } from 'element-plus';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { SearchOutlined, EnvironmentOutlined } from '@/components/icons';
  import RegionSearch from './components/region-search.vue';
  import {
    getRegionNavTree,
    pageRegionChildren,
    removeRegion
  } from '@/api/basic-data/region';
  import type { Region, RegionNavNode } from '@/api/basic-data/region/model';

  defineOptions({ name: 'BasicDataRegion' });

  const { openModal } = useModal();

  const collapse = ref(false);
  const treeRef = ref<InstanceType<typeof ElTree> | null>(null);
  const treeLoading = ref(true);
  const navTree = ref<RegionNavNode[]>([]);
  const currentNode = ref<RegionNavNode | null>(null);
  const keywords = ref('');

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 只允许在市级（level>=2）节点下添加 */
  const canAdd = computed(
    () => currentNode.value != null && currentNode.value.level >= 2
  );

  const columns = ref<Columns>([
    {
      prop: 'name',
      label: '地区名称',
      minWidth: 160
    },
    {
      prop: 'code',
      label: '地区代码',
      width: 140,
      align: 'center'
    },
    {
      prop: 'level',
      label: '层级',
      width: 90,
      align: 'center',
      formatter: (row: Region) => {
        const map: Record<number, string> = { 1: '省', 2: '市', 3: '区/县' };
        return map[row.level || 0] || `${row.level}级`;
      }
    },
    {
      prop: 'longitude',
      label: '经度',
      width: 110,
      align: 'center',
      formatter: (row: Region) => row.longitude != null ? String(row.longitude) : '—'
    },
    {
      prop: 'latitude',
      label: '纬度',
      width: 110,
      align: 'center',
      formatter: (row: Region) => row.latitude != null ? String(row.latitude) : '—'
    },
    {
      columnKey: 'source',
      prop: 'source',
      label: '来源',
      width: 100,
      align: 'center',
      slot: 'source'
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status',
      formatter: (row: Region) => (row.status === 1 ? '正常' : '停用')
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 148,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  /** 表格数据源 — 服务端分页 */
  const datasource: DatasourceFunction = ({ pages, where }) => {
    if (!currentNode.value) {
      return Promise.resolve({ list: [], count: 0 });
    }
    return pageRegionChildren({
      parentCode: currentNode.value.code,
      ...pages,
      name: where?.name || undefined,
      source: where?.source
    });
  };

  /** 搜索 / 刷新 */
  const reload = (where?: Record<string, any>, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  /** 在导航树中按 code 查找节点（省/市两级） */
  const findNodeByCode = (
    nodes: RegionNavNode[],
    code: string
  ): RegionNavNode | null => {
    for (const n of nodes) {
      if (n.code === code) {
        return n;
      }
      if (n.children?.length) {
        const hit = findNodeByCode(n.children, code);
        if (hit) {
          return hit;
        }
      }
    }
    return null;
  };

  /**
   * 左侧树：加载
   * @param preserveCode 刷新后仍选中该节点（新增/删除子级后保持当前市/省），不传则首次选中第一个省
   */
  const queryNavTree = (preserveCode?: string | null) => {
    treeLoading.value = true;
    getRegionNavTree()
      .then((data) => {
        treeLoading.value = false;
        navTree.value = data ?? [];
        if (navTree.value.length === 0) {
          return;
        }
        let target: RegionNavNode | null = null;
        if (preserveCode) {
          target = findNodeByCode(navTree.value, preserveCode);
        }
        if (!target) {
          target = navTree.value[0];
        }
        handleNodeClick(target);
        nextTick(() => {
          treeRef.value?.setCurrentKey?.(target!.code);
        });
      })
      .catch((e) => {
        treeLoading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  /** 左侧树：点击节点 */
  const handleNodeClick = (data: RegionNavNode) => {
    currentNode.value = data;
    reload({}, 1);
  };

  /** 左侧树：过滤 */
  const filterNode = (value: string, data: RegionNavNode) => {
    if (value) {
      return !!(data.name && data.name.includes(value));
    }
    return true;
  };

  watch(keywords, (value) => {
    treeRef.value?.filter?.(value);
  });

  /** 打开编辑弹窗 */
  const openEdit = (row?: Region) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/region-edit.vue'),
      componentProps: {
        data: row,
        parentCode: currentNode.value?.code,
        parentName: currentNode.value?.name,
        onDone: () => {
          const parentCode = currentNode.value?.code;
          queryNavTree(parentCode);
        }
      }
    });
  };

  /** 删除 */
  const remove = (row: Region) => {
    ElMessageBox.confirm(
      `确定要删除"${row.name}"吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeRegion(row.regionId!)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            queryNavTree(currentNode.value?.code);
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  queryNavTree();
</script>
<style scoped>
.ele-card-body {
  :deep(.ele-card-body) {
    padding: 8px 0 8px 0 !important;
  }
}
</style>