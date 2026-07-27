<template>
  <div class="doc-center">
    <ele-card class="doc-tree-panel" :body-style="{ padding: 0, height: '100%' }">
      <div class="doc-tree-header">
        <el-input
          v-model="filterText"
          placeholder="搜索文档..."
          :prefix-icon="SearchIcon"
          clearable
          size="default"
        />
      </div>
      <el-scrollbar class="doc-tree-scroll">
        <el-tree
          ref="treeRef"
          :data="treeData"
          :props="treeProps"
          node-key="key"
          :expand-on-click-node="true"
          :filter-node-method="filterNode"
          :default-expanded-keys="expandedKeys"
          highlight-current
          @node-click="handleNodeClick"
        >
          <template #default="{ node, data }">
            <span class="doc-tree-node">
              <el-icon v-if="!data.isLeaf" class="doc-tree-node-icon">
                <FolderOpened v-if="node.expanded" />
                <Folder v-else />
              </el-icon>
              <el-icon v-else class="doc-tree-node-icon">
                <Document />
              </el-icon>
              <span class="doc-tree-node-label">{{ node.label }}</span>
            </span>
          </template>
        </el-tree>
      </el-scrollbar>
    </ele-card>

    <ele-card
      class="doc-content-panel"
      :body-style="{ padding: 0, height: '100%' }"
    >
      <div v-if="currentPath" class="doc-content-breadcrumb">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item>文档中心</el-breadcrumb-item>
          <el-breadcrumb-item v-for="(seg, idx) in breadcrumbs" :key="idx">
            {{ seg }}
          </el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <el-scrollbar class="doc-content-scroll">
        <div v-if="loading" class="doc-content-loading">
          <el-icon class="is-loading" :size="28"><Loading /></el-icon>
          <span>正在加载文档，请稍候…</span>
        </div>
        <div v-else-if="docContent" class="doc-content-body">
          <byte-md-viewer :value="docContent" :config="viewerConfig" />
        </div>
        <div v-else class="doc-content-empty">
          <el-empty description="请从左侧选择一篇文档查看">
            <template #image>
              <el-icon :size="64" color="var(--el-text-color-secondary)">
                <Reading />
              </el-icon>
            </template>
          </el-empty>
        </div>
      </el-scrollbar>
    </ele-card>
  </div>
</template>

<script lang="ts" setup>
  import { ref, watch, computed, onMounted } from 'vue';
  import {
    Search as SearchIcon,
    FolderOpened,
    Folder,
    Document,
    Loading,
    Reading
  } from '@element-plus/icons-vue';
  import type { ElTree } from 'element-plus';
  import ByteMdViewer from '@/components/ByteMdViewer/index.vue';
  import gfm from '@bytemd/plugin-gfm';
  import highlight from '@bytemd/plugin-highlight';
  import mermaid from '@bytemd/plugin-mermaid';
  import 'highlight.js/styles/github-dark.css';
  import 'github-markdown-css/github-markdown-light.css';
  import { getDocTree, getDocContent } from '@/api/doc-center';
  import type { DocTreeNode } from '@/api/doc-center/model';

  defineOptions({ name: 'DocBrowser' });

  const treeRef = ref<InstanceType<typeof ElTree>>();
  const treeData = ref<DocTreeNode[]>([]);
  const filterText = ref('');
  const currentPath = ref('');
  const docContent = ref('');
  const loading = ref(false);
  const expandedKeys = ref<string[]>([]);

  const treeProps = {
    label: 'title',
    children: 'children',
    isLeaf: 'isLeaf'
  };

  const viewerConfig = {
    plugins: [gfm(), highlight(), mermaid()]
  };

  const breadcrumbs = computed(() => {
    if (!currentPath.value) return [];
    return currentPath.value.replace(/\.md$/i, '').split('/');
  });

  const filterNode = (value: string, data: DocTreeNode) => {
    if (!value) return true;
    return data.title.toLowerCase().includes(value.toLowerCase());
  };

  watch(filterText, (val) => {
    treeRef.value?.filter(val);
  });

  const handleNodeClick = async (data: DocTreeNode) => {
    if (!data.isLeaf) return;

    const filePath = data.key.endsWith('.md') ? data.key : `${data.key}.md`;
    if (filePath === currentPath.value) return;

    currentPath.value = filePath;
    loading.value = true;
    docContent.value = '';

    try {
      const res = await getDocContent(filePath);
      if (res) {
        docContent.value = res.content;
      }
    } catch (e) {
      console.error(e);
      docContent.value = '> 文档加载失败，请稍后重试。';
    } finally {
      loading.value = false;
    }
  };

  const loadTree = async () => {
    try {
      const data = await getDocTree();
      treeData.value = data ?? [];
      if (treeData.value.length > 0) {
        expandedKeys.value = treeData.value.map((n) => n.key);
      }
    } catch (e) {
      console.error(e);
    }
  };

  onMounted(() => {
    loadTree();
  });
</script>

<style lang="scss" scoped>
  .doc-center {
    display: flex;
    gap: 16px;
    flex: 1;
    overflow: hidden;
    min-height: 0;
  }

  .doc-tree-panel {
    width: 300px;
    min-width: 260px;
    flex-shrink: 0;

    :deep(.el-card) {
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    :deep(.el-card__body) {
      flex: 1;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
  }

  .doc-tree-header {
    padding: 12px 12px 8px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    flex-shrink: 0;
  }

  .doc-tree-scroll {
    flex: 1;
    overflow: hidden;

    :deep(.el-scrollbar__wrap) {
      overflow-x: hidden;
    }

    :deep(.el-tree) {
      padding: 6px 0;
      --el-tree-node-content-height: 34px;
    }

    :deep(.el-tree-node__content) {
      padding-left: 8px !important;
    }
  }

  .doc-tree-node {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    overflow: hidden;
  }

  .doc-tree-node-icon {
    flex-shrink: 0;
    color: var(--el-text-color-secondary);
  }

  .doc-tree-node-label {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .doc-content-panel {
    flex: 1;
    min-width: 0;

    :deep(.el-card) {
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    :deep(.el-card__body) {
      flex: 1;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
  }

  .doc-content-breadcrumb {
    padding: 12px 20px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    flex-shrink: 0;
  }

  .doc-content-scroll {
    flex: 1;
    overflow: hidden;
  }

  .doc-content-body {
    padding: 20px 32px 40px;
    max-width: 960px;
  }

  .doc-content-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    height: 300px;
    color: var(--el-text-color-secondary);
  }

  .doc-content-empty {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 400px;
  }
</style>

<style lang="scss">
  .doc-content-body .markdown-body .highlight pre,
  .doc-content-body .markdown-body pre {
    color: #e6edf3;
    background-color: #161b22;
  }
</style>
