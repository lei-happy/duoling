<!-- 角色权限分配弹窗：左模块列表 + 右权限树 -->
<template>
  <ele-modal
    :width="1080"
    title="权限管理"
    position="center"
    :body-style="{
      padding: '0 0 12px',
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

    <div class="role-auth-body">
      <aside class="role-auth-modules">
        <button
          v-for="row in visibleModuleRows"
          :key="row.mod.menuId"
          type="button"
          class="role-auth-module-item"
          :class="{ 'is-active': row.mod.menuId === activeModuleId }"
          @click="selectModule(row.mod.menuId!)"
        >
          <el-checkbox
            :model-value="row.state.checked"
            :indeterminate="row.state.indeterminate"
            @click.stop
            @change="onModuleCheckChange(row.mod, $event)"
          />
          <span class="role-auth-module-title">{{ row.mod.title }}</span>
          <span
            class="role-auth-module-count"
            :class="{ 'is-partial': row.state.checkedCount > 0 }"
          >
            {{ row.state.checkedCount }}/{{ row.state.total }}
          </span>
        </button>
        <div v-if="!visibleModuleRows.length" class="role-auth-modules-empty">
          没有匹配的模块
        </div>
      </aside>

      <div class="role-auth-main">
        <div v-if="activeModule" class="role-auth-main-header">
          <span class="role-auth-main-title">{{ activeModule.title }}</span>
          <div class="role-auth-main-actions">
            <el-button text type="primary" @click="selectModuleAll"
              >本模块全选</el-button
            >
            <el-button text type="primary" @click="clearModuleAll"
              >本模块清空</el-button
            >
          </div>
        </div>
        <div class="role-auth-tree-wrap">
          <el-tree
            v-if="activeModule"
            :key="treeKey"
            ref="treeRef"
            show-checkbox
            :data="activeTreeData"
            node-key="menuId"
            :default-expand-all="false"
            :default-expanded-keys="defaultExpandedKeys"
            :props="treeProps"
            :filter-node-method="filterAuthNode"
            :style="{ '--ele-tree-item-height': '28px' }"
            @check="onTreeCheck"
          >
            <template #default="{ data: nodeData }">
              <span class="role-auth-node-label">{{ nodeData.title }}</span>
            </template>
          </el-tree>
          <div v-else class="role-auth-tree-empty">请从左侧选择模块</div>
        </div>
      </div>
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
  import { ref, computed, watch, nextTick, unref } from 'vue';
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
    collectSaveMenuIds,
    countModuleSelection,
    expandCheckedKeysWithCascade,
    filterAuthNode,
    getRoleAuthTreeNodeClass,
    menuOrDescendantMatches
  } from './role-auth-utils';

  const props = defineProps<{
    /** 当前角色数据 */
    data?: Role | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const treeRef = ref<InstanceType<typeof ElTree> | null>(null);

  const authData = ref<Menu[]>([]);

  /** 全局完全勾选的菜单 id（不含半选祖先） */
  const checkedKeys = ref<number[]>([]);

  const loading = ref(false);

  const filterText = ref('');

  const treeKey = ref(0);

  const activeModuleId = ref<number | null>(null);

  const defaultExpandedKeys = ref<number[]>([]);

  const treeProps = {
    label: 'title',
    class: getRoleAuthTreeNodeClass
  };

  const checkedSet = computed(() => new Set(checkedKeys.value));

  const visibleModules = computed(() => {
    const kw = filterText.value;
    if (!kw?.trim()) {
      return authData.value;
    }
    return authData.value.filter((m) => menuOrDescendantMatches(m, kw));
  });

  const activeModule = computed(
    () =>
      authData.value.find((m) => m.menuId === activeModuleId.value) ?? null
  );

  /** 右侧展示二级及以下，避免与左侧模块名重复占位 */
  const activeTreeData = computed(() => {
    const mod = activeModule.value;
    if (!mod) {
      return [];
    }
    return mod.children?.length ? mod.children : [mod];
  });

  type ModuleState = {
    checked: boolean;
    indeterminate: boolean;
    checkedCount: number;
    total: number;
  };

  const emptyModuleState: ModuleState = {
    checked: false,
    indeterminate: false,
    checkedCount: 0,
    total: 0
  };

  const moduleStates = computed(() => {
    const map = new Map<number, ModuleState>();
    for (const mod of authData.value) {
      if (mod.menuId == null) {
        continue;
      }
      const { checked, total } = countModuleSelection(mod, checkedSet.value);
      map.set(mod.menuId, {
        checked: total > 0 && checked === total,
        indeterminate: checked > 0 && checked < total,
        checkedCount: checked,
        total
      });
    }
    return map;
  });

  const visibleModuleRows = computed(() =>
    visibleModules.value.map((mod) => ({
      mod,
      state: (mod.menuId != null
        ? moduleStates.value.get(mod.menuId)
        : undefined) ?? emptyModuleState
    }))
  );

  const onModuleCheckChange = (mod: Menu, val: unknown) => {
    toggleModule(mod, Boolean(val));
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

  const syncCheckedFromTree = () => {
    const mod = activeModule.value;
    if (!mod?.menuId || !treeRef.value) {
      return;
    }
    const subtreeIds = new Set(collectAllMenuIds([mod]));
    let currentChecked =
      (treeRef.value.getCheckedKeys?.(false) as number[]) ?? [];
    // 右侧不展示一级节点时：子孙全选则补上一级 id
    if (mod.children?.length) {
      const descendantIds = collectAllMenuIds(mod.children);
      const allDescChecked =
        descendantIds.length > 0 &&
        descendantIds.every((id) => currentChecked.includes(id));
      if (allDescChecked) {
        currentChecked = [...currentChecked, mod.menuId];
      }
    }
    checkedKeys.value = [
      ...checkedKeys.value.filter((id) => !subtreeIds.has(id)),
      ...currentChecked
    ];
  };

  const applyCheckedToTree = () => {
    nextTick(() => {
      if (!activeModule.value || !treeRef.value) {
        return;
      }
      const treeIds = new Set(collectAllMenuIds(activeTreeData.value));
      const keys = checkedKeys.value.filter((id) => treeIds.has(id));
      treeRef.value.setCheckedKeys(keys, false);
      treeRef.value.filter(filterText.value);
    });
  };

  const remountActiveTree = () => {
    defaultExpandedKeys.value = collectDefaultExpandedKeys(activeTreeData.value);
    treeKey.value++;
    applyCheckedToTree();
  };

  const selectModule = (menuId: number) => {
    if (menuId === activeModuleId.value) {
      return;
    }
    syncCheckedFromTree();
    activeModuleId.value = menuId;
    remountActiveTree();
  };

  const onTreeCheck = () => {
    syncCheckedFromTree();
  };

  const toggleModule = (mod: Menu, checked: boolean) => {
    const ids = collectAllMenuIds([mod]);
    const idSet = new Set(ids);
    if (checked) {
      const merged = new Set(checkedKeys.value);
      ids.forEach((id) => merged.add(id));
      checkedKeys.value = [...merged];
    } else {
      checkedKeys.value = checkedKeys.value.filter((id) => !idSet.has(id));
    }
    if (mod.menuId === activeModuleId.value) {
      applyCheckedToTree();
    }
  };

  const selectModuleAll = () => {
    if (!activeModule.value) {
      return;
    }
    toggleModule(activeModule.value, true);
  };

  const clearModuleAll = () => {
    if (!activeModule.value) {
      return;
    }
    toggleModule(activeModule.value, false);
  };

  const expandAll = () => {
    nextTick(() => {
      if (!activeTreeData.value.length) {
        return;
      }
      const keys = collectAllExpandableKeys(activeTreeData.value);
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
    checkedKeys.value = collectAllMenuIds(authData.value);
    applyCheckedToTree();
  };

  const clearAll = () => {
    checkedKeys.value = [];
    applyCheckedToTree();
  };

  watch(filterText, (val) => {
    const visible = visibleModules.value;
    if (
      visible.length &&
      !visible.some((m) => m.menuId === activeModuleId.value)
    ) {
      syncCheckedFromTree();
      activeModuleId.value = visible[0].menuId ?? null;
      remountActiveTree();
      return;
    }
    treeRef.value?.filter(val);
  });

  const query = () => {
    authData.value = [];
    checkedKeys.value = [];
    defaultExpandedKeys.value = [];
    filterText.value = '';
    activeModuleId.value = null;
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
        checkedKeys.value = expandCheckedKeysWithCascade(tree, flatChecked);
        activeModuleId.value = tree[0]?.menuId ?? null;
        remountActiveTree();
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
    syncCheckedFromTree();
    loading.value = true;
    const ids = collectSaveMenuIds(authData.value, new Set(checkedKeys.value));
    updateRoleMenus(props.data?.roleId, ids)
      .then((msg) => {
        loading.value = false;
        EleMessage.success({ message: msg, plain: true });
        emit('done');
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
    padding: 12px 20px 10px;
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

  .role-auth-body {
    flex: 1;
    min-height: 0;
    display: flex;
    align-items: stretch;
  }

  .role-auth-modules {
    width: 200px;
    flex-shrink: 0;
    overflow: auto;
    padding: 8px 0;
    border-right: 1px solid var(--el-border-color-lighter);
    background: var(--el-fill-color-blank);
  }

  .role-auth-module-item {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    margin: 0;
    padding: 8px 12px 8px 14px;
    border: none;
    border-left: 2px solid transparent;
    background: transparent;
    color: var(--el-text-color-regular);
    font: inherit;
    text-align: left;
    cursor: pointer;
    box-sizing: border-box;
    transition:
      background-color 0.15s ease,
      border-color 0.15s ease,
      color 0.15s ease;
  }

  .role-auth-module-item:hover {
    background: var(--el-fill-color-light);
  }

  .role-auth-module-item.is-active {
    border-left-color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
  }

  .role-auth-module-title {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 13px;
    line-height: 1.3;
  }

  .role-auth-module-count {
    flex-shrink: 0;
    font-size: 12px;
    color: var(--el-text-color-placeholder);
    font-variant-numeric: tabular-nums;
  }

  .role-auth-module-count.is-partial {
    color: var(--el-color-primary);
  }

  .role-auth-modules-empty,
  .role-auth-tree-empty {
    padding: 24px 16px;
    font-size: 13px;
    color: var(--el-text-color-secondary);
    text-align: center;
  }

  .role-auth-main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .role-auth-main-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 8px 16px 4px 18px;
    flex-shrink: 0;
  }

  .role-auth-main-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .role-auth-main-actions {
    display: flex;
    align-items: center;
    gap: 0 2px;
  }

  .role-auth-tree-wrap {
    flex: 1;
    min-height: 0;
    overflow: auto;
    padding: 4px 16px 8px 18px;
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

  /* 子级全部为按钮权限时，横向排列；左侧缩进体现层级 */
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

  .role-auth-tree-wrap
    :deep(
      .el-tree-node.is-role-auth-action-group
        > .el-tree-node__children
        > .el-tree-node
    ) {
    flex: 0 0 auto;
    padding-left: 0 !important;
  }

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
