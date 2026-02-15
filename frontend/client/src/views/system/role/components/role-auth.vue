<!-- 角色权限分配弹窗 -->
<template>
  <ele-modal
    :width="460"
    title="分配权限"
    position="center"
    :body-style="{
      padding: '12px 18px 12px 20px',
      height: 'calc(100vh - 192px)',
      maxHeight: 'calc(100dvh - 192px)',
      minHeight: '100px',
      overflow: 'auto'
    }"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-tree
      ref="treeRef"
      show-checkbox
      :data="authData"
      node-key="menuId"
      :default-expand-all="true"
      :props="{ label: 'title' }"
      :default-checked-keys="checkedKeys"
      :style="{ '--ele-tree-item-height': '28px' }"
    >
      <template #default="scope">
        <div>
          <el-icon
            v-if="scope.data.icon"
            :size="16"
            style="margin-right: 6px; vertical-align: -5px"
          >
            <component :is="scope.data.icon" />
          </el-icon>
          <span style="vertical-align: -2px">{{ scope.data.title }}</span>
        </div>
      </template>
    </el-tree>
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
  import { ref, nextTick } from 'vue';
  import type { ElTree } from 'element-plus';
  import { EleMessage, toTree, eachTree, useModal } from 'ele-admin-plus';
  import { listRoleMenus, updateRoleMenus } from '@/api/system/role';
  import type { Role } from '@/api/system/role/model';
  import type { Menu } from '@/api/system/menu/model';

  const props = defineProps<{
    /** 当前角色数据 */
    data?: Role | null;
  }>();

  const { modalProps, closeModal } = useModal();

  /** 树组件实例 */
  const treeRef = ref<InstanceType<typeof ElTree> | null>(null);

  /** 权限数据 */
  const authData = ref<Menu[]>([]);

  /** 提交状态 */
  const loading = ref(false);

  /** 角色权限选中的keys */
  const checkedKeys = ref<number[]>([]);

  /** 查询权限数据 */
  const query = () => {
    authData.value = [];
    checkedKeys.value = [];
    if (!props.data) {
      return;
    }
    loading.value = true;
    listRoleMenus(props.data.roleId)
      .then((data) => {
        loading.value = false;
        // 转成树形结构的数据
        authData.value = toTree({
          data: data,
          idField: 'menuId',
          parentIdField: 'parentId'
        });
        // 回显选中的数据
        nextTick(() => {
          const cks: number[] = [];
          eachTree(authData.value, (d) => {
            if (d.menuId && d.checked && !d.children?.length) {
              cks.push(d.menuId);
            }
          });
          checkedKeys.value = cks;
        });
      })
      .catch((e) => {
        loading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  /** 关闭弹窗 */
  const handleCancel = () => {
    closeModal();
  };

  /** 保存权限分配 */
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

  /** 查询数据 */
  query();
</script>
