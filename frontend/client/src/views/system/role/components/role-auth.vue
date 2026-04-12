<!-- 角色权限分配弹窗 -->
<template>
  <ele-modal
    :width="920"
    title="分配权限"
    position="center"
    :body-style="{
      padding: '0 18px 12px 20px',
      height: 'calc(100vh - 192px)',
      maxHeight: 'calc(100dvh - 192px)',
      minHeight: '100px',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column'
    }"
    :loading="loading"
    v-bind="modalProps"
  >
    <div class="role-auth-toolbar">
      <el-input
        v-model="filterText"
        clearable
        placeholder="搜索权限名称或标识"
        :prefix-icon="SearchIcon"
        class="role-auth-search"
      />
      <div class="role-auth-toolbar-actions">
        <el-button text type="primary" @click="expandAll">展开全部</el-button>
        <el-button text type="primary" @click="collapseAll">收起全部</el-button>
        <el-button text type="primary" @click="selectAll">全选</el-button>
        <el-button text type="primary" @click="clearAll">清空</el-button>
      </div>
    </div>
    <div class="role-auth-tree-wrap">
      <el-tree
        :key="treeKey"
        ref="treeRef"
        show-checkbox
        :data="authData"
        node-key="menuId"
        :default-expand-all="false"
        :default-expanded-keys="defaultExpandedKeys"
        :props="treeProps"
        :filter-node-method="filterAuthNode"
        :style="{ '--ele-tree-item-height': '28px' }"
      >
        <template #default="{ data: nodeData }">
          <span class="role-auth-node-label">{{ nodeData.title }}</span>
        </template>
      </el-tree>
    </div>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
          { preset: 'save', onClick: () => save() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, watch, nextTick, unref } from 'vue';
  import { Search as SearchIcon } from '@element-plus/icons-vue';
  import type { ElTree } from 'element-plus';
  import { EleMessage, toTree, useModal } from 'ele-admin-plus';
  import { listRoleMenus, updateRoleMenus } from '@/api/system/role';
  import type { Role } from '@/api/system/role/model';
  import type { Menu } from '@/api/system/menu/model';
  import {
    collectDefaultExpandedKeys,
    collectAllExpandableKeys,
    collectAllMenuIds,
    filterAuthNode,
    getRoleAuthTreeNodeClass
  } from './role-auth-utils';

  const props = defineProps<{
    /** 当前角色数据 */
    data?: Role | null;
  }>();

  const { modalProps, closeModal } = useModal();

  const treeRef = ref<InstanceType<typeof ElTree> | null>(null);

  const authData = ref<Menu[]>([]);

  const loading = ref(false);

  const filterText = ref('');

  const treeKey = ref(0);

  const defaultExpandedKeys = ref<number[]>([]);

  const treeProps = {
    label: 'title',
    class: getRoleAuthTreeNodeClass
  };

  /** Element Plus 的 ElTree 未在实例上暴露 setExpandedKeys，需用 store.setDefaultExpandedKeys */
  const getTreeStore = () => {
    const tree = treeRef.value as
      | (InstanceType<typeof ElTree> & {
          store?: unknown;
        })
      | null;
    if (!tree?.store) {
      return null;
    }
    return unref(tree.store as { root?: unknown }) as {
      root: {
        childNodes?: Array<{ collapse?: () => void; childNodes?: unknown[] }>;
      };
      setDefaultExpandedKeys: (keys: number[]) => void;
    } | null;
  };

  const expandAll = () => {
    nextTick(() => {
      const keys = collectAllExpandableKeys(authData.value);
      getTreeStore()?.setDefaultExpandedKeys(keys);
    });
  };

  const collapseAll = () => {
    nextTick(() => {
      const store = getTreeStore();
      if (!store?.root) {
        return;
      }
      const walk = (node: {
        childNodes?: Array<{ collapse?: () => void; childNodes?: unknown[] }>;
      }) => {
        node.childNodes?.forEach((child) => {
          walk(child);
          child.collapse?.();
        });
      };
      walk(store.root);
    });
  };

  const selectAll = () => {
    const ids = collectAllMenuIds(authData.value);
    treeRef.value?.setCheckedKeys(ids, false);
  };

  const clearAll = () => {
    treeRef.value?.setCheckedKeys([]);
  };

  watch(filterText, (val) => {
    treeRef.value?.filter(val);
  });

  const query = () => {
    authData.value = [];
    defaultExpandedKeys.value = [];
    filterText.value = '';
    if (!props.data) {
      return;
    }
    loading.value = true;
    listRoleMenus(props.data.roleId)
      .then((list) => {
        loading.value = false;
        const flatChecked =
          (list || [])
            .filter((m) => m.checked && m.menuId != null)
            .map((m) => m.menuId as number) ?? [];
        const tree = toTree({
          data: list as Menu[],
          idField: 'menuId',
          parentIdField: 'parentId'
        });
        authData.value = tree;
        defaultExpandedKeys.value = collectDefaultExpandedKeys(authData.value);
        treeKey.value++;
        nextTick(() => {
          treeRef.value?.setCheckedKeys(flatChecked, false);
          treeRef.value?.filter(filterText.value);
        });
      })
      .catch((e) => {
        loading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const handleCancel = () => {
    closeModal();
  };

  const save = () => {
    loading.value = true;
    const ids =
      (treeRef.value?.getCheckedKeys?.() ?? []).concat(
        treeRef.value?.getHalfCheckedKeys?.() ?? []
      ) ?? [];
    updateRoleMenus(props.data?.roleId, ids as unknown as number[])
      .then((msg) => {
        loading.value = false;
        EleMessage.success({ message: msg, plain: true });
        handleCancel();
      })
      .catch((e) => {
        loading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  query();
</script>

<style scoped>
  .role-auth-toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px 12px;
    padding: 12px 0 10px;
    flex-shrink: 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  .role-auth-search {
    flex: 1;
    min-width: 200px;
    max-width: 360px;
  }

  .role-auth-toolbar-actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0 4px;
  }

  .role-auth-tree-wrap {
    flex: 1;
    min-height: 0;
    overflow: auto;
    padding-top: 8px;
  }

  .role-auth-node-label {
    display: inline-block;
    max-width: 100%;
  }

  /* 缩小复选框与右侧文案（自定义 slot）之间的间距 */
  .role-auth-tree-wrap :deep(.el-tree-node__content > .el-checkbox) {
    margin-right: 4px;
  }

  .role-auth-tree-wrap :deep(.el-tree-node__content) {
    column-gap: 6px;
  }

  /* 子级全部为按钮权限时，横向排列；左侧缩进体现层级（略大于一级树缩进） */
  .role-auth-tree-wrap
    :deep(.el-tree-node.is-role-auth-action-group > .el-tree-node__children) {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px 6px;
    padding-top: 2px;
    padding-left: calc(var(--el-tree-node-indent, 18px) * 2 + 28px);
    box-sizing: border-box;
    margin-left: 0 !important;
  }

  /* 横向每项不拉伸，避免悬停背景铺得过宽 */
  .role-auth-tree-wrap
    :deep(
      .el-tree-node.is-role-auth-action-group
        > .el-tree-node__children
        > .el-tree-node
    ) {
    flex: 0 0 auto;
    padding-left: 0 !important;
  }

  /* 悬停高亮仅包裹「展开占位 + 复选框 + 文案」，左缘与选项对齐 */
  .role-auth-tree-wrap
    :deep(
      .el-tree-node.is-role-auth-action-group
        > .el-tree-node__children
        > .el-tree-node
        > .el-tree-node__content
    ) {
    flex: 0 0 auto !important;
    width: fit-content;
    max-width: 100%;
    padding-left: 0 !important;
    padding-right: 6px !important;
    box-sizing: border-box;
  }

  /* 叶子箭头占位仍占宽度，收起后高亮左侧会留白 */
  .role-auth-tree-wrap
    :deep(
      .el-tree-node.is-role-auth-action-group
        > .el-tree-node__children
        > .el-tree-node
        .el-tree-node__expand-icon
    ) {
    width: 0 !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    visibility: hidden;
    overflow: hidden;
  }

  /* 横向按钮行内：复选框与文字更紧凑 */
  .role-auth-tree-wrap
    :deep(
      .el-tree-node.is-role-auth-action-group
        .el-tree-node__content
        > .el-checkbox
    ) {
    margin-right: 2px;
  }

  .role-auth-tree-wrap
    :deep(.el-tree-node.is-role-auth-action-group .el-checkbox__label) {
    padding-left: 4px;
  }
</style>
