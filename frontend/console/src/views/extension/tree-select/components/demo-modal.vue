<template>
  <ele-card header="弹窗模式、抽屉模式">
    <div style="margin: 0 0 8px 0">弹窗模式:</div>
    <div style="max-width: 240px">
      <ele-tree-select
        clearable
        multiple
        placeholder="请选择"
        v-model="selectedValue"
        :popper-width="460"
        :tree-props="treeProps"
        :max-tag-count="1"
        popper-type="modal"
        popper-title="请选择"
      />
    </div>
    <div style="margin: 32px 0 8px 0">抽屉模式:</div>
    <div style="max-width: 240px">
      <ele-tree-select
        clearable
        multiple
        placeholder="请选择"
        v-model="selectedValue2"
        :popper-width="460"
        :tree-props="treeProps"
        :max-tag-count="1"
        popper-type="drawer"
        popper-title="请选择"
      />
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import type { EleTreeSelect } from 'ele-admin-plus';

  interface DataItem {
    id: number;
    label: string;
    disabled?: boolean;
    children?: DataItem[];
  }

  /** 选中值 */
  const selectedValue = ref<number[]>([]);

  /** 树属性 */
  const treeProps = reactive({
    height: 266,
    data: [] as DataItem[],
    checkStrictly: false,
    expandOnClickNode: true
  });

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

  /** 选中值 */
  const selectedValue2 = ref<number[]>([]);
</script>
