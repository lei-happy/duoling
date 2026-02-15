<template>
  <ele-card header="修改菜单徽章">
    <el-form label-width="80px" style="max-width: 360px" @submit.prevent="">
      <el-form-item label="菜单">
        <el-tree-select
          clearable
          :data="treeData"
          check-strictly
          default-expand-all
          placeholder="请选择菜单"
          v-model="path"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        >
          <template #default="{ data }">
            <el-icon
              v-if="data.meta?.icon"
              style="margin-right: 4px; transform: translateY(-1px)"
            >
              <component :is="data.meta?.icon" />
            </el-icon>
            <span>{{ data.label }}</span>
          </template>
          <template v-if="selectedIcon" #prefix>
            <el-icon
              color="var(--el-text-color-regular)"
              style="margin-right: 6px"
            >
              <component :is="selectedIcon" />
            </el-icon>
          </template>
        </el-tree-select>
      </el-form-item>
      <el-form-item label="徽章值">
        <el-input clearable v-model="badge" placeholder="请输入徽章值" />
      </el-form-item>
      <el-form-item label="徽章类型">
        <el-select
          clearable
          v-model="type"
          placeholder="请选择徽章类型"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        >
          <el-option label="primary" value="primary" />
          <el-option label="success" value="success" />
          <el-option label="warning" value="warning" />
          <el-option label="danger" value="danger" />
          <el-option label="info" value="info" />
        </el-select>
      </el-form-item>
      <el-form-item style="margin: 0">
        <el-button type="primary" @click="setBadge">更新</el-button>
      </el-form-item>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, computed } from 'vue';
  import { storeToRefs } from 'pinia';
  import type { BadgeProps } from 'element-plus';
  import { EleMessage, mapTree, findTree } from 'ele-admin-plus';
  import { useUserStore } from '@/store/modules/user';

  /** 菜单树 */
  const userStore = useUserStore();
  const { menus } = storeToRefs(userStore);

  /** 菜单树下拉数据 */
  const treeData = computed(() => {
    return mapTree(menus.value, (m) => {
      return {
        ...m,
        value: m.path,
        label: m.meta?.title
      };
    });
  });

  /** 选中菜单 */
  const path = ref<string>();

  /** 徽章值 */
  const badge = ref<string>();

  /** 徽章类型 */
  const type = ref<BadgeProps['type']>();

  /** 选中菜单的图标 */
  const selectedIcon = computed(() => {
    if (!path.value) {
      return;
    }
    return findTree(treeData.value, (d) => d.path == path.value)?.meta?.icon;
  });

  /** 修改菜单徽章数据 */
  const setBadge = () => {
    if (!path.value) {
      EleMessage.error({ message: '请选择菜单', plain: true });
      return;
    }
    userStore.setMenuBadge(
      path.value,
      !badge.value || isNaN(Number(badge.value))
        ? badge.value
        : Number(badge.value),
      type.value
    );
  };
</script>
