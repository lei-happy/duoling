<template>
  <ele-card header="标签显示策略">
    <div style="max-width: 240px">
      <ele-tree-select
        ref="treeSelectRef"
        clearable
        multiple
        placeholder="请选择"
        v-model="selectedValue"
        :popper-width="240"
        :tree-props="treeProps"
        :showCheckedStrategy="showCheckedStrategy"
        :checkedValueStrategy="checkedValueStrategy"
        :popper-options="{ strategy: 'fixed' }"
      />
    </div>
    <option-item
      label="显示策略"
      :label-style="{ paddingTop: '6px' }"
      style="margin-top: 10px; align-items: flex-start"
    >
      <el-radio-group
        v-model="showCheckedStrategy"
        style="flex-direction: column; align-items: flex-start"
      >
        <el-radio
          value="parent"
          label="parent(当子节点全部选中时只显示父级)"
          style="margin: 0; display: flex; width: 100%"
        />
        <el-radio
          value="child"
          label="child(只显示选中的子节点)"
          style="margin: 0; display: flex; width: 100%"
        />
        <el-radio
          value="all"
          label="all(显示所有选中的节点)"
          style="margin: 0; display: flex; width: 100%"
        />
      </el-radio-group>
    </option-item>
    <option-item label="值策略" :responsive="false" style="margin-top: 10px">
      <el-radio-group v-model="checkedValueStrategy">
        <el-radio :value="false" label="全部选中值" />
        <el-radio :value="true" label="同标签策略" />
      </el-radio-group>
    </option-item>
    <option-item label="选中值" style="margin-top: 10px">
      {{ JSON.stringify(selectedValue) }}
    </option-item>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import type { EleTreeSelect } from 'ele-admin-plus';
  import type { ShowCheckedStrategy } from 'ele-admin-plus/es/ele-tree-select/types';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';

  interface DataItem {
    id: number;
    label: string;
    disabled?: boolean;
    children?: DataItem[];
  }

  /** 树选择组件 */
  const treeSelectRef = ref<InstanceType<typeof EleTreeSelect> | null>(null);

  /** 选中值 */
  const selectedValue = ref<number[]>([2, 3, 4]);

  /** 树属性 */
  const treeProps = reactive({
    height: 266,
    data: [] as DataItem[]
  });

  /** 标签显示策略 */
  const showCheckedStrategy = ref<ShowCheckedStrategy>('parent');

  /** 值策略 */
  const checkedValueStrategy = ref(false);

  onMounted(() => {
    setTimeout(() => {
      let count = 0;
      const data = Array.from({ length: 4 }).map((_, i) => {
        count++;
        return {
          id: count,
          label: `${String(count).padStart(5, '0')}-node-${i + 1}`,
          disabled: false,
          children: Array.from({ length: 3 }).map((_, j) => {
            count++;
            return {
              id: count,
              label: `${String(count).padStart(5, '0')}-node-${i + 1}-${j + 1}`,
              disabled: false,
              children: Array.from({ length: 2 }).map((_, k) => {
                count++;
                const idStr = String(count).padStart(5, '0');
                return {
                  id: count,
                  label: `${idStr}-node-${i + 1}-${j + 1}-${k + 1}`,
                  disabled: false
                };
              })
            };
          })
        };
      });
      treeProps.data = data;
    }, 100);
  });
</script>
