<!-- 上级菜单选择下拉框（客户端菜单专用） -->
<template>
  <el-tree-select
    clearable
    filterable
    :data="menuData"
    check-strictly
    default-expand-all
    node-key="menuId"
    :props="{ label: 'title' }"
    :placeholder="placeholder"
    :model-value="modelValue || void 0"
    class="ele-fluid"
    :popper-options="{ strategy: 'fixed' }"
    @update:modelValue="updateValue"
  >
    <template #default="{ data }">
      <menu-icon
        v-if="data.icon"
        :icon="data.icon"
        :component-style="{ marginRight: '4px', transform: 'translateY(-1px)' }"
        :img-style="{
          width: '20px',
          height: '20px',
          marginRight: '4px',
          transform: 'translateY(-1px)'
        }"
      />
      <span>{{ data.title }}</span>
    </template>
    <template v-if="selectedIcon" #prefix>
      <el-icon color="var(--el-text-color-regular)" style="margin-right: 6px">
        <component :is="selectedIcon" />
      </el-icon>
    </template>
  </el-tree-select>
</template>

<script lang="ts" setup>
  import { ref, computed } from 'vue';
  import { EleMessage, toTree, findTree } from 'ele-admin-plus';
  import MenuIcon from '@/components/IconSelect/components/menu-icon.vue';
  import { listClientMenus } from '@/api/system/client-menu';
  import type { ClientMenu } from '@/api/system/client-menu/model';

  const props = withDefaults(
    defineProps<{
      modelValue?: number | string;
      placeholder?: string;
    }>(),
    {
      placeholder: '请选择上级菜单'
    }
  );

  const emit = defineEmits<{
    (e: 'update:modelValue', value: number | string): void;
  }>();

  const menuData = ref<ClientMenu[]>([]);

  const updateValue = (value: number | string) => {
    emit('update:modelValue', value || 0);
  };

  const selectedIcon = computed(() => {
    if (!props.modelValue) {
      return;
    }
    return findTree(menuData.value, (d) => d.menuId == props.modelValue)?.icon;
  });

  listClientMenus()
    .then((list) => {
      menuData.value = toTree({
        data: list,
        idField: 'menuId',
        parentIdField: 'parentId'
      });
    })
    .catch((e) => {
      EleMessage.error({ message: e.message, plain: true });
    });
</script>
