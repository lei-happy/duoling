<template>
  <ele-card header="基础用法">
    <div>基于 ElTreeV2 虚拟滚动树组件封装, 大量数据也毫无压力</div>
    <div style="max-width: 240px; margin-top: 12px">
      <ele-tree-select
        ref="treeSelectRef"
        clearable
        placeholder="请选择"
        v-model="selectedValue"
        :popper-width="240"
        :tree-props="treeProps"
        :disabled="disabled"
        :popper-options="{ strategy: 'fixed' }"
      />
    </div>
    <option-item label="整体禁用" :responsive="false" style="margin-top: 16px">
      <el-radio-group v-model="disabled">
        <el-radio :value="false" label="否" />
        <el-radio :value="true" label="是" />
      </el-radio-group>
    </option-item>
    <option-item label="父级点击" :responsive="false" style="margin-top: 0">
      <el-radio-group v-model="treeProps.expandOnClickNode">
        <el-radio :value="true" label="展开" />
        <el-radio :value="false" label="选中" />
      </el-radio-group>
    </option-item>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import type { EleTreeSelect } from 'ele-admin-plus';
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
  const selectedValue = ref<number>();

  /** 树属性 */
  const treeProps = reactive({
    height: 266,
    data: [] as DataItem[],
    expandOnClickNode: false
  });

  /** 禁用 */
  const disabled = ref(false);

  onMounted(() => {
    setTimeout(() => {
      let count = 0;
      const data = Array.from({ length: 20 }).map((_, i) => {
        count++;
        return {
          id: count,
          label: `${String(count).padStart(5, '0')}-node-${i + 1}`,
          disabled: false,
          children: Array.from({ length: 20 }).map((_, j) => {
            count++;
            return {
              id: count,
              label: `${String(count).padStart(5, '0')}-node-${i + 1}-${j + 1}`,
              disabled: false,
              children: Array.from({ length: 30 }).map((_, k) => {
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
      data[0].children[0].children[2].disabled = true;
      data[0].children[2].disabled = true;
      data[0].children[2].children.forEach((d) => {
        d.disabled = true;
      });
      treeProps.data = data;
    }, 100);
  });
</script>
