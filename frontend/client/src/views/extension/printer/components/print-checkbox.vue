<!-- 复选框组 -->
<template>
  <div class="print-checkbox-group">
    <div
      v-for="item in items"
      :key="item.value"
      :class="[
        'print-checkbox',
        { 'is-checked': model && model.includes(item.value) }
      ]"
      @click="handleItemClick(item)"
    >
      <div class="print-checkbox-icon"></div>
      <div>{{ item.label }}</div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  interface Item {
    label: string;
    value: string | number;
  }

  defineProps<{
    /** 选项 */
    items: Item[];
  }>();

  const model = defineModel<(string | number)[]>({ type: Array });

  /** item点击事件 */
  const handleItemClick = (item: Item) => {
    // 取消选中
    if (model.value && model.value.includes(item.value)) {
      model.value.splice(model.value.indexOf(item.value), 1);
      return;
    }
    // 选中
    if (model.value) {
      model.value.push(item.value);
      return;
    }
    model.value = [item.value];
  };
</script>

<style lang="scss" scoped>
  .print-checkbox-group {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }

  .print-checkbox {
    display: flex;
    align-items: center;
    color: #000;
    font-size: 15px;
    margin-right: 24px;
    cursor: pointer;

    .print-checkbox-icon {
      width: 15px;
      height: 15px;
      flex-shrink: 0;
      border: 1px solid #000;
      margin-right: 8px;
    }

    &.is-checked .print-checkbox-icon::before {
      content: '';
      width: 11px;
      height: 5px;
      display: inline-block;
      border: 2px solid transparent;
      border-left-color: #000;
      border-bottom-color: #000;
      transform: rotate(-45deg) translate(6px, -5px);
    }
  }
</style>
