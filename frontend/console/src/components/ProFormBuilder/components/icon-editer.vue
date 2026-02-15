<!-- 图标编辑器 -->
<template>
  <IconSelect
    :clearable="true"
    :popperHeight="388"
    filterable="popper"
    :placeholder="placeholder ?? '请选择图标'"
    :popperOptions="{ strategy: 'fixed' }"
    :modelValue="modelValue"
    @update:modelValue="updateModelValue"
  />
</template>

<script lang="ts" setup>
  import IconSelect from '@/components/IconSelect/index.vue';

  defineProps<{
    /** 图标 */
    modelValue?: string;
    /** 提示文本 */
    placeholder?: string;
  }>();

  const emit = defineEmits<{
    (e: 'update:modelValue', value?: string): void;
  }>();

  /** 更新图标 */
  const updateModelValue = (value?: string) => {
    emit('update:modelValue', value);
  };
</script>
