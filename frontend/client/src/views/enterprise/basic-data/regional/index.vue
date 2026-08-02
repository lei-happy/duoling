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
            class="ele-fluid"
            clearable
            :maxlength="20"
            v-model="keywords"
            placeholder="输入名称或拼音搜索"
            :prefix-icon="SearchOutlined"
          />
        </template>
        <ele-loading
          :loading="treeLoading"
          :spinner-style="{ background: 'none' }"
          :style="{ flex: '1 1 60px', overflow: 'auto' }"
        >
          <el-empty
            v-if="searchActive && displayTree.length === 0"
            description="未找到相关地区"
            :image-size="72"
          />
          <el-tree
            v-else
            :key="treeRenderKey"
            ref="treeRef"
            :data="searchActive ? displayTree : []"
            highlight-current
            node-key="code"
            :lazy="!searchActive"
            :load="loadTreeNode"
            :props="{ label: 'name', children: 'children', isLeaf: 'leaf' }"
            :expand-on-click-node="false"
            :default-expand-all="searchActive"
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
            :pagination="{ pageSize: 20 }"
            :show-overflow-tooltip="true"
            :highlight-current-row="true"
            :load-on-created="false"
            cache-key="BasicDataRegionTable"
          >
            <template #toolbar>
              <div class="region-toolbar">
                <btn-items
                  :items="[
                    {
                      preset: 'add',
                      vIf: () => canAdd,
                      onClick: () => openEdit()
                    }
                  ]"
                />
                <span
                  v-if="currentPath"
                  class="region-current-path"
                  :title="currentPath"
                >
                  {{ currentPath }}
                </span>
              </div>
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
  import type Node from 'element-plus/es/components/tree/src/model/node';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { debounce } from 'lodash-es';
  import { SearchOutlined, EnvironmentOutlined } from '@/components/icons';
  import { pinyinMatch, warmPinyinCache } from '@/utils/pinyin-match';
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
  /** 完整三级树（仅内存索引，不直接绑到 el-tree） */
  const navTreeAll = ref<RegionNavNode[]>([]);
  /** 实际渲染的树：浏览态省/市，检索态为命中分支（可含区县） */
  const displayTree = ref<RegionNavNode[]>([]);
  const searchActive = ref(false);
  const treeRenderKey = ref(0);
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
      minWidth: 140,
      align: 'center'
    },
    {
      prop: 'level',
      label: '层级',
      minWidth: 90,
      align: 'center',
      formatter: (row: Region) => {
        const map: Record<number, string> = { 1: '省', 2: '市', 3: '区/县' };
        return map[row.level || 0] || `${row.level}级`;
      }
    },
    {
      prop: 'longitude',
      label: '经度',
      minWidth: 110,
      align: 'center',
      formatter: (row: Region) =>
        row.longitude != null ? String(row.longitude) : '—'
    },
    {
      prop: 'latitude',
      label: '纬度',
      minWidth: 110,
      align: 'center',
      formatter: (row: Region) =>
        row.latitude != null ? String(row.latitude) : '—'
    },
    {
      columnKey: 'source',
      prop: 'source',
      label: '来源',
      minWidth: 100,
      align: 'center',
      slot: 'source'
    },
    {
      prop: 'status',
      label: '状态',
      minWidth: 90,
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

  /** 在完整导航树中按 code 查找节点 */
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

  /** 收集导航树全部名称，用于预热拼音缓存 */
  const collectNavNames = (nodes: RegionNavNode[], out: string[] = []) => {
    for (const n of nodes) {
      if (n.name) out.push(n.name);
      if (n.children?.length) collectNavNames(n.children, out);
    }
    return out;
  };

  /** 树节点视图（补充 leaf，供 el-tree 懒加载判断） */
  type NavViewNode = RegionNavNode & { leaf?: boolean };

  /**
   * 检索态：在完整三级树上做拼音匹配，只保留命中节点及其祖先路径。
   * 渲染节点极少，因此可流畅支持区县拼音。
   */
  const filterNavTree = (
    nodes: RegionNavNode[],
    keyword: string
  ): NavViewNode[] => {
    const result: NavViewNode[] = [];
    for (const n of nodes) {
      const children = n.children?.length
        ? filterNavTree(n.children, keyword)
        : [];
      if (pinyinMatch(n.name ?? '', keyword) || children.length) {
        result.push({
          ...n,
          children,
          leaf: children.length === 0
        });
      }
    }
    return result;
  };

  /**
   * 浏览态懒加载：
   * - el-tree lazy 下根节点必须由 load 注入（:data 不会自动建子节点）
   * - 省 → 市 → 区县逐级展开，避免一次挂载全国区县
   */
  const loadTreeNode = (node: Node, resolve: (data: NavViewNode[]) => void) => {
    // 根节点：注入省级列表
    if (node.level === 0) {
      const provinces = navTreeAll.value.map((p) => ({
        ...p,
        leaf: false,
        children: undefined
      }));
      resolve(provinces);
      const keep = currentNode.value?.code;
      if (keep) {
        nextTick(() => treeRef.value?.setCurrentKey?.(keep));
      }
      return;
    }

    const data = node.data as NavViewNode | undefined;
    if (!data?.code) {
      resolve([]);
      return;
    }

    const full = findNodeByCode(navTreeAll.value, data.code);
    const children = full?.children || [];

    if (data.level === 1) {
      // 省 → 市
      resolve(
        children.map((c) => ({
          ...c,
          leaf: (c.childCount ?? 0) <= 0,
          children: undefined
        }))
      );
      return;
    }

    if (data.level === 2) {
      // 市 → 区县
      resolve(
        children.map((d) => ({
          ...d,
          leaf: true,
          children: undefined
        }))
      );
      return;
    }

    resolve([]);
  };

  const syncTreeSelection = (code?: string | null) => {
    if (!code) return;
    nextTick(() => {
      treeRef.value?.setCurrentKey?.(code);
    });
  };

  /** 按关键词切换浏览树 / 检索树 */
  const applyTreeKeywords = (raw: string) => {
    const kw = raw.trim();
    const keepCode = currentNode.value?.code;
    if (!kw) {
      searchActive.value = false;
      displayTree.value = [];
      treeRenderKey.value += 1;
      syncTreeSelection(keepCode);
      return;
    }
    searchActive.value = true;
    displayTree.value = filterNavTree(navTreeAll.value, kw);
    treeRenderKey.value += 1;
    syncTreeSelection(keepCode);
  };

  const applyTreeKeywordsDebounced = debounce(applyTreeKeywords, 200);

  /**
   * 左侧树：加载
   * @param preserveCode 刷新后仍选中该节点（新增/删除子级后保持当前市/省），不传则首次选中第一个省
   */
  const queryNavTree = (preserveCode?: string | null) => {
    treeLoading.value = true;
    getRegionNavTree()
      .then((data) => {
        treeLoading.value = false;
        navTreeAll.value = data ?? [];
        // 加载阶段预热拼音，输入时只做字符串判断
        warmPinyinCache(collectNavNames(navTreeAll.value));
        if (navTreeAll.value.length === 0) {
          displayTree.value = [];
          return;
        }
        applyTreeKeywords(keywords.value);
        let target: RegionNavNode | null = null;
        if (preserveCode) {
          target = findNodeByCode(navTreeAll.value, preserveCode);
        }
        if (!target) {
          target = navTreeAll.value[0];
        }
        handleNodeClick(target);
        syncTreeSelection(target.code);
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

  watch(keywords, (value) => {
    if (!value?.trim()) {
      applyTreeKeywordsDebounced.cancel();
      applyTreeKeywords('');
      return;
    }
    applyTreeKeywordsDebounced(value);
  });

  /** 从完整导航树拼出节点路径，如 内蒙古自治区/鄂尔多斯市/东胜区 */
  const findNavPathNames = (
    nodes: RegionNavNode[],
    code: string,
    trail: string[] = []
  ): string[] | null => {
    for (const node of nodes) {
      const next = [...trail, node.name];
      if (node.code === code) return next;
      if (node.children?.length) {
        const found = findNavPathNames(node.children, code, next);
        if (found) return found;
      }
    }
    return null;
  };

  const getParentPath = (code?: string) => {
    if (!code) return '';
    const names = findNavPathNames(navTreeAll.value, code);
    return names?.join('/') || '';
  };

  /** 当前选中节点完整路径，与添加弹窗「上级地区」同源 */
  const currentPath = computed(() => getParentPath(currentNode.value?.code));

  /** 打开编辑弹窗 */
  const openEdit = (row?: Region) => {
    const parentCode = currentNode.value?.code;
    openModal({
      custom: true,
      asyncComponent: () => import('./components/region-edit.vue'),
      componentProps: {
        data: row,
        parentCode,
        parentName: currentNode.value?.name,
        parentPath: getParentPath(parentCode),
        onDone: () => {
          queryNavTree(currentNode.value?.code);
        }
      }
    });
  };

  /** 删除 */
  const remove = (row: Region) => {
    ElMessageBox.confirm(`确定要删除"${row.name}"吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
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

  .region-toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
  }

  .region-current-path {
    min-width: 0;
    overflow: hidden;
    color: var(--el-text-color-secondary);
    font-size: 13px;
    line-height: 1.4;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
