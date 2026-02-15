<template>
  <ele-card header="可搜索">
    <option-item label="单选">
      <div style="max-width: 240px">
        <ele-tree-select
          clearable
          filterable
          placeholder="请选择"
          v-model="selectedValue"
          :popper-width="240"
          :tree-props="treeProps"
          :popper-options="{ strategy: 'fixed' }"
        />
      </div>
    </option-item>
    <option-item label="多选" style="margin-top: 18px">
      <div style="max-width: 240px">
        <ele-tree-select
          clearable
          multiple
          filterable
          placeholder="请选择"
          v-model="selectedValue2"
          :popper-width="240"
          :tree-props="treeProps2"
          :popper-options="{ strategy: 'fixed' }"
        />
      </div>
    </option-item>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { EleMessage, toTree } from 'ele-admin-plus';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';
  import { listMenus } from '@/api/system/menu';
  import type { Menu } from '@/api/system/menu/model';

  /** 选中值 */
  const selectedValue = ref<number>();

  /** 树属性 */
  const treeProps = reactive({
    height: 266,
    data: [] as Menu[],
    props: { value: 'menuId', label: 'title' },
    expandOnClickNode: false
  });

  /** 选中值 */
  const selectedValue2 = ref<number[]>([]);

  /** 树属性 */
  const treeProps2 = reactive({
    height: 266,
    data: [] as Menu[],
    props: { value: 'menuId', label: 'title' },
    expandOnClickNode: true
  });

  listMenus()
    .then((list) => {
      treeProps.data = toTree({
        data: list,
        idField: 'menuId',
        parentIdField: 'parentId'
      });
      treeProps2.data = toTree({
        data: list,
        idField: 'menuId',
        parentIdField: 'parentId'
      });
    })
    .catch((e) => {
      EleMessage.error({ message: e.message, plain: true });
    });
</script>
